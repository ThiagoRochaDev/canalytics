from .base import Connector, ProviderError, request


class Twitch(Connector):
    id = "twitch"
    title = "Twitch"

    def pull(self, credentials, app):
        headers = {
            "Authorization": "Bearer " + credentials["access_token"],
            "Client-Id": app["client_id"],
        }
        request(
            "GET",
            "https://id.twitch.tv/oauth2/validate",
            headers={"Authorization": "OAuth " + credentials["access_token"]},
        )

        def get(path, **params):
            return request(
                "GET",
                "https://api.twitch.tv/helix/" + path,
                headers=headers,
                params=params,
            )

        user = get("users")["data"][0]
        rid = user["id"]
        streams = get("streams", user_id=rid).get("data", [])
        stream = streams[0] if streams else None
        warnings = []
        followers = None
        try:
            followers = get("channels/followers", broadcaster_id=rid, first=1).get(
                "total"
            )
        except ProviderError:
            warnings.append("Seguidores indisponíveis para o escopo atual.")
        videos = get("videos", user_id=rid, first=100)
        if videos.get("pagination", {}).get("cursor"):
            warnings.append("Catálogo limitado aos 100 VODs mais recentes.")
        contents = [
            {
                "id": v["id"],
                "title": v["title"],
                "published": v["published_at"],
                "format": v["type"],
                "duration": v["duration"],
                "views": v["view_count"],
                "likes": None,
                "comments": None,
                "url": v["url"],
                "scope": "lifetime",
                "source": "Twitch Helix",
            }
            for v in videos.get("data", [])
        ]
        resource = {
            "external_id": rid,
            "name": user["display_name"],
            "kind": "stream",
            "color": "#8462ec",
            "initials": "TW",
            "followers": followers,
            "content_count": len(contents),
            "content_count_scope": "loaded",
            "mode": "snapshot",
            "url": "https://www.twitch.tv/" + user["login"],
            "live": bool(stream),
            "live_title": stream["title"] if stream else None,
            "capabilities": ["snapshots", "contents", "live"],
            "source": "Twitch Helix",
        }
        snapshot = {
            "followers": followers,
            "live_viewers": stream["viewer_count"] if stream else None,
            "live": bool(stream),
            "source": "Twitch Helix",
            "kind": "observed_snapshot",
        }
        return {
            "resources": [resource],
            "snapshot": snapshot,
            "contents": contents,
            "warnings": warnings,
            "sync_seconds": 900,
        }
