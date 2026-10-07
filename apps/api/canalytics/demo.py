"""Deterministic, explicitly fictional data. No credentials or external calls."""

import math
from datetime import datetime, timedelta, timezone


def demo_data():
    end = datetime.now(timezone.utc).date() - timedelta(days=3)
    resources = [
        {
            "id": "demo-yt",
            "provider": "youtube",
            "name": "TGR Lab",
            "kind": "channel",
            "color": "#ed582f",
            "initials": "YT",
            "followers": 28430,
            "content_count": 86,
            "mode": "daily",
            "capabilities": ["daily_analytics", "contents", "audience", "retention"],
            "source": "Dados fictícios • demonstração",
            "coverage": {
                "start": str(end - timedelta(days=179)),
                "end": str(end),
                "requested_end": str(end),
            },
            "last_sync": str(end) + "T12:00:00Z",
        },
        {
            "id": "demo-tw",
            "provider": "twitch",
            "name": "TGR Live",
            "kind": "stream",
            "color": "#8462ec",
            "initials": "TW",
            "followers": 6482,
            "content_count": 24,
            "mode": "snapshot",
            "live": True,
            "live_title": "Construindo com a comunidade",
            "source": "Dados fictícios • demonstração",
            "capabilities": ["snapshots", "live", "contents"],
            "last_sync": str(end) + "T12:00:00Z",
        },
        {
            "id": "demo-dc",
            "provider": "discord",
            "name": "TGR Community",
            "kind": "community",
            "color": "#5865f2",
            "initials": "DC",
            "followers": 3210,
            "followers_label": "Membros aproximados",
            "content_count": 18,
            "mode": "snapshot",
            "source": "Dados fictícios • demonstração",
            "capabilities": ["snapshots", "community"],
            "last_sync": str(end) + "T12:00:00Z",
        },
        {
            "id": "demo-tt",
            "provider": "tiktok",
            "name": "TGR em 60s",
            "kind": "profile",
            "color": "#252a34",
            "initials": "TK",
            "followers": 18760,
            "content_count": 54,
            "mode": "snapshot",
            "source": "Dados fictícios • demonstração",
            "capabilities": ["snapshots", "contents"],
            "last_sync": str(end) + "T12:00:00Z",
        },
    ]
    daily = []
    snapshots = []
    for i in range(180):
        day = str(end - timedelta(days=179 - i))
        views = round(
            4300 + i * 33 + math.sin(i / 4) * 1700 + (6000 if i % 31 in (5, 6) else 0)
        )
        daily.append(
            {
                "resource_id": "demo-yt",
                "day": day,
                "views": views,
                "minutes": round(views * 4.4),
                "average_duration": 264,
                "average_percentage": 42.8,
                "likes": round(views * 0.042),
                "comments": round(views * 0.003),
                "shares": round(views * 0.006),
                "gained": round(views * 0.009),
                "lost": round(views * 0.0014),
                "revenue": None,
                "kind": "official_daily",
                "source": "Simulação de relatório diário",
            }
        )
        for rid, base in [("demo-tw", 5200), ("demo-dc", 2510), ("demo-tt", 12000)]:
            snapshots.append(
                {
                    "resource_id": rid,
                    "observed_at": day + "T12:00:00Z",
                    "followers": base + i * (7 if rid != "demo-tt" else 37),
                    "members": base + i * 4 if rid == "demo-dc" else None,
                    "online": round(240 + math.sin(i) * 50)
                    if rid == "demo-dc"
                    else None,
                    "live_viewers": round(360 + i * 2 + math.sin(i) * 110)
                    if rid == "demo-tw"
                    else None,
                    "live": rid == "demo-tw",
                    "kind": "observed_snapshot",
                    "source": "Simulação de coleta",
                }
            )
    titles = [
        "Como organizamos um projeto open source",
        "Um estúdio de criação que cabe na mesa",
        "Do roteiro à publicação: nosso processo",
        "Ferramentas que usamos todos os dias",
        "Criando uma comunidade do zero",
        "Automatize o trabalho, preserve a criatividade",
        "Por dentro do setup TGR",
        "O que aprendemos depois de 30 vídeos",
        "Seu primeiro dashboard de verdade",
        "Uma semana criando em público",
        "Vídeo longo ou conteúdo curto?",
        "Como medimos o que importa",
    ]
    contents = []
    for i, title in enumerate(titles):
        contents.append(
            {
                "id": "demo-video-" + str(i),
                "resource_id": "demo-yt",
                "title": title,
                "published": str(end - timedelta(days=i * 6 + 1)) + "T15:00:00Z",
                "format": "video",
                "views": round(22400 + (11 - i) * 5300 + math.sin(i) * 9200),
                "likes": 320 + i * 91,
                "comments": 46 + i * 13,
                "shares": None,
                "duration": "PT8M32S",
                "scope": "lifetime",
                "source": "Dados fictícios",
            }
        )
    breakdowns = [
        {
            "resource_id": "demo-yt",
            "kind": kind,
            "rows": [
                {
                    "label": label,
                    "value": value,
                    "start": str(end - timedelta(days=179)),
                    "end": str(end),
                    "unit": "views",
                }
                for label, value in rows
            ],
        }
        for kind, rows in {
            "country": [("BR", 74000), ("PT", 12000), ("US", 8500), ("Outros", 5500)],
            "device": [
                ("MOBILE", 62000),
                ("DESKTOP", 23000),
                ("TV", 11000),
                ("TABLET", 4000),
            ],
            "traffic": [
                ("RELATED_VIDEO", 41000),
                ("YT_SEARCH", 28000),
                ("SUBSCRIBER", 19000),
                ("EXT_URL", 12000),
            ],
        }.items()
    ]
    return {
        "demo": True,
        "resources": resources,
        "daily": daily,
        "snapshots": snapshots,
        "contents": contents,
        "breakdowns": breakdowns,
        "notes": [],
        "jobs": [],
        "connections": [],
    }
