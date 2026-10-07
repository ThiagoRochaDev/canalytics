from importlib.metadata import entry_points

from .discord import Discord
from .tiktok import TikTok
from .twitch import Twitch
from .youtube import YouTube

CONNECTORS = {c.id: c() for c in [YouTube, Twitch, TikTok, Discord]}
# Extensions are installed by the self-hosting operator, never from untrusted UI input.
for ep in entry_points(group="canalytics.connectors"):
    connector = ep.load()()
    if connector.id in CONNECTORS:
        raise RuntimeError("Duplicate connector id: " + connector.id)
    CONNECTORS[connector.id] = connector

CATALOG = [
    {
        "id": "youtube",
        "name": "YouTube",
        "color": "#ed582f",
        "status": "implemented",
        "kind": "Conteúdo",
        "description": "Histórico diário, vídeos, público e retenção.",
        "capabilities": ["Analytics diário", "Vídeos", "Público", "Retenção"],
        "docs": "https://developers.google.com/youtube/analytics",
        "fields": ["client_id", "client_secret"],
        "limitations": "Sem Reporting API de impressões/CTR nesta versão. Receita depende de escopo adicional.",
    },
    {
        "id": "twitch",
        "name": "Twitch",
        "color": "#8462ec",
        "status": "implemented",
        "kind": "Ao vivo",
        "description": "Estado das lives, seguidores e catálogo de VODs.",
        "capabilities": ["Lives", "Snapshots", "VODs"],
        "docs": "https://dev.twitch.tv/docs/",
        "fields": ["client_id", "client_secret"],
        "limitations": "Histórico começa na coleta. Não fornece o painel financeiro do streamer.",
    },
    {
        "id": "discord",
        "name": "Discord",
        "color": "#5865f2",
        "status": "experimental",
        "kind": "Comunidade",
        "description": "Membros aproximados, presença e canais do servidor.",
        "capabilities": ["Servidor", "Snapshots"],
        "docs": "https://docs.discord.com/developers/topics/oauth2",
        "fields": ["client_id", "client_secret", "bot_token"],
        "limitations": "Sem coleta de mensagens, Gateway ou moderação. Requer instalação do bot.",
    },
    {
        "id": "tiktok",
        "name": "TikTok",
        "color": "#252a34",
        "status": "experimental",
        "kind": "Conteúdo",
        "description": "Perfil, catálogo e contadores públicos autorizados.",
        "capabilities": ["Perfil", "Vídeos", "Snapshots"],
        "docs": "https://developers.tiktok.com/",
        "fields": ["client_id", "client_secret"],
        "limitations": "Client ID corresponde ao Client Key. Requer Login Kit e Display API aprovados. Sem postagem nesta versão.",
    },
    {
        "id": "bilibili",
        "name": "Bilibili",
        "color": "#18a6ce",
        "status": "planned",
        "kind": "Conteúdo",
        "description": "Integração prevista na plataforma aberta da Bilibili.",
        "capabilities": [],
        "docs": "https://open.bilibili.com/",
        "fields": [],
        "limitations": "Acesso e elegibilidade ainda precisam de validação. Nenhuma sincronização implementada.",
    },
]
