from .base import Connector, ProviderError, request


class TikTok(Connector):
    id = "tiktok"
    title = "TikTok"

    def pull(self, credentials, app):
        headers = {"Authorization": "Bearer " + credentials["access_token"]}

        def call(method, path, **kw):
            data = request(
                method, "https://open.tiktokapis.com" + path, headers=headers, **kw
            )
            if data.get("error", {}).get("code") not in (None, "ok"):
                raise ProviderError(
                    "TikTok recusou a consulta. Confira os produtos e escopos aprovados.",
                    403,
                )
            return data.get("data", {})

        fields = (
            "open_id,display_name,avatar_url,follower_count,video_count,likes_count"
        )
        user = call("GET", "/v2/user/info/", params={"fields": fields})["user"]
        contents = []
        cursor = 0
        more = False
        for _ in range(10):
            data = call(
                "POST",
                "/v2/video/list/",
                params={
                    "fields": "id,title,create_time,duration,share_url,view_count,like_count,comment_count,share_count"
                },
                json={"max_count": 20, "cursor": cursor},
            )
            for v in data.get("videos", []):
                from datetime import datetime, timezone

                contents.append(
                    {
                        "id": v["id"],
                        "title": v.get("title", "Vídeo"),
                        "published": datetime.fromtimestamp(
                            v["create_time"], timezone.utc
                        ).isoformat(),
                        "format": "video",
                        "duration": str(v["duration"]) + "s",
                        "views": v.get("view_count"),
                        "likes": v.get("like_count"),
                        "comments": v.get("comment_count"),
                        "shares": v.get("share_count"),
                        "url": v.get("share_url"),
                        "scope": "lifetime",
                        "source": "TikTok Display API",
                    }
                )
            more = data.get("has_more", False)
            cursor = data.get("cursor", 0)
            if not more:
                break
        resource = {
            "external_id": user["open_id"],
            "name": user["display_name"],
            "kind": "profile",
            "color": "#252a34",
            "initials": "TK",
            "followers": user.get("follower_count"),
            "content_count": user.get("video_count"),
            "mode": "snapshot",
            "capabilities": ["snapshots", "contents"],
            "source": "TikTok Display API",
        }
        return {
            "resources": [resource],
            "snapshot": {
                "followers": user.get("follower_count"),
                "likes_total": user.get("likes_count"),
                "kind": "observed_snapshot",
                "source": "TikTok Display API",
            },
            "contents": contents,
            "warnings": ["Catálogo limitado aos 200 vídeos mais recentes."]
            if more
            else [],
            "sync_seconds": 86400,
        }
