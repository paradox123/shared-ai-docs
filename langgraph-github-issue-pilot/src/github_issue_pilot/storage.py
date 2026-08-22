from __future__ import annotations

import json
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

                CREATE TABLE IF NOT EXISTS implementation_executions (
                    run_id TEXT PRIMARY KEY REFERENCES issue_runs(run_id),
                    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'failed')),
                    assignment_json TEXT NOT NULL,
                    worktree_path TEXT NOT NULL,
                    branch TEXT NOT NULL,
                    base_ref TEXT NOT NULL,
                    policy_version TEXT NOT NULL,
                    model TEXT NOT NULL,
                    reasoning_effort TEXT NOT NULL,
                    skills_json TEXT NOT NULL,
                    access_profile_json TEXT NOT NULL,
                    diagnostic_events_json TEXT,
                    result_json TEXT,
                    error TEXT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT
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

    def prepare_implementation(
        self,
        *,
        run_id: str,
        assignment: dict[str, object],
        worktree_path: str,
        branch: str,
        base_ref: str,
        policy_version: str,
        model: str,
        reasoning_effort: str,
        skills: list[dict[str, str]],
        access_profile: dict[str, object],
        started_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO implementation_executions (
                    run_id, status, assignment_json, worktree_path, branch, base_ref,
                    policy_version, model, reasoning_effort, skills_json,
                    access_profile_json, started_at
                ) VALUES (?, 'running', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id) DO NOTHING
                """,
                (
                    run_id,
                    json.dumps(assignment, sort_keys=True),
                    worktree_path,
                    branch,
                    base_ref,
                    policy_version,
                    model,
                    reasoning_effort,
                    json.dumps(skills, sort_keys=True),
                    json.dumps(access_profile, sort_keys=True),
                    started_at,
                ),
            )

    def workflow_implementation(self, run_id: str) -> dict[str, object] | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT status, assignment_json, worktree_path, branch, base_ref,
                       policy_version, model, reasoning_effort, skills_json,
                       access_profile_json, diagnostic_events_json, result_json,
                       error, started_at, completed_at
                FROM implementation_executions WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "status": row["status"],
            "assignment": json.loads(row["assignment_json"]),
            "worktree": {
                "path": row["worktree_path"],
                "branch": row["branch"],
                "base_ref": row["base_ref"],
            },
            "policy": {
                "version": row["policy_version"],
                "model": row["model"],
                "reasoning_effort": row["reasoning_effort"],
            },
            "skills": json.loads(row["skills_json"]),
            "access_profile": json.loads(row["access_profile_json"]),
            "diagnostic_events": (
                json.loads(row["diagnostic_events_json"])
                if row["diagnostic_events_json"] is not None
                else []
            ),
            "result": json.loads(row["result_json"]) if row["result_json"] is not None else None,
            "error": row["error"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
        }

    def complete_implementation(
        self,
        *,
        run_id: str,
        result: dict[str, object],
        diagnostic_events: list[dict[str, object]],
        completed_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE implementation_executions
                SET status = 'completed', result_json = ?, diagnostic_events_json = ?,
                    error = NULL, completed_at = ?
                WHERE run_id = ? AND status = 'running'
                """,
                (
                    json.dumps(result, sort_keys=True),
                    json.dumps(diagnostic_events, sort_keys=True),
                    completed_at,
                    run_id,
                ),
            )

    def fail_implementation(
        self,
        *,
        run_id: str,
        error: str,
        diagnostic_events: list[dict[str, object]],
        completed_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE implementation_executions
                SET status = 'failed', result_json = NULL, diagnostic_events_json = ?,
                    error = ?, completed_at = ?
                WHERE run_id = ? AND status = 'running'
                """,
                (
                    json.dumps(diagnostic_events, sort_keys=True),
                    error,
                    completed_at,
                    run_id,
                ),
            )

    def close(self) -> None:
        with self._lock:
            self._connection.close()
