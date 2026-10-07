import pytest

from canalytics.connectors.base import ProviderError
from canalytics.connectors.twitch import Twitch
from canalytics.connectors.youtube import YouTube
from canalytics.oauth import verify_discord_guild


def test_youtube_normalizes_daily_preserves_missing_revenue(monkeypatch):
    calls = []

    def fake(method, url, **kwargs):
        params = kwargs.get("params", {})
        calls.append((url, params))
        if url.endswith("/channels"):
            return {
                "items": [
                    {
                        "id": "channel",
                        "snippet": {"title": "Creator"},
                        "statistics": {
                            "subscriberCount": "123",
                            "viewCount": "1000",
                            "videoCount": "1",
                        },
                        "contentDetails": {"relatedPlaylists": {"uploads": "playlist"}},
                    }
                ]
            }
        if url.endswith("/reports"):
            names = params["metrics"].split(",")
            dim = params["dimensions"]
            return {
                "columnHeaders": [{"name": n} for n in [dim, *names]],
                "rows": [["2026-01-01", 20, 40, 120, 50, 3, 2, 1, 5, 1]]
                if dim == "day"
                else [],
            }
        if url.endswith("/playlistItems"):
            return {"items": [{"contentDetails": {"videoId": "video"}}]}
        if url.endswith("/videos"):
            return {
                "items": [
                    {
                        "id": "video",
                        "snippet": {
                            "title": "Title",
                            "publishedAt": "2026-01-01T00:00:00Z",
                        },
                        "contentDetails": {"duration": "PT30S"},
                        "statistics": {"viewCount": "20"},
                    }
                ]
            }
        raise AssertionError(url)

    monkeypatch.setattr("canalytics.connectors.youtube.request", fake)
    result = YouTube().pull({"access_token": "token"}, {})
    assert result["daily"][0]["views"] == 20
    assert result["daily"][0]["revenue"] is None
    assert result["contents"][0]["likes"] is None
    assert (
        result["contents"][0]["format"] == "video"
    )  # Duration alone must not imply Shorts.
    assert result["contents"][0]["scope"] == "lifetime"
    assert result["resources"][0]["mode"] == "daily"


def test_twitch_offline_not_zero_audience(monkeypatch):
    def fake(method, url, **kwargs):
        if url.endswith("/validate"):
            return {"client_id": "client"}
        if url.endswith("/users"):
            return {
                "data": [{"id": "123", "display_name": "Streamer", "login": "streamer"}]
            }
        if url.endswith("/streams"):
            return {"data": []}
        if url.endswith("/followers"):
            return {"total": 25, "data": []}
        if url.endswith("/videos"):
            return {"data": []}
        raise AssertionError(url)

    monkeypatch.setattr("canalytics.connectors.twitch.request", fake)
    result = Twitch().pull({"access_token": "token"}, {"client_id": "client"})
    assert result["snapshot"]["live_viewers"] is None
    assert result["snapshot"]["live"] is False
    assert "daily" not in result


def test_discord_rejects_unmanaged_server(monkeypatch):
    monkeypatch.setattr(
        "canalytics.oauth.request",
        lambda *a, **kw: [{"id": "123", "permissions": "1024", "owner": False}],
    )
    with pytest.raises(ProviderError):
        verify_discord_guild({"access_token": "token"}, "123")
    monkeypatch.setattr(
        "canalytics.oauth.request",
        lambda *a, **kw: [{"id": "123", "permissions": "32", "owner": False}],
    )
    token = {"access_token": "token"}
    verify_discord_guild(token, "123")
    assert token["guild_id"] == "123"
