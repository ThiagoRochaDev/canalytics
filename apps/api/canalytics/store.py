"""SQLite persistence with workspace-scoped queries and encrypted secrets."""

import contextlib
import hashlib
import json
import os
import secrets
import sqlite3
import time
from pathlib import Path

from cryptography.fernet import Fernet

SCHEMA = """
CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL);
INSERT INTO schema_version SELECT 1 WHERE NOT EXISTS(SELECT 1 FROM schema_version);
CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,email TEXT UNIQUE NOT NULL,name TEXT NOT NULL,password TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS workspaces(id TEXT PRIMARY KEY,name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS members(user_id TEXT NOT NULL REFERENCES users(id),workspace_id TEXT NOT NULL REFERENCES workspaces(id),role TEXT NOT NULL,PRIMARY KEY(user_id,workspace_id));
CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,user_id TEXT NOT NULL REFERENCES users(id),expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS apps(id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL REFERENCES workspaces(id),provider TEXT NOT NULL,secrets TEXT NOT NULL,created REAL NOT NULL);
CREATE INDEX IF NOT EXISTS apps_scope ON apps(workspace_id,provider,created);
CREATE TABLE IF NOT EXISTS connections(id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL REFERENCES workspaces(id),app_id TEXT NOT NULL REFERENCES apps(id),provider TEXT NOT NULL,label TEXT NOT NULL,secrets TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'active',last_sync TEXT,error TEXT,next_sync REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS oauth_states(state_hash TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,user_id TEXT NOT NULL,app_id TEXT NOT NULL,provider TEXT NOT NULL,verifier TEXT NOT NULL,session_hash TEXT NOT NULL,expires REAL NOT NULL);
CREATE TABLE IF NOT EXISTS resources(id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,connection_id TEXT NOT NULL REFERENCES connections(id) ON DELETE CASCADE,provider TEXT NOT NULL,external_id TEXT NOT NULL,payload TEXT NOT NULL,UNIQUE(workspace_id,provider,external_id));
CREATE TABLE IF NOT EXISTS daily(resource_id TEXT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,day TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(resource_id,day));
CREATE TABLE IF NOT EXISTS snapshots(resource_id TEXT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,observed_at TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(resource_id,observed_at));
CREATE TABLE IF NOT EXISTS contents(resource_id TEXT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,external_id TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(resource_id,external_id));
CREATE TABLE IF NOT EXISTS breakdowns(resource_id TEXT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,kind TEXT NOT NULL,payload TEXT NOT NULL,PRIMARY KEY(resource_id,kind));
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,connection_id TEXT NOT NULL REFERENCES connections(id) ON DELETE CASCADE,workspace_id TEXT NOT NULL,status TEXT NOT NULL,created REAL NOT NULL,started REAL,finished REAL,error TEXT,attempts INTEGER NOT NULL DEFAULT 0);
CREATE UNIQUE INDEX IF NOT EXISTS jobs_active ON jobs(connection_id) WHERE status IN ('pending','running');
CREATE TABLE IF NOT EXISTS notes(id TEXT PRIMARY KEY,workspace_id TEXT NOT NULL,resource_id TEXT NOT NULL REFERENCES resources(id) ON DELETE CASCADE,body TEXT NOT NULL,created TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS resources_scope ON resources(workspace_id);
CREATE INDEX IF NOT EXISTS jobs_scope ON jobs(workspace_id,created);
"""


def uid():
    return secrets.token_urlsafe(18)


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


