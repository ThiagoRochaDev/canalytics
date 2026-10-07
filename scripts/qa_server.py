"""Disposable local fixture server for recorded QA. No external provider calls.

Run from the project root: python scripts/qa_server.py
Open http://localhost:8094/qa/open. The database is created in output/qa/.
Never deploy this helper. Production main.py does not provide /qa/open.
"""

import json
import secrets
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
import uvicorn
from fastapi.responses import RedirectResponse
from canalytics.main import create_app
from canalytics.demo import demo_data
from canalytics.store import uid, digest
from canalytics.security import hash_password
from canalytics.connectors import CONNECTORS

root = Path(__file__).resolve().parents[1]
directory = root / "output" / "qa" / uid()
app = create_app(
    directory,
    public_url="http://localhost:8094",
    worker_enabled=True,
    session_cookie="canalytics_qa_session",
)
app.state.testing = True
store = app.state.store
user_id, workspace_id = uid(), uid()
store.execute(
    "INSERT INTO users VALUES(?,?,?,?)",
    (
        user_id,
        "qa@canalytics.example",
        "QA - dados fictícios",
        hash_password("canalytics-test-only-2026"),
    ),
)
store.execute(
    "INSERT INTO workspaces VALUES(?,?)", (workspace_id, "TGR - ambiente de testes")
)
store.execute("INSERT INTO members VALUES(?,?,'owner')", (user_id, workspace_id))
fixture = demo_data()
for r in fixture["resources"]:
    provider = r["provider"]
    aid, cid = uid(), uid()
    store.execute(
        "INSERT INTO apps VALUES(?,?,?,?,?)",
        (
            aid,
            workspace_id,
            provider,
            store.seal(
                {
                    "client_id": "fixture-" + provider,
                    "client_secret": "FICTIONAL-TEST-ONLY",
                    "bot_token": "FICTIONAL-TEST-ONLY",
                }
            ),
            time.time(),
        ),
    )
    store.execute(
        "INSERT INTO connections(id,workspace_id,app_id,provider,label,secrets,next_sync) VALUES(?,?,?,?,?,?,?)",
        (
            cid,
            workspace_id,
            aid,
            provider,
            "Fixture " + provider,
            store.seal(
                {
                    "access_token": "FICTIONAL-TEST-ONLY",
                    "refresh_token": "FICTIONAL-TEST-ONLY",
                    "expires_at": time.time() + 86400,
                    "guild_id": "123",
                }
            ),
            time.time() + 86400,
        ),
    )

    def fixture_result(r=r):
        resource = {
            **r,
            "external_id": r["id"],
            "source": "Fixture QA - dados fictícios",
        }
        daily = [
            {k: v for k, v in x.items() if k != "resource_id"}
            for x in fixture["daily"]
            if x["resource_id"] == r["id"]
        ]
        contents = [
            {k: v for k, v in x.items() if k != "resource_id"}
            for x in fixture["contents"]
            if x["resource_id"] == r["id"]
        ]
        breakdowns = {
            x["kind"]: x["rows"]
            for x in fixture["breakdowns"]
            if x["resource_id"] == r["id"]
        }
        result = {
            "resources": [resource],
            "daily": daily,
            "contents": contents,
            "breakdowns": breakdowns,
            "warnings": [
                "Sincronização simulada no ambiente QA; nenhum acesso à plataforma."
            ],
            "sync_seconds": 86400,
        }
        if r["mode"] == "daily":
            result["interval"] = [daily[0]["day"], daily[-1]["day"]]
        else:
            last = next(
                x for x in reversed(fixture["snapshots"]) if x["resource_id"] == r["id"]
            )
            result["snapshot"] = {
                k: v for k, v in last.items() if k not in ("resource_id", "observed_at")
            }
        return result

    CONNECTORS[provider].pull = lambda credentials, settings, build=fixture_result: (
        build()
    )
    conn = store.one("SELECT * FROM connections WHERE id=?", (cid,))
    store.save_sync(conn, fixture_result(), fixture["resources"][0]["last_sync"])
    persisted = store.one("SELECT id FROM resources WHERE connection_id=?", (cid,))[
        "id"
    ]
    with store.db() as db:
        for s in fixture["snapshots"]:
            if s["resource_id"] == r["id"]:
                db.execute(
                    "INSERT OR REPLACE INTO snapshots VALUES(?,?,?)",
                    (
                        persisted,
                        s["observed_at"],
                        json.dumps(
                            {
                                k: v
                                for k, v in s.items()
                                if k not in ("resource_id", "observed_at")
                            }
                        ),
                    ),
                )
CONNECTORS["youtube"].retention = lambda *args: [
    {"position": i * 5, "retention": 96 - i * 2.4, "relative": 50} for i in range(21)
]


@app.get("/qa/open")
def fixture_session():
    token = secrets.token_urlsafe(40)
    store.execute(
        "INSERT INTO sessions VALUES(?,?,?)",
        (digest(token), user_id, time.time() + 3600),
    )
    response = RedirectResponse("/", 303)
    response.set_cookie(
        "canalytics_qa_session",
        token,
        httponly=True,
        samesite="lax",
        path="/",
        max_age=3600,
    )
    return response


if __name__ == "__main__":
    print("Disposable QA: http://localhost:8094/qa/open - fictional fixtures only")
    uvicorn.run(app, host="127.0.0.1", port=8094, access_log=False)
