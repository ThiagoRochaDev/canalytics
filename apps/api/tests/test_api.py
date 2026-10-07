import json
import time
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient

from canalytics.main import create_app
from canalytics.store import uid
from canalytics.worker import run_job

HEAD = {"X-Canalytics-Request": "1", "Origin": "http://localhost:8093"}


@pytest.fixture
def instance(tmp_path):
    app = create_app(tmp_path, worker_enabled=False, serve_frontend=False)
    with TestClient(app, headers=HEAD, base_url="http://localhost:8093") as client:
        yield app, client


def setup(client):
    response = client.post(
        "/api/setup",
        json={
            "email": "creator@example.test",
            "password": "a-long-test-password",
            "name": "Creator",
            "workspace": "Studio",
        },
    )
    assert response.status_code == 200
    workspace = client.get("/api/status").json()["workspaces"][0]["id"]
    client.headers["X-Workspace-ID"] = workspace
    return workspace


def seed(app, workspace):
    store = app.state.store
    aid, cid = uid(), uid()
    store.execute(
        "INSERT INTO apps VALUES(?,?,?,?,?)",
        (
            aid,
            workspace,
            "youtube",
            store.seal({"client_id": "test", "client_secret": "never-return-this"}),
            time.time(),
        ),
    )
    store.execute(
        "INSERT INTO connections(id,workspace_id,app_id,provider,label,secrets) VALUES(?,?,?,?,?,?)",
        (
            cid,
            workspace,
            aid,
            "youtube",
            "Test",
            store.seal(
                {"access_token": "secret-token", "expires_at": time.time() + 3600}
            ),
        ),
    )
    conn = store.one("SELECT * FROM connections WHERE id=?", (cid,))
    result = {
        "resources": [
            {
                "external_id": "yt-channel",
                "name": "Test channel",
                "mode": "daily",
                "provider": "youtube",
            }
        ],
        "daily": [{"day": "2026-01-01", "views": 50, "revenue": None}],
        "contents": [{"id": "test-video", "title": "Test video"}],
        "interval": ["2026-01-01", "2026-01-01"],
    }
    store.save_sync(conn, result, "2026-01-04T12:00:00+00:00")
    rid = store.one("SELECT id FROM resources WHERE connection_id=?", (cid,))["id"]
    return conn, rid, result


def test_demo_and_auth_boundary(instance):
    app, client = instance
    assert client.get("/api/demo").json()["demo"] is True
    assert client.get("/api/data").status_code == 401
    assert app.state.store.one("SELECT 1 FROM connections") is None
    setup(client)
    assert client.get("/api/data").json()["resources"] == []
    assert (
        client.post(
            "/api/setup",
            json={"email": "other@t.test", "password": "other-password-123"},
        ).status_code
        == 409
    )
    cookie = client.cookies.get("canalytics_session")
    assert cookie not in json.dumps(app.state.store.all("SELECT * FROM sessions"))


def test_csrf_and_logout(instance):
    _, client = instance
    setup(client)
    assert (
        client.post(
            "/api/workspaces",
            json={"name": "Bad"},
            headers={"Origin": "https://attacker.test"},
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/workspaces",
            json={"name": "Bad"},
            headers={"X-Canalytics-Request": "0"},
        ).status_code
        == 403
    )
    assert client.post("/api/logout").status_code == 200
    assert client.get("/api/data").status_code == 401
    assert (
        client.post(
            "/api/login",
            json={"email": "creator@example.test", "password": "a-long-test-password"},
        ).status_code
        == 200
    )


def test_workspace_isolation_for_data_notes_exports_and_removal(instance):
    app, client = instance
    a = setup(client)
    conn, rid, _ = seed(app, a)
    # The authenticated user owns both areas; selection still isolates resources.
    b = client.post("/api/workspaces", json={"name": "Another studio"}).json()["id"]
    client.headers["X-Workspace-ID"] = b
    assert client.get("/api/data").json()["resources"] == []
    assert client.get("/api/resources/" + rid + "/export").status_code == 404
    assert (
        client.post(
            "/api/resources/" + rid + "/notes", json={"body": "No access"}
        ).status_code
        == 404
    )
    assert client.delete("/api/connections/" + conn["id"]).status_code == 404
    client.headers["X-Workspace-ID"] = "unknown-workspace"
    assert client.get("/api/data").status_code == 403
    client.headers["X-Workspace-ID"] = a
    note = client.post(
        "/api/resources/" + rid + "/notes", json={"body": "Published a video"}
    ).json()
    assert client.get("/api/data").json()["notes"][0]["body"] == "Published a video"
    client.headers["X-Workspace-ID"] = b
    assert client.delete("/api/notes/" + note["id"]).status_code == 404


def test_credentials_are_encrypted_and_not_echoed(instance):
    app, client = instance
    workspace = setup(client)
    response = client.post(
        "/api/apps/youtube",
        json={"client_id": "application", "client_secret": "very-private-secret"},
    )
    assert response.status_code == 200
    assert (
        "very-private-secret"
        not in app.state.store.app(workspace, "youtube")["secrets"]
    )
    assert "very-private-secret" not in client.get("/api/apps").text
    assert "very-private-secret" not in client.get("/api/data").text