class Store:
    def __init__(self, directory):
        self.path = Path(directory)
        self.path.mkdir(parents=True, exist_ok=True)
        key_path = self.path / "secrets.key"
        try:
            fd = os.open(key_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, "wb") as f:
                f.write(Fernet.generate_key())
        self.cipher = Fernet(key_path.read_bytes())
        self.db_path = self.path / "canalytics.sqlite"
        with self.db() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript(SCHEMA)

    @contextlib.contextmanager
    def db(self):
        db = sqlite3.connect(self.db_path, timeout=20)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def all(self, sql, args=()):
        with self.db() as db:
            return [dict(r) for r in db.execute(sql, args).fetchall()]

    def one(self, sql, args=()):
        result = self.all(sql, args)
        return result[0] if result else None

    def execute(self, sql, args=()):
        with self.db() as db:
            return db.execute(sql, args).rowcount

    def seal(self, data):
        return self.cipher.encrypt(json.dumps(data).encode()).decode()

    def unseal(self, data):
        return json.loads(self.cipher.decrypt(data.encode()))

    def app(self, workspace, provider):
        return self.one(
            "SELECT * FROM apps WHERE workspace_id=? AND provider=? ORDER BY created DESC LIMIT 1",
            (workspace, provider),
        )

    def enqueue(self, workspace, connection_id):
        with self.db() as db:
            db.execute("BEGIN IMMEDIATE")
            existing = db.execute(
                "SELECT id FROM jobs WHERE workspace_id=? AND connection_id=? AND status IN ('pending','running')",
                (workspace, connection_id),
            ).fetchone()
            if existing:
                return existing["id"]
            job = uid()
            db.execute(
                "INSERT INTO jobs(id,connection_id,workspace_id,status,created) VALUES(?,?,?,'pending',?)",
                (job, connection_id, workspace, time.time()),
            )
            return job

    def save_sync(self, connection, result, now):
        with self.db() as db:
            # A removed connection must never be recreated by an in-flight sync.
            if not db.execute(
                "SELECT 1 FROM connections WHERE id=? AND workspace_id=?",
                (connection["id"], connection["workspace_id"]),
            ).fetchone():
                return
            known = {
                r["external_id"]
                for r in db.execute(
                    "SELECT external_id FROM resources WHERE connection_id=?",
                    (connection["id"],),
                ).fetchall()
            }
            incoming = {r["external_id"] for r in result["resources"]}
            if known and known != incoming:
                raise ValueError(
                    "Reautorize o mesmo canal. Para outro canal, crie uma nova conexão."
                )
            for resource in result["resources"]:
                old = db.execute(
                    "SELECT id,connection_id FROM resources WHERE workspace_id=? AND provider=? AND external_id=?",
                    (
                        connection["workspace_id"],
                        connection["provider"],
                        resource["external_id"],
                    ),
                ).fetchone()
                if old and old["connection_id"] != connection["id"]:
                    raise ValueError(
                        "Este recurso já está conectado nesta área. Remova a conexão anterior para reconectar."
                    )
                rid = old["id"] if old else uid()
                resource = {
                    **resource,
                    "id": rid,
                    "connection_id": connection["id"],
                    "provider": connection["provider"],
                    "last_sync": now,
                }
                db.execute(
                    "INSERT INTO resources VALUES(?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload",
                    (
                        rid,
                        connection["workspace_id"],
                        connection["id"],
                        connection["provider"],
                        resource["external_id"],
                        json.dumps(resource),
                    ),
                )
                interval = result.get("interval")
                if interval:
                    db.execute(
                        "DELETE FROM daily WHERE resource_id=? AND day BETWEEN ? AND ?",
                        (rid, *interval),
                    )
                for row in result.get("daily", []):
                    db.execute(
                        "INSERT OR REPLACE INTO daily VALUES(?,?,?)",
                        (rid, row["day"], json.dumps(row)),
                    )
                if result.get("snapshot") is not None:
                    db.execute(
                        "INSERT OR REPLACE INTO snapshots VALUES(?,?,?)",
                        (rid, now, json.dumps(result["snapshot"])),
                    )
                # Current catalog cache replaces only when the provider query succeeded.
                if "contents" in result:
                    db.execute("DELETE FROM contents WHERE resource_id=?", (rid,))
                    for content in result["contents"]:
                        db.execute(
                            "INSERT INTO contents VALUES(?,?,?)",
                            (rid, content["id"], json.dumps(content)),
                        )
                for kind, rows in result.get("breakdowns", {}).items():
                    db.execute(
                        "INSERT OR REPLACE INTO breakdowns VALUES(?,?,?)",
                        (rid, kind, json.dumps(rows)),
                    )
            db.execute(
                "UPDATE connections SET last_sync=?,status='active',error=?,next_sync=? WHERE id=?",
                (
                    now,
                    "; ".join(result.get("warnings", [])) or None,
                    time.time() + result.get("sync_seconds", 86400),
                    connection["id"],
                ),
            )

    def workspace_data(self, workspace):
        resource_rows = self.all(
            "SELECT r.*,c.error AS connection_error,c.status AS connection_status FROM resources r JOIN connections c ON c.id=r.connection_id WHERE r.workspace_id=?",
            (workspace,),
        )
        resources = [
            {
                **json.loads(r["payload"]),
                "sync_error": r["connection_error"],
                "connection_status": r["connection_status"],
            }
            for r in resource_rows
        ]

        def scoped(table, field):
            return [
                {**json.loads(r["payload"]), "resource_id": r["resource_id"]}
                for r in self.all(
                    "SELECT t.resource_id,t.payload FROM "
                    + table
                    + " t JOIN resources r ON r.id=t.resource_id WHERE r.workspace_id=? "
                    + field,
                    (workspace,),
                )
            ]

        snapshots = [
            {
                **json.loads(r["payload"]),
                "resource_id": r["resource_id"],
                "observed_at": r["observed_at"],
            }
            for r in self.all(
                "SELECT t.* FROM snapshots t JOIN resources r ON r.id=t.resource_id WHERE r.workspace_id=? ORDER BY t.observed_at",
                (workspace,),
            )
        ]
        breakdowns = [
            {
                "resource_id": r["resource_id"],
                "kind": r["kind"],
                "rows": json.loads(r["payload"]),
            }
            for r in self.all(
                "SELECT t.* FROM breakdowns t JOIN resources r ON r.id=t.resource_id WHERE r.workspace_id=?",
                (workspace,),
            )
        ]
        return {
            "demo": False,
            "resources": resources,
            "daily": scoped("daily", "ORDER BY t.day"),
            "contents": scoped("contents", ""),
            "snapshots": snapshots,
            "breakdowns": breakdowns,
        }
