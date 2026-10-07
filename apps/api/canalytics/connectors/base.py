"""Public connector contract: independently testable, normalized, capability-driven."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

import httpx


class ProviderError(Exception):
    def __init__(self, message, status=502):
        super().__init__(message)
        self.status = status


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def date_window(days=180):
    end = datetime.now(timezone.utc).date() - timedelta(days=3)
    return str(end - timedelta(days=days - 1)), str(end)


def request(method, url, **kwargs):
    try:
        with httpx.Client(timeout=30, follow_redirects=False) as client:
            response = client.request(method, url, **kwargs)
        if response.status_code >= 400:
            messages = {
                401: "Autorização expirada ou revogada. Reconecte a conta.",
                403: "A plataforma recusou o acesso. Verifique escopos, elegibilidade e cota.",
                429: "Limite temporário da plataforma. A coleta será tentada novamente.",
            }
            raise ProviderError(
                messages.get(
                    response.status_code,
                    "A plataforma não concluiu a consulta (HTTP "
                    + str(response.status_code)
                    + ").",
                ),
                response.status_code,
            )
        return response.json() if response.content else {}
    except httpx.HTTPError as exc:
        raise ProviderError(
            "Não foi possível alcançar a plataforma. Tente novamente.", 503
        ) from exc


class Connector(ABC):
    id: str
    title: str

    @abstractmethod
    def pull(self, credentials: dict, app: dict) -> dict:
        """Return resources + optional daily/contents/snapshot/breakdowns.
        Never manufacture unavailable metrics or treat snapshots as interval reports.
        """
