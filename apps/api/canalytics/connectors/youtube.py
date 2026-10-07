from .base import Connector, ProviderError, date_window, request


class YouTube(Connector):
    id = "youtube"
    title = "YouTube"

    def pull(self, credentials, app):
        headers = {"Authorization": "Bearer " + credentials["access_token"]}
        channel = request(
            "GET",
            "https://www.googleapis.com/youtube/v3/channels",
            headers=headers,
            params={"part": "snippet,statistics,contentDetails", "mine": "true"},
        ).get("items", [])
        if not channel:
            raise ProviderError("Nenhum canal disponível para esta autorização.", 403)
        c = channel[0]
        stats = c["statistics"]
        start, end = date_window()
        rid = c["id"]
        warnings = []

        def report(metrics, dimensions, **extra):
            response = request(
                "GET",
                "https://youtubeanalytics.googleapis.com/v2/reports",
                headers=headers,
                params={
                    "ids": "channel==" + rid,
                    "startDate": start,
                    "endDate": end,
                    "metrics": metrics,
                    "dimensions": dimensions,
                    **extra,
                },
            )
            names = [x["name"] for x in response.get("columnHeaders", [])]
            return [dict(zip(names, r)) for r in response.get("rows", [])]

        rows = report(
            "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,likes,comments,shares,subscribersGained,subscribersLost",
            "day",
            sort="day",
        )
        daily = [
            {
                "day": r["day"],
                "views": r["views"],
                "minutes": r["estimatedMinutesWatched"],
                "average_duration": r["averageViewDuration"],
                "average_percentage": r["averageViewPercentage"],
                "likes": r["likes"],
                "comments": r["comments"],
                "shares": r["shares"],
                "gained": r["subscribersGained"],
                "lost": r["subscribersLost"],
                "revenue": None,
                "source": "YouTube Analytics API",
                "kind": "official_daily",
            }
            for r in rows
        ]
        if "yt-analytics-monetary.readonly" in str(credentials.get("scope", "")):
            try:
                monetary = {
                    r["day"]: r["estimatedRevenue"]
                    for r in report("estimatedRevenue", "day", currency="USD")
                }
                for row in daily:
                    row["revenue"] = monetary.get(row["day"])
            except ProviderError:
                warnings.append(
                    "Receita indisponível para esta autorização; mantida como não disponível."
                )
        breakdowns = {}
        for kind, dimension in [
            ("traffic", "insightTrafficSourceType"),
            ("country", "country"),
            ("device", "deviceType"),
        ]:
            try:
                br = report("views", dimension, sort="-views", maxResults=25)
                breakdowns[kind] = [
                    {
                        "label": r[dimension],
                        "value": r["views"],
                        "start": start,
                        "end": end,
                        "unit": "views",
                    }
                    for r in br
                ]
            except ProviderError:
                warnings.append("Relatório de " + kind + " indisponível.")
        playlist = c["contentDetails"]["relatedPlaylists"]["uploads"]
        ids = []
        token = None
        for _ in range(10):
            params = {
                "part": "contentDetails",
                "playlistId": playlist,
                "maxResults": 50,
            }
            if token:
                params["pageToken"] = token
            page = request(
                "GET",
                "https://www.googleapis.com/youtube/v3/playlistItems",
                headers=headers,
                params=params,
            )
            ids.extend(x["contentDetails"]["videoId"] for x in page.get("items", []))
            token = page.get("nextPageToken")
            if not token:
                break
        if token:
            warnings.append(
                "Catálogo limitado aos 500 vídeos mais recentes nesta versão."
            )
        contents = []
        for offset in range(0, len(ids), 50):
            page = request(
                "GET",
                "https://www.googleapis.com/youtube/v3/videos",
                headers=headers,
                params={
                    "part": "snippet,statistics,contentDetails",
                    "id": ",".join(ids[offset : offset + 50]),
                },
            )
            for v in page.get("items", []):
                s = v.get("statistics", {})
                contents.append(
                    {
                        "id": v["id"],
                        "title": v["snippet"]["title"],
                        "published": v["snippet"]["publishedAt"],
                        "format": "video",
                        "views": int(s["viewCount"]) if "viewCount" in s else None,
                        "likes": int(s["likeCount"]) if "likeCount" in s else None,
                        "comments": int(s["commentCount"])
                        if "commentCount" in s
                        else None,
                        "duration": v["contentDetails"]["duration"],
                        "url": "https://www.youtube.com/watch?v=" + v["id"],
                        "scope": "lifetime",
                        "source": "YouTube Data API",
                    }
                )
        resource = {
            "external_id": rid,
            "name": c["snippet"]["title"],
            "kind": "channel",
            "color": "#ed582f",
            "initials": "YT",
            "followers": None
            if stats.get("hiddenSubscriberCount")
            else int(stats.get("subscriberCount", 0)),
            "content_count": int(stats.get("videoCount", 0)),
            "views_total": int(stats.get("viewCount", 0)),
            "url": "https://www.youtube.com/channel/" + rid,
            "currency": "USD",
            "mode": "daily",
            "coverage": {
                "start": start,
                "requested_end": end,
                "end": daily[-1]["day"] if daily else None,
            },
            "capabilities": ["daily_analytics", "contents", "audience", "retention"],
            "source": "YouTube Analytics / Data API",
        }
        return {
            "resources": [resource],
            "daily": daily,
            "contents": contents,
            "breakdowns": breakdowns,
            "interval": [start, end],
            "warnings": warnings,
        }

    def retention(self, credentials, channel_id, video_id, start, end):
        response = request(
            "GET",
            "https://youtubeanalytics.googleapis.com/v2/reports",
            headers={"Authorization": "Bearer " + credentials["access_token"]},
            params={
                "ids": "channel==" + channel_id,
                "startDate": start,
                "endDate": end,
                "metrics": "audienceWatchRatio,relativeRetentionPerformance",
                "dimensions": "elapsedVideoTimeRatio",
                "filters": "video==" + video_id,
            },
        )
        return [
            {"position": r[0] * 100, "retention": r[1] * 100, "relative": r[2] * 100}
            for r in response.get("rows", [])
        ]
