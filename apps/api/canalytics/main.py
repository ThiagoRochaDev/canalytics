import asyncio
import contextlib
import csv
import io
import json
import os
import secrets
import time
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .connectors import CATALOG, CONNECTORS
from .connectors.base import ProviderError, now_iso
from .demo import demo_data
from .oauth import authorization, exchange, fresh_credentials, verify_discord_guild
from .security import RateLimit, hash_password, verify_password
from .store import Store, digest, uid
from .worker import worker


class AccountInput(BaseModel):
    email: str = Field(min_length=3, max_length=200)
    password: str = Field(min_length=12, max_length=200)
    name: str = Field(default="Criador", min_length=1, max_length=80)
    workspace: str = Field(default="Meu estúdio", min_length=1, max_length=80)


class LoginInput(BaseModel):
    email: str = Field(max_length=200)
    password: str = Field(max_length=200)


class NameInput(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class AppInput(BaseModel):
    client_id: str = Field(min_length=1, max_length=500)
    client_secret: str = Field(min_length=1, max_length=1000)
    bot_token: str = Field(default="", max_length=1000)


class StartInput(BaseModel):
    monetary: bool = False
    connection_id: str | None = Field(default=None, max_length=100)


class NoteInput(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


def create_app(
    data_dir=None,
    public_url=None,
    worker_enabled=True,
    serve_frontend=True,
    session_cookie="canalytics_session",
):
    store = Store(data_dir or os.environ.get("CANALYTICS_DATA_DIR", "data"))
    origin = (
        public_url or os.environ.get("CANALYTICS_PUBLIC_URL", "http://localhost:8093")
    ).rstrip("/")
    if urlparse(origin).scheme not in ("http", "https") or urlparse(origin).path:
        raise ValueError(
            "CANALYTICS_PUBLIC_URL must be an http(s) origin without a path."
        )
    allowed = {origin}
    if urlparse(origin).hostname in ("localhost", "127.0.0.1"):
        allowed.update(
            {
                "http://localhost:5178",
                "http://127.0.0.1:5178",
                "http://localhost:8093",
                "http://127.0.0.1:8093",
            }
        )
    limiter = RateLimit()

    @asynccontextmanager
    async def lifespan(app):
        task = asyncio.create_task(worker(store)) if worker_enabled else None
        yield
        if task:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task

    app = FastAPI(
        title="Canalytics",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.store = store
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=list({urlparse(origin).hostname, "localhost", "127.0.0.1"}),
    )

    @app.middleware("http")
    async def protect(request, call_next):
        if request.method in ("POST", "PUT", "DELETE", "PATCH"):
            if request.headers.get("X-Canalytics-Request") != "1" or (
                request.headers.get("origin")
                and request.headers["origin"] not in allowed
            ):
                return JSONResponse(
                    {"detail": "Origem da solicitação não autorizada."}, 403
                )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; font-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        )
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store"
        return response

    def identity(request):
        token = request.cookies.get(session_cookie, "")
        user = store.one(
            "SELECT u.id,u.email,u.name,s.token_hash FROM sessions s JOIN users u ON u.id=s.user_id WHERE token_hash=? AND expires>?",
            (digest(token), time.time()),
        )
        if not user:
            raise HTTPException(401, "Entre na sua conta para continuar.")
        return user

    def scope(request):
        user = identity(request)
        workspace = request.headers.get("X-Workspace-ID", "")
        member = store.one(
            "SELECT * FROM members WHERE user_id=? AND workspace_id=?",
            (user["id"], workspace),
        )
        if not member:
            raise HTTPException(403, "Área de trabalho não autorizada.")
        return user, workspace, member["role"]

    def owner(request):
        user, workspace, role = scope(request)
        if role != "owner":
            raise HTTPException(
                403, "Somente o responsável pode alterar esta configuração."
            )
        return user, workspace

    def resource(request, rid):
        _, workspace, _ = scope(request)
        row = store.one(
            "SELECT * FROM resources WHERE id=? AND workspace_id=?", (rid, workspace)
        )
        if not row:
            raise HTTPException(404, "Canal não encontrado.")
        return row

    def session_response(user_id):
        token = secrets.token_urlsafe(40)
        store.execute(
            "INSERT INTO sessions VALUES(?,?,?)",
            (digest(token), user_id, time.time() + 7 * 86400),
        )
        response = JSONResponse({"ok": True})
        response.set_cookie(
            session_cookie,
            token,
            max_age=7 * 86400,
            httponly=True,
            secure=origin.startswith("https:"),
            samesite="lax",
            path="/",
        )
        return response

    def provider_row(provider):
        row = next(
            (c for c in CATALOG if c["id"] == provider and c["status"] != "planned"),
            None,
        )
        if not row:
            raise HTTPException(404, "Conector indisponível.")
        return row

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": "0.1.0"}

    @app.get("/api/status")
    def status(request: Request):
        try:
            user = identity(request)
        except HTTPException:
            user = None
        return {
            "testing": bool(getattr(app.state, "testing", False)),
            "setup_required": not bool(store.one("SELECT id FROM users LIMIT 1")),
            "user": {k: v for k, v in user.items() if k != "token_hash"}
            if user
            else None,
            "workspaces": store.all(
                "SELECT w.id,w.name,m.role FROM workspaces w JOIN members m ON m.workspace_id=w.id WHERE m.user_id=?",
                (user["id"],),
            )
            if user
            else [],
            "catalog": CATALOG,
            "public_url": origin,
            "version": "0.1.0",
        }

    @app.post("/api/setup")
    def setup(body: AccountInput, request: Request):
        limiter.check("setup:" + request.client.host, 5)
        if "@" not in body.email:
            raise HTTPException(422, "Informe um e-mail válido.")
        hashed = hash_password(body.password)
        user_id, workspace = uid(), uid()
        with store.db() as db:
            db.execute("BEGIN IMMEDIATE")
            if db.execute("SELECT 1 FROM users LIMIT 1").fetchone():
                raise HTTPException(409, "Esta instalação já foi configurada.")
            db.execute(
                "INSERT INTO users VALUES(?,?,?,?)",
                (user_id, body.email.lower().strip(), body.name, hashed),
            )
            db.execute(
                "INSERT INTO workspaces VALUES(?,?)", (workspace, body.workspace)
            )
            db.execute("INSERT INTO members VALUES(?,?,'owner')", (user_id, workspace))
        return session_response(user_id)

    @app.post("/api/login")
    def login(body: LoginInput, request: Request):
        limiter.check("login:" + request.client.host)
        user = store.one(
            "SELECT * FROM users WHERE email=?", (body.email.lower().strip(),)
        )
        valid = verify_password(
            body.password,
            user["password"] if user else hash_password("invalid-account-password"),
        )
        if not user or not valid:
            raise HTTPException(401, "E-mail ou senha inválidos.")
        return session_response(user["id"])

    @app.post("/api/logout")
    def logout(request: Request):
        store.execute(
            "DELETE FROM sessions WHERE token_hash=?",
            (digest(request.cookies.get(session_cookie, "")),),
        )
        response = JSONResponse({"ok": True})
        response.delete_cookie(session_cookie, path="/")
        return response

    @app.post("/api/workspaces")
    def new_workspace(body: NameInput, request: Request):
        user = identity(request)
        workspace = uid()
        with store.db() as db:
            db.execute("INSERT INTO workspaces VALUES(?,?)", (workspace, body.name))
            db.execute(
                "INSERT INTO members VALUES(?,?,'owner')", (user["id"], workspace)
            )
        return {"id": workspace, "name": body.name}

    @app.get("/api/demo")
    def demo():
        return demo_data()

    @app.get("/api/data")
    def data(request: Request):
        _, workspace, _ = scope(request)
        result = store.workspace_data(workspace)
        result["notes"] = store.all(
            "SELECT * FROM notes WHERE workspace_id=? ORDER BY created DESC",
            (workspace,),
        )
        result["connections"] = store.all(
            "SELECT id,provider,label,status,last_sync,error FROM connections WHERE workspace_id=? ORDER BY rowid DESC",
            (workspace,),
        )
        result["jobs"] = store.all(
            "SELECT id,connection_id,status,created,finished,error FROM jobs WHERE workspace_id=? ORDER BY created DESC LIMIT 20",
            (workspace,),
        )
        return result

    @app.get("/api/apps")
    def apps(request: Request):
        _, workspace = owner(request)
        return {
            "configured": [
                r["provider"]
                for r in store.all(
                    "SELECT DISTINCT provider FROM apps WHERE workspace_id=?",
                    (workspace,),
                )
            ],
            "redirects": {
                p: origin + "/api/oauth/" + p + "/callback" for p in CONNECTORS
            },
        }

    @app.post("/api/apps/{provider}")
    def save_app(provider: str, body: AppInput, request: Request):
        _, workspace = owner(request)
        row = provider_row(provider)
        values = {k: getattr(body, k).strip() for k in row["fields"]}
        if any(not value for value in values.values()):
            raise HTTPException(422, "Preencha todas as credenciais.")
        store.execute(
            "INSERT INTO apps VALUES(?,?,?,?,?)",
            (uid(), workspace, provider, store.seal(values), time.time()),
        )
        return {"ok": True}

    @app.post("/api/oauth/{provider}/start")
    def oauth_start(provider: str, body: StartInput, request: Request):
        user, workspace = owner(request)
        provider_row(provider)
        limiter.check("oauth:" + user["id"], 20)
        configured = store.app(workspace, provider)
        if not configured:
            raise HTTPException(409, "Configure o aplicativo da plataforma primeiro.")
        if body.connection_id and not store.one(
            "SELECT 1 FROM connections WHERE id=? AND workspace_id=? AND provider=?",
            (body.connection_id, workspace, provider),
        ):
            raise HTTPException(404, "Conexão não encontrada.")
        state = secrets.token_urlsafe(40)
        url, verifier = authorization(
            provider,
            store.unseal(configured["secrets"]),
            origin + "/api/oauth/" + provider + "/callback",
            state,
            body.monetary,
        )
        store.execute(
            "INSERT INTO oauth_states VALUES(?,?,?,?,?,?,?,?)",
            (
                digest(state),
                workspace,
                user["id"],
                configured["id"],
                provider,
                store.seal({"value": verifier, "connection_id": body.connection_id}),
                user["token_hash"],
                time.time() + 600,
            ),
        )
        return {"url": url}

    @app.get("/api/oauth/{provider}/callback")
    def oauth_callback(provider: str, request: Request):
        user = identity(request)
        with store.db() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute(
                "SELECT * FROM oauth_states WHERE state_hash=?",
                (digest(request.query_params.get("state", "")),),
            ).fetchone()
            if (
                not row
                or row["expires"] < time.time()
                or row["provider"] != provider
                or row["user_id"] != user["id"]
                or row["session_hash"] != user["token_hash"]
            ):
                raise HTTPException(
                    400,
                    "Autorização expirada ou inválida. Inicie novamente pelo Canalytics.",
                )
            db.execute(
                "DELETE FROM oauth_states WHERE state_hash=?", (row["state_hash"],)
            )
            auth = dict(row)
        if request.query_params.get("error"):
            return RedirectResponse("/?oauth=cancelled", 303)
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(400, "Código de autorização ausente.")
        configured = store.one(
            "SELECT * FROM apps WHERE id=? AND workspace_id=?",
            (auth["app_id"], auth["workspace_id"]),
        )
        try:
            credentials = exchange(
                provider,
                store.unseal(configured["secrets"]),
                code,
                origin + "/api/oauth/" + provider + "/callback",
                store.unseal(auth["verifier"])["value"],
            )
            if provider == "discord":
                verify_discord_guild(
                    credentials, request.query_params.get("guild_id", "")
                )
        except ProviderError:
            return RedirectResponse("/?oauth=failed", 303)
        connection_id = store.unseal(auth["verifier"]).get("connection_id")
        if connection_id:
            changed = store.execute(
                "UPDATE connections SET app_id=?,secrets=?,status='active',error=NULL,next_sync=0 WHERE id=? AND workspace_id=? AND provider=?",
                (
                    auth["app_id"],
                    store.seal(credentials),
                    connection_id,
                    auth["workspace_id"],
                    provider,
                ),
            )
            if not changed:
                raise HTTPException(
                    404, "A conexão foi removida durante a autorização."
                )
        else:
            connection_id = uid()
            store.execute(
                "INSERT INTO connections(id,workspace_id,app_id,provider,label,secrets) VALUES(?,?,?,?,?,?)",
                (
                    connection_id,
                    auth["workspace_id"],
                    auth["app_id"],
                    provider,
                    provider.capitalize(),
                    store.seal(credentials),
                ),
            )
        store.enqueue(auth["workspace_id"], connection_id)
        return RedirectResponse("/?oauth=connected", 303)

    @app.post("/api/connections/{cid}/sync")
    def sync(cid: str, request: Request):
        _, workspace = owner(request)
        if not store.one(
            "SELECT id FROM connections WHERE id=? AND workspace_id=?", (cid, workspace)
        ):
            raise HTTPException(404, "Conexão não encontrada.")
        limiter.check("sync:" + cid, 3, 300)
        return {"job_id": store.enqueue(workspace, cid)}

    @app.delete("/api/connections/{cid}")
    def disconnect(cid: str, request: Request):
        _, workspace = owner(request)
        if not store.execute(
            "DELETE FROM connections WHERE id=? AND workspace_id=?", (cid, workspace)
        ):
            raise HTTPException(404, "Conexão não encontrada.")
        return {
            "ok": True,
            "message": "Credenciais e dados desta conexão foram removidos. Revogue também o acesso nas configurações da plataforma.",
        }

    @app.post("/api/resources/{rid}/notes")
    def add_note(rid: str, body: NoteInput, request: Request):
        row = resource(request, rid)
        note = {
            "id": uid(),
            "workspace_id": row["workspace_id"],
            "resource_id": rid,
            "body": body.body.strip(),
            "created": now_iso(),
        }
        if not note["body"]:
            raise HTTPException(422, "Escreva uma anotação.")
        store.execute("INSERT INTO notes VALUES(?,?,?,?,?)", tuple(note.values()))
        return note

    @app.delete("/api/notes/{nid}")
    def delete_note(nid: str, request: Request):
        _, workspace, _ = scope(request)
        if not store.execute(
            "DELETE FROM notes WHERE id=? AND workspace_id=?", (nid, workspace)
        ):
            raise HTTPException(404, "Anotação não encontrada.")
        return {"ok": True}

    @app.get("/api/resources/{rid}/retention/{video_id}")
    def retention(rid: str, video_id: str, start: date, end: date, request: Request):
        row = resource(request, rid)
        if row["provider"] != "youtube" or not store.one(
            "SELECT 1 FROM contents WHERE resource_id=? AND external_id=?",
            (rid, video_id),
        ):
            raise HTTPException(404, "Vídeo não encontrado neste canal.")
        if start > end or (end - start).days > 365:
            raise HTTPException(422, "Escolha um intervalo de até 366 dias.")
        limiter.check("retention:" + rid, 10, 300)
        conn = store.one(
            "SELECT * FROM connections WHERE id=?", (row["connection_id"],)
        )
        try:
            credentials, _ = fresh_credentials(store, conn)
            return {
                "rows": CONNECTORS["youtube"].retention(
                    credentials, row["external_id"], video_id, str(start), str(end)
                ),
                "source": "YouTube Analytics API",
                "start": str(start),
                "end": str(end),
            }
        except ProviderError as exc:
            raise HTTPException(502, str(exc)) from exc

    @app.get("/api/resources/{rid}/export")
    def export(rid: str, request: Request):
        row = resource(request, rid)
        dataset = store.workspace_data(row["workspace_id"])
        kind = "daily" if json.loads(row["payload"])["mode"] == "daily" else "snapshots"
        rows = [r for r in dataset[kind] if r["resource_id"] == rid]
        if not rows:
            raise HTTPException(404, "Ainda não há dados para exportar.")
        output = io.StringIO()
        writer = csv.DictWriter(
            output, fieldnames=list(dict.fromkeys(k for r in rows for k in r))
        )
        writer.writeheader()
        for item in rows:
            writer.writerow(
                {
                    k: (
                        "'" + v
                        if isinstance(v, str) and v.startswith(("=", "+", "-", "@"))
                        else v
                    )
                    for k, v in item.items()
                }
            )
        return Response(
            "\ufeff" + output.getvalue(),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": 'attachment; filename="canalytics-'
                + row["provider"]
                + '.csv"'
            },
        )

    dist = Path(__file__).resolve().parents[2] / "web" / "dist"
    if serve_frontend and (dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

        @app.get("/favicon.svg")
        def favicon():
            return FileResponse(dist / "favicon.svg")

        @app.get("/")
        def frontend():
            return FileResponse(dist / "index.html")

    return app


app = create_app()
