from __future__ import annotations

import sqlite3
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Delivery:
    delivery_id: str
    body_digest: str
    repository: str
    issue_number: int
    event: str
    action: str
    accepted_at: str


class WorkflowStore:
    def __init__(self, database_path: Path) -> None:
        self._connection = sqlite3.connect(database_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = threading.RLock()
        self._setup()

    def _setup(self) -> None:
        with self._lock, self._connection:
            self._connection.executescript(
                """
                PRAGMA journal_mode=WAL;
                PRAGMA foreign_keys=ON;

                CREATE TABLE IF NOT EXISTS inbox_deliveries (
                    delivery_id TEXT PRIMARY KEY,
                    body_digest TEXT NOT NULL,
                    repository TEXT NOT NULL,
                    issue_number INTEGER NOT NULL,
                    event TEXT NOT NULL,
                    action TEXT NOT NULL,
                    accepted_at TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'accepted'
                        CHECK (status IN ('accepted', 'dispatched', 'ignored', 'failed'))
                );

                CREATE TABLE IF NOT EXISTS issue_runs (
                    run_id TEXT PRIMARY KEY,
                    repository TEXT NOT NULL,
                    issue_number INTEGER NOT NULL,
                    delivery_id TEXT NOT NULL UNIQUE
                        REFERENCES inbox_deliveries(delivery_id),
                    status TEXT NOT NULL CHECK (status IN ('running', 'paused', 'completed')),
                    created_at TEXT NOT NULL,
                    UNIQUE (repository, issue_number)
                );

                CREATE UNIQUE INDEX IF NOT EXISTS one_running_issue_per_repository
                    ON issue_runs(repository)
                    WHERE status = 'running';

                CREATE TABLE IF NOT EXISTS claim_projections (
                    run_id TEXT PRIMARY KEY REFERENCES issue_runs(run_id),
                    label TEXT NOT NULL,
                    projected_at TEXT NOT NULL
                );
                """
            )

    def accept(self, delivery: Delivery) -> str:
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                existing = self._connection.execute(
                    "SELECT body_digest FROM inbox_deliveries WHERE delivery_id = ?",
                    (delivery.delivery_id,),
                ).fetchone()
                if existing is not None:
                    self._connection.commit()
                    return "duplicate" if existing["body_digest"] == delivery.body_digest else "conflict"

                self._connection.execute(
                    """
                    INSERT INTO inbox_deliveries (
                        delivery_id, body_digest, repository, issue_number,
                        event, action, accepted_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        delivery.delivery_id,
                        delivery.body_digest,
                        delivery.repository,
                        delivery.issue_number,
                        delivery.event,
                        delivery.action,
                        delivery.accepted_at,
                    ),
                )
                self._connection.commit()
                return "accepted"
            except Exception:
                self._connection.rollback()
                raise

    def workflow_delivery(self, repository: str, issue_number: int) -> dict[str, str] | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT delivery_id, status, accepted_at, event, action
                FROM inbox_deliveries
                WHERE repository = ? AND issue_number = ?
                ORDER BY accepted_at DESC
                LIMIT 1
                """,
                (repository, issue_number),
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row["delivery_id"],
            "status": row["status"],
            "accepted_at": row["accepted_at"],
            "event": row["event"],
            "action": row["action"],
        }

    def claim_run(self, delivery: Delivery, *, created_at: str) -> dict[str, object] | None:
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                existing = self._connection.execute(
                    """
                    SELECT run_id, repository, issue_number, status, created_at
                    FROM issue_runs
                    WHERE repository = ? AND issue_number = ?
                    """,
                    (delivery.repository, delivery.issue_number),
                ).fetchone()
                if existing is not None:
                    self._connection.commit()
                    return self._run_dict(existing, created=False)

                active = self._connection.execute(
                    "SELECT 1 FROM issue_runs WHERE repository = ? AND status = 'running'",
                    (delivery.repository,),
                ).fetchone()
                if active is not None:
                    self._connection.commit()
                    return None

                run_id = str(uuid.uuid4())
                self._connection.execute(
                    """
                    INSERT INTO issue_runs (
                        run_id, repository, issue_number, delivery_id, status, created_at
                    ) VALUES (?, ?, ?, ?, 'running', ?)
                    """,
                    (
                        run_id,
                        delivery.repository,
                        delivery.issue_number,
                        delivery.delivery_id,
                        created_at,
                    ),
                )
                row = self._connection.execute(
                    """
                    SELECT run_id, repository, issue_number, status, created_at
                    FROM issue_runs WHERE run_id = ?
                    """,
                    (run_id,),
                ).fetchone()
                self._connection.commit()
                return self._run_dict(row, created=True)
            except sqlite3.IntegrityError:
                self._connection.rollback()
                return None
            except Exception:
                self._connection.rollback()
                raise

    @staticmethod
    def _run_dict(row: sqlite3.Row, *, created: bool) -> dict[str, object]:
        return {
            "id": row["run_id"],
            "repository": row["repository"],
            "issue_number": row["issue_number"],
            "status": row["status"],
            "created_at": row["created_at"],
            "created": created,
        }

    def run_id_for_issue(self, repository: str, issue_number: int) -> str:
        with self._lock:
            row = self._connection.execute(
                "SELECT run_id FROM issue_runs WHERE repository = ? AND issue_number = ?",
                (repository, issue_number),
            ).fetchone()
        if row is None:
            raise LookupError("run not found")
        return str(row["run_id"])

    def record_claim(self, *, run_id: str, label: str, projected_at: str) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO claim_projections (run_id, label, projected_at)
                VALUES (?, ?, ?)
                ON CONFLICT(run_id) DO NOTHING
                """,
                (run_id, label, projected_at),
            )

    def workflow_run(self, repository: str, issue_number: int) -> dict[str, object] | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT run_id, repository, issue_number, status, created_at
                FROM issue_runs
                WHERE repository = ? AND issue_number = ?
                """,
                (repository, issue_number),
            ).fetchone()
        if row is None:
            return None
        run = self._run_dict(row, created=False)
        run.pop("created")
        return run

    def workflow_claim(self, run_id: str) -> dict[str, str] | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT label, projected_at FROM claim_projections WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return {"label": row["label"], "projected_at": row["projected_at"]}

    def close(self) -> None:
        with self._lock:
            self._connection.close()