def test_oauth_state_binding_replay_and_callback(monkeypatch, instance):
    app, client = instance
    setup(client)
    client.post(
        "/api/apps/youtube", json={"client_id": "app", "client_secret": "secret"}
    )
    url = client.post("/api/oauth/youtube/start", json={}).json()["url"]
    query = parse_qs(urlparse(url).query)
    assert query["code_challenge_method"] == ["S256"]
    assert "monetary" not in query["scope"][0]
    state = query["state"][0]
    assert state not in json.dumps(app.state.store.all("SELECT * FROM oauth_states"))
    callback = "/api/oauth/youtube/callback?state=" + state + "&code=code"
    assert (
        client.get(callback.replace(state, "wrong"), follow_redirects=False).status_code
        == 400
    )
    # A second valid login session is not the initiating browser session.
    cookie = client.cookies.get("canalytics_session")
    client.post(
        "/api/login",
        json={"email": "creator@example.test", "password": "a-long-test-password"},
    )
    assert client.get(callback, follow_redirects=False).status_code == 400
    client.cookies.clear()
    client.cookies.set("canalytics_session", cookie, domain="localhost.local", path="/")
    monkeypatch.setattr(
        "canalytics.main.exchange",
        lambda *args: {
            "access_token": "private-access",
            "refresh_token": "private-refresh",
            "expires_at": time.time() + 3600,
        },
    )
    assert client.get(callback, follow_redirects=False).status_code == 303
    assert client.get(callback, follow_redirects=False).status_code == 400
    payload = client.get("/api/data").json()
    assert len(payload["connections"]) == 1 and len(payload["jobs"]) == 1
    assert "private-access" not in json.dumps(payload)
    assert payload["connections"][0]["provider"] == "youtube"


def test_sync_idempotency_and_delete_inflight(instance):
    app, client = instance
    workspace = setup(client)
    conn, rid, result = seed(app, workspace)
    app.state.store.save_sync(conn, result, "2026-01-05T12:00:00+00:00")
    assert len(client.get("/api/data").json()["daily"]) == 1
    first = client.post("/api/connections/" + conn["id"] + "/sync").json()["job_id"]
    assert (
        client.post("/api/connections/" + conn["id"] + "/sync").json()["job_id"]
        == first
    )
    client.post("/api/resources/" + rid + "/notes", json={"body": "A note"})
    assert client.delete("/api/connections/" + conn["id"]).status_code == 200
    app.state.store.save_sync(conn, result, "2026-01-06T12:00:00+00:00")
    assert client.get("/api/data").json()["resources"] == []
    assert app.state.store.all("SELECT * FROM notes") == []


def test_nulls_and_csv_formula_escaping(instance):
    app, client = instance
    workspace = setup(client)
    conn, rid, result = seed(app, workspace)
    result["daily"][0]["source"] = "=HYPERLINK(test)"
    app.state.store.save_sync(conn, result, "2026-01-06")
    payload = client.get("/api/data").json()
    assert payload["daily"][0]["revenue"] is None
    export = client.get("/api/resources/" + rid + "/export")
    assert export.status_code == 200
    assert "'=HYPERLINK(test)" in export.text


def test_worker_error_never_leaks_tokens(monkeypatch, instance):
    app, client = instance
    workspace = setup(client)
    conn, _, _ = seed(app, workspace)
    job_id = app.state.store.enqueue(workspace, conn["id"])

    def fail(*args):
        raise RuntimeError("url?access_token=super-private")

    monkeypatch.setattr("canalytics.worker.fresh_credentials", fail)
    run_job(
        app.state.store,
        {
            "id": job_id,
            "workspace_id": workspace,
            "connection_id": conn["id"],
            "attempts": 1,
        },
    )
    payload = client.get("/api/data").json()
    assert "super-private" not in json.dumps(payload)
    assert payload["jobs"][0]["status"] == "error"


def test_retention_rejects_foreign_video(instance):
    app, client = instance
    workspace = setup(client)
    _, rid, _ = seed(app, workspace)
    assert (
        client.get(
            "/api/resources/"
            + rid
            + "/retention/foreign?start=2026-01-01&end=2026-01-28"
        ).status_code
        == 404
    )


def test_reauthorization_keeps_resource_history(monkeypatch, instance):
    app, client = instance
    workspace = setup(client)
    conn, rid, result = seed(app, workspace)
    url = client.post(
        "/api/oauth/youtube/start", json={"connection_id": conn["id"]}
    ).json()["url"]
    state = parse_qs(urlparse(url).query)["state"][0]
    monkeypatch.setattr(
        "canalytics.main.exchange",
        lambda *args: {"access_token": "new-token", "expires_at": time.time() + 3600},
    )
    assert (
        client.get(
            "/api/oauth/youtube/callback?state=" + state + "&code=new",
            follow_redirects=False,
        ).status_code
        == 303
    )
    dataset = client.get("/api/data").json()
    assert len(dataset["connections"]) == 1
    assert dataset["resources"][0]["id"] == rid
    assert len(dataset["daily"]) == 1
    changed = {
        **result,
        "resources": [
            {"external_id": "wrong-channel", "name": "Wrong", "mode": "daily"}
        ],
    }
    with pytest.raises(ValueError):
        app.state.store.save_sync(conn, changed, "2026-01-07")
    assert client.get("/api/data").json()["resources"][0]["id"] == rid


def test_expired_oauth_state_and_foreign_host(instance):
    app, client = instance
    workspace = setup(client)
    seed(app, workspace)
    url = client.post("/api/oauth/youtube/start", json={}).json()["url"]
    state = parse_qs(urlparse(url).query)["state"][0]
    app.state.store.execute("UPDATE oauth_states SET expires=0")
    assert (
        client.get("/api/oauth/youtube/callback?state=" + state + "&code=x").status_code
        == 400
    )
    assert (
        client.get("/api/status", headers={"Host": "attacker.example"}).status_code
        == 400
    )
