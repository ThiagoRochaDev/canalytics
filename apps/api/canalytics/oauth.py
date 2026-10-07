"""Official authorization code flows. Tokens never leave the API."""

import base64
import hashlib
import secrets
import threading
import time
from urllib.parse import urlencode

from .connectors.base import ProviderError, request

AUTH = {
    "youtube": "https://accounts.google.com/o/oauth2/v2/auth",
    "twitch": "https://id.twitch.tv/oauth2/authorize",
    "discord": "https://discord.com/oauth2/authorize",
    "tiktok": "https://www.tiktok.com/v2/auth/authorize/",
}
TOKEN = {
    "youtube": "https://oauth2.googleapis.com/token",
    "twitch": "https://id.twitch.tv/oauth2/token",
    "discord": "https://discord.com/api/v10/oauth2/token",
    "tiktok": "https://open.tiktokapis.com/v2/oauth/token/",
}
SCOPES = {
    "youtube": "https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/yt-analytics.readonly",
    "twitch": "moderator:read:followers",
    "discord": "identify guilds bot",
    "tiktok": "user.info.basic,user.info.stats,video.list",
}


def authorization(provider, app, redirect, state, monetary=False):
    verifier = secrets.token_urlsafe(64)
    params = {
        "client_id": app["client_id"],
        "redirect_uri": redirect,
        "response_type": "code",
        "state": state,
        "scope": SCOPES[provider],
    }
    if provider == "youtube":
        params.update(access_type="offline", prompt="consent select_account")
        if monetary:
            params["scope"] += (
                " https://www.googleapis.com/auth/yt-analytics-monetary.readonly"
            )
        params.update(
            code_challenge=base64.urlsafe_b64encode(
                hashlib.sha256(verifier.encode()).digest()
            )
            .decode()
            .rstrip("="),
            code_challenge_method="S256",
        )
    if provider == "twitch":
        params["force_verify"] = "true"
    if provider == "discord":
        params["permissions"] = "1024"
    if provider == "tiktok":
        params["client_key"] = params.pop("client_id")
        # Web Login Kit uses a confidential client; PKCE is required for mobile/desktop only.
    return AUTH[provider] + "?" + urlencode(params), verifier


def token_request(provider, app, fields):
    data = {
        "client_id": app["client_id"],
        "client_secret": app["client_secret"],
        **fields,
    }
    if provider == "tiktok":
        data["client_key"] = data.pop("client_id")
    result = request("POST", TOKEN[provider], data=data)
    if not result.get("access_token"):
        raise ProviderError(
            "A plataforma não concedeu a autorização. Confira as configurações do aplicativo.",
            403,
        )
    result["expires_at"] = time.time() + int(result.get("expires_in", 3600))
    return result


def exchange(provider, app, code, redirect, verifier):
    fields = {
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect,
    }
    if provider == "youtube":
        fields["code_verifier"] = verifier
    return token_request(provider, app, fields)


_refresh_lock = threading.RLock()


def fresh_credentials(store, connection):
    with _refresh_lock:
        latest = store.one(
            "SELECT * FROM connections WHERE id=? AND workspace_id=?",
            (connection["id"], connection["workspace_id"]),
        )
        if not latest:
            raise ProviderError("Conexão removida.", 404)
        return _fresh_credentials(store, latest)


def _fresh_credentials(store, connection):
    credentials = store.unseal(connection["secrets"])
    approw = store.one(
        "SELECT secrets FROM apps WHERE id=? AND workspace_id=?",
        (connection["app_id"], connection["workspace_id"]),
    )
    app = store.unseal(approw["secrets"])
    if credentials.get("expires_at", 0) < time.time() + 120:
        if not credentials.get("refresh_token"):
            raise ProviderError("A autorização expirou. Reconecte a conta.", 401)
        refreshed = token_request(
            connection["provider"],
            app,
            {
                "grant_type": "refresh_token",
                "refresh_token": credentials["refresh_token"],
            },
        )
        credentials.update(refreshed)
        store.execute(
            "UPDATE connections SET secrets=? WHERE id=? AND workspace_id=?",
            (store.seal(credentials), connection["id"], connection["workspace_id"]),
        )
    return credentials, app


def verify_discord_guild(credentials, guild_id):
    if not guild_id or not guild_id.isdigit():
        raise ProviderError("O Discord não informou um servidor válido.", 403)
    guilds = request(
        "GET",
        "https://discord.com/api/v10/users/@me/guilds",
        headers={"Authorization": "Bearer " + credentials["access_token"]},
    )
    guild = next((g for g in guilds if g["id"] == guild_id), None)
    if not guild or not (
        guild.get("owner")
        or int(guild.get("permissions", "0")) & 32
        or int(guild.get("permissions", "0")) & 8
    ):
        raise ProviderError("É preciso administrar o servidor autorizado.", 403)
    credentials["guild_id"] = guild_id
