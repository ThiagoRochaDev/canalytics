import asyncio
import logging
import time

from .connectors import CONNECTORS
from .connectors.base import ProviderError, now_iso
from .oauth import fresh_credentials


def run_job(store, job):
    connection = store.one(
        "SELECT * FROM connections WHERE id=? AND workspace_id=?",
        (job["connection_id"], job["workspace_id"]),
    )
    if not connection:
        return
    try:
        credentials, app = fresh_credentials(store, connection)
        result = CONNECTORS[connection["provider"]].pull(credentials, app)
        store.save_sync(connection, result, now_iso())
        store.execute(
            "UPDATE jobs SET status='success',finished=?,error=NULL WHERE id=?",
            (time.time(), job["id"]),
        )
    except Exception as exc:
        message = (
            str(exc)
            if isinstance(exc, ProviderError)
            else "Falha na coleta. Confira permissões e se o canal já está conectado."
        )
        transient = isinstance(exc, ProviderError) and exc.status in (
            429,
            500,
            502,
            503,
            504,
        )
        retry = transient and job["attempts"] < 3
        store.execute(
            "UPDATE jobs SET status=?,finished=?,error=? WHERE id=?",
            ("pending" if retry else "error", time.time(), message, job["id"]),
        )
        store.execute(
            "UPDATE connections SET status='error',error=?,next_sync=? WHERE id=?",
            (message, time.time() + (120 if retry else 3600), connection["id"]),
        )


async def worker(store):
    store.execute("UPDATE jobs SET status='pending' WHERE status='running'")
    while True:
        try:
            now = time.time()
            for conn in store.all(
                "SELECT id,workspace_id FROM connections WHERE next_sync<=?", (now,)
            ):
                store.enqueue(conn["workspace_id"], conn["id"])
            with store.db() as db:
                db.execute("BEGIN IMMEDIATE")
                row = db.execute(
                    "SELECT j.* FROM jobs j JOIN connections c ON c.id=j.connection_id WHERE j.status='pending' AND (j.attempts=0 OR c.next_sync<=?) ORDER BY j.created LIMIT 1",
                    (now,),
                ).fetchone()
                job = dict(row) if row else None
                if job:
                    db.execute(
                        "UPDATE jobs SET status='running',started=?,attempts=attempts+1 WHERE id=?",
                        (now, job["id"]),
                    )
                    job["attempts"] += 1
            if job:
                await asyncio.to_thread(run_job, store, job)
                continue
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logging.getLogger("canalytics.worker").error(
                "Scheduler error (%s)", type(exc).__name__
            )
        await asyncio.sleep(10)
