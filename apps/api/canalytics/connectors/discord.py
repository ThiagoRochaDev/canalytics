from .base import Connector, ProviderError, request


class Discord(Connector):
    id = "discord"
    title = "Discord"

    def pull(self, credentials, app):
        guild_id = credentials.get("guild_id")
        if not guild_id:
            raise ProviderError("Servidor não identificado. Reconecte o Discord.", 403)
        # Re-check current membership before every use of the bot credential.
        from ..oauth import verify_discord_guild

        verify_discord_guild(credentials, guild_id)
        headers = {"Authorization": "Bot " + app["bot_token"]}
        guild = request(
            "GET",
            "https://discord.com/api/v10/guilds/" + guild_id,
            headers=headers,
            params={"with_counts": "true"},
        )
        channels = request(
            "GET",
            "https://discord.com/api/v10/guilds/" + guild_id + "/channels",
            headers=headers,
        )
        count = guild.get("approximate_member_count")
        resource = {
            "external_id": guild_id,
            "name": guild["name"],
            "kind": "community",
            "color": "#5865f2",
            "initials": "DC",
            "followers": count,
            "followers_label": "Membros aproximados",
            "content_count": len(channels),
            "mode": "snapshot",
            "capabilities": ["snapshots", "community"],
            "source": "Discord API",
        }
        return {
            "resources": [resource],
            "snapshot": {
                "members": count,
                "online": guild.get("approximate_presence_count"),
                "channels": len(channels),
                "kind": "observed_snapshot",
                "source": "Discord API",
            },
            "contents": [],
            "warnings": [
                "Este conector coleta snapshots do servidor. Mensagens, atividade histórica e moderação não estão implementadas."
            ],
            "sync_seconds": 3600,
        }
