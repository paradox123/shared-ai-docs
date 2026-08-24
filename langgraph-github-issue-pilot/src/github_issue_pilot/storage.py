from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

_STARTUP_RECONCILIATION_COLUMNS = """
    boot_id, status, outcome, previous_last_alive_at,
    started_at, completed_at, offline_seconds,
    discovered_commands, accepted_commands, deduplicated_commands
"""


@dataclass(frozen=True)
class Delivery:
    delivery_id: str
    body_digest: str
    repository: str
    issue_number: int
    event: str
    action: str
    accepted_at: str
    kind: str = "issue"
    pull_request_number: int | None = None
    actor_login: str | None = None
    feedback: tuple[str, ...] = ()
    head_sha: str | None = None
    merged: bool = False
    source_id: str | None = None
    command_key: str | None = None


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

                CREATE TABLE IF NOT EXISTS inbox_commands (
                    command_key TEXT PRIMARY KEY,
                    first_delivery_id TEXT NOT NULL UNIQUE
                        REFERENCES inbox_deliveries(delivery_id),
                    repository TEXT NOT NULL,
                    issue_number INTEGER NOT NULL,
                    kind TEXT NOT NULL,
                    accepted_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS runtime_liveness (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    last_alive_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS startup_reconciliations (
                    boot_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL CHECK (status IN ('running', 'completed', 'not_required')),
                    outcome TEXT NOT NULL CHECK (
                        outcome IN (
                            'first_start', 'below_threshold', 'clock_before_last_alive',
                            'threshold_reached'
                        )
                    ),
                    previous_last_alive_at TEXT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    offline_seconds INTEGER,
                    discovered_commands INTEGER NOT NULL DEFAULT 0,
                    accepted_commands INTEGER NOT NULL DEFAULT 0,
                    deduplicated_commands INTEGER NOT NULL DEFAULT 0
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

                CREATE TABLE IF NOT EXISTS candidate_dispositions (
                    repository TEXT NOT NULL,
                    issue_number INTEGER NOT NULL,
                    delivery_id TEXT NOT NULL REFERENCES inbox_deliveries(delivery_id),
                    status TEXT NOT NULL
                        CHECK (status IN ('queued', 'interrupted', 'selected', 'completed')),
                    reason TEXT,
                    issue_type TEXT NOT NULL,
                    evaluated_at TEXT NOT NULL,
                    PRIMARY KEY (repository, issue_number)
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

                CREATE TABLE IF NOT EXISTS draft_pr_publications (
                    run_id TEXT PRIMARY KEY REFERENCES issue_runs(run_id),
                    status TEXT NOT NULL CHECK (status IN ('publishing', 'published', 'rejected')),
                    evidence_json TEXT,
                    branch TEXT,
                    head_sha TEXT,
                    body TEXT,
                    pull_request_number INTEGER,
                    pull_request_url TEXT,
                    is_draft INTEGER,
                    reason TEXT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS review_batches (
                    batch_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES issue_runs(run_id),
                    head_sha TEXT NOT NULL,
                    pull_request_number INTEGER NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('running', 'blocked', 'verified')),
                    reason TEXT,
                    projected_labels_json TEXT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    UNIQUE (run_id, head_sha)
                );

                CREATE TABLE IF NOT EXISTS review_results (
                    batch_id TEXT NOT NULL REFERENCES review_batches(batch_id),
                    axis TEXT NOT NULL CHECK (axis IN ('requirements', 'code', 'architecture')),
                    assignment_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    policy_json TEXT NOT NULL,
                    route_axis TEXT NOT NULL,
                    skills_json TEXT NOT NULL,
                    access_profile_json TEXT NOT NULL,
                    diagnostic_events_json TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    PRIMARY KEY (batch_id, axis)
                );

                CREATE TABLE IF NOT EXISTS repair_batches (
                    repair_batch_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES issue_runs(run_id),
                    initial_review_batch_id TEXT NOT NULL UNIQUE
                        REFERENCES review_batches(batch_id),
                    round_limit INTEGER NOT NULL DEFAULT 3 CHECK (round_limit = 3),
                    status TEXT NOT NULL
                        CHECK (status IN ('running', 'verified', 'needs-info', 'ready-for-human')),
                    open_findings_json TEXT NOT NULL DEFAULT '[]',
                    projected_labels_json TEXT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS repair_attempts (
                    attempt_id TEXT PRIMARY KEY,
                    repair_batch_id TEXT NOT NULL REFERENCES repair_batches(repair_batch_id),
                    round_number INTEGER NOT NULL CHECK (round_number BETWEEN 1 AND 3),
                    status TEXT NOT NULL
                        CHECK (status IN ('running', 'unsuccessful', 'verified', 'blocked', 'failed')),
                    assignment_json TEXT NOT NULL,
                    head_sha TEXT,
                    deterministic_verification_json TEXT,
                    review_batch_id TEXT REFERENCES review_batches(batch_id),
                    remaining_findings_json TEXT NOT NULL DEFAULT '[]',
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    UNIQUE (repair_batch_id, round_number)
                );

                CREATE TABLE IF NOT EXISTS repair_invocations (
                    attempt_id TEXT NOT NULL REFERENCES repair_attempts(attempt_id),
                    invocation_number INTEGER NOT NULL CHECK (invocation_number >= 1),
                    policy_json TEXT NOT NULL,
                    skills_json TEXT NOT NULL,
                    access_profile_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    diagnostic_events_json TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    PRIMARY KEY (attempt_id, invocation_number)
                );

                CREATE TABLE IF NOT EXISTS human_feedback_batches (
                    feedback_batch_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES issue_runs(run_id),
                    delivery_id TEXT NOT NULL UNIQUE REFERENCES inbox_deliveries(delivery_id),
                    pull_request_number INTEGER NOT NULL,
                    starting_head_sha TEXT NOT NULL,
                    author TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    feedback_json TEXT NOT NULL,
                    superseded_evidence_json TEXT NOT NULL DEFAULT '[]',
                    superseded_review_batch_id TEXT,
                    round_limit INTEGER NOT NULL DEFAULT 3 CHECK (round_limit = 3),
                    status TEXT NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'running', 'verified', 'needs-info', 'ready-for-human')),
                    projected_labels_json TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT
                );

                CREATE TABLE IF NOT EXISTS human_feedback_attempts (
                    attempt_id TEXT PRIMARY KEY,
                    feedback_batch_id TEXT NOT NULL
                        REFERENCES human_feedback_batches(feedback_batch_id),
                    round_number INTEGER NOT NULL CHECK (round_number BETWEEN 1 AND 3),
                    status TEXT NOT NULL
                        CHECK (status IN ('running', 'unsuccessful', 'verified', 'blocked', 'failed')),
                    assignment_json TEXT NOT NULL,
                    result_json TEXT,
                    head_sha TEXT,
                    evidence_json TEXT,
                    deterministic_verification_json TEXT,
                    review_batch_id TEXT REFERENCES review_batches(batch_id),
                    projected_labels_json TEXT,
                    invalidation_labels_json TEXT,
                    policy_json TEXT,
                    skills_json TEXT,
                    access_profile_json TEXT,
                    diagnostic_events_json TEXT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    UNIQUE (feedback_batch_id, round_number)
                );

                CREATE TABLE IF NOT EXISTS interventions (
                    intervention_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES issue_runs(run_id),
                    phase TEXT NOT NULL CHECK (phase IN ('implementation', 'review', 'repair')),
                    role TEXT NOT NULL CHECK (
                        role IN (
                            'implementer', 'requirements_reviewer', 'code_reviewer',
                            'architecture_reviewer', 'repairer'
                        )
                    ),
                    operation_key TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL CHECK (
                        status IN (
                            'pending_delivery', 'open', 'delivery_blocked',
                            'answered', 'applying', 'applied'
                        )
                    ),
                    request_json TEXT NOT NULL,
                    source_result_json TEXT NOT NULL,
                    codex_thread_id TEXT UNIQUE,
                    delivery_turn_id TEXT,
                    answer_turn_id TEXT UNIQUE,
                    answer_text TEXT,
                    delivery_error TEXT,
                    created_at TEXT NOT NULL,
                    delivered_at TEXT,
                    answered_at TEXT,
                    applied_at TEXT
                );

                CREATE TABLE IF NOT EXISTS run_completions (
                    run_id TEXT PRIMARY KEY REFERENCES issue_runs(run_id),
                    delivery_id TEXT NOT NULL UNIQUE REFERENCES inbox_deliveries(delivery_id),
                    reason TEXT NOT NULL CHECK (reason = 'human-merged'),
                    pull_request_number INTEGER NOT NULL,
                    head_sha TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    completed_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS recovery_events (
                    event_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL REFERENCES issue_runs(run_id),
                    phase TEXT NOT NULL CHECK (
                        phase IN (
                            'claim', 'implementation', 'publication', 'review',
                            'repair', 'human_feedback', 'waiting'
                        )
                    ),
                    operation_key TEXT NOT NULL,
                    outcome TEXT NOT NULL CHECK (
                        outcome IN ('completed', 'reused', 'retried', 'waiting', 'failed')
                    ),
                    recorded_at TEXT NOT NULL,
                    UNIQUE (run_id, phase, operation_key)
                );
                """
            )

    def begin_startup_reconciliation(
        self,
        *,
        boot_id: str,
        now: datetime,
        threshold_seconds: int,
    ) -> tuple[dict[str, object], bool]:
        if not boot_id or len(boot_id) > 200:
            raise ValueError("boot session id must contain 1 to 200 characters")
        now_text = now.isoformat()
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                existing = self._startup_reconciliation_row(boot_id)
                if existing is not None:
                    self._write_liveness(now_text)
                    self._connection.commit()
                    return self._reconciliation_dict(existing), existing["status"] == "running"

                liveness = self._connection.execute(
                    "SELECT last_alive_at FROM runtime_liveness WHERE singleton = 1"
                ).fetchone()
                previous = str(liveness["last_alive_at"]) if liveness is not None else None
                outcome, status, offline_seconds = self._classify_startup(
                    previous=previous,
                    now=now,
                    threshold_seconds=threshold_seconds,
                )
                completed_at = now_text if status == "not_required" else None
                self._connection.execute(
                    """
                    INSERT INTO startup_reconciliations (
                        boot_id, status, outcome, previous_last_alive_at,
                        started_at, completed_at, offline_seconds
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        boot_id,
                        status,
                        outcome,
                        previous,
                        now_text,
                        completed_at,
                        offline_seconds,
                    ),
                )
                self._write_liveness(now_text)
                row = self._startup_reconciliation_row(boot_id)
                self._connection.commit()
                return self._reconciliation_dict(row), status == "running"
            except Exception:
                self._connection.rollback()
                raise

    def complete_startup_reconciliation(
        self,
        *,
        boot_id: str,
        completed_at: str,
        discovered_commands: int = 0,
        accepted_commands: int = 0,
        deduplicated_commands: int = 0,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE startup_reconciliations
                SET status = 'completed', completed_at = ?,
                    discovered_commands = ?, accepted_commands = ?,
                    deduplicated_commands = ?
                WHERE boot_id = ? AND status = 'running'
                """,
                (
                    completed_at,
                    discovered_commands,
                    accepted_commands,
                    deduplicated_commands,
                    boot_id,
                ),
            )

    def touch_liveness(self, alive_at: str) -> None:
        with self._lock, self._connection:
            self._write_liveness(alive_at)

    def latest_startup_reconciliation(self) -> dict[str, object] | None:
        with self._lock:
            row = self._connection.execute(
                f"""
                SELECT {_STARTUP_RECONCILIATION_COLUMNS}
                FROM startup_reconciliations ORDER BY rowid DESC LIMIT 1
                """
            ).fetchone()
            liveness = self._connection.execute(
                "SELECT last_alive_at FROM runtime_liveness WHERE singleton = 1"
            ).fetchone()
        if row is None:
            return None
        result = self._reconciliation_dict(row)
        result["last_alive_at"] = (
            str(liveness["last_alive_at"]) if liveness is not None else None
        )
        return result

    def _startup_reconciliation_row(self, boot_id: str) -> sqlite3.Row | None:
        return self._connection.execute(
            f"""
            SELECT {_STARTUP_RECONCILIATION_COLUMNS}
            FROM startup_reconciliations WHERE boot_id = ?
            """,
            (boot_id,),
        ).fetchone()

    def _write_liveness(self, alive_at: str) -> None:
        self._connection.execute(
            """
            INSERT INTO runtime_liveness (singleton, last_alive_at)
            VALUES (1, ?)
            ON CONFLICT(singleton) DO UPDATE SET last_alive_at = excluded.last_alive_at
            """,
            (alive_at,),
        )

    @staticmethod
    def _classify_startup(
        *,
        previous: str | None,
        now: datetime,
        threshold_seconds: int,
    ) -> tuple[str, str, int | None]:
        if previous is None:
            return "first_start", "not_required", None
        offline_seconds = int((now - datetime.fromisoformat(previous)).total_seconds())
        if offline_seconds < 0:
            return "clock_before_last_alive", "not_required", offline_seconds
        if offline_seconds < threshold_seconds:
            return "below_threshold", "not_required", offline_seconds
        return "threshold_reached", "running", offline_seconds

    @staticmethod
    def _reconciliation_dict(row: sqlite3.Row) -> dict[str, object]:
        return {
            "boot_id": row["boot_id"],
            "status": row["status"],
            "outcome": row["outcome"],
            "previous_last_alive_at": row["previous_last_alive_at"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
            "offline_seconds": row["offline_seconds"],
            "discovered_commands": row["discovered_commands"],
            "accepted_commands": row["accepted_commands"],
            "deduplicated_commands": row["deduplicated_commands"],
        }

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
                command_key = delivery.command_key or f"delivery:{delivery.delivery_id}"
                existing_command = self._connection.execute(
                    "SELECT 1 FROM inbox_commands WHERE command_key = ?",
                    (command_key,),
                ).fetchone()
                if existing_command is not None:
                    self._connection.execute(
                        "UPDATE inbox_deliveries SET status = 'ignored' WHERE delivery_id = ?",
                        (delivery.delivery_id,),
                    )
                    self._connection.commit()
                    return "command_duplicate"
                self._connection.execute(
                    """
                    INSERT INTO inbox_commands (
                        command_key, first_delivery_id, repository,
                        issue_number, kind, accepted_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        command_key,
                        delivery.delivery_id,
                        delivery.repository,
                        delivery.issue_number,
                        delivery.kind,
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
                SELECT d.delivery_id, d.status, d.accepted_at, d.event, d.action
                FROM candidate_dispositions AS c
                JOIN inbox_deliveries AS d ON d.delivery_id = c.delivery_id
                WHERE c.repository = ? AND c.issue_number = ?
                """,
                (repository, issue_number),
            ).fetchone()
            if row is None:
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

    def claim_run(
        self,
        delivery: Delivery,
        *,
        issue_number: int,
        created_at: str,
    ) -> dict[str, object] | None:
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                existing = self._connection.execute(
                    """
                    SELECT run_id, repository, issue_number, status, created_at
                    FROM issue_runs
                    WHERE repository = ? AND issue_number = ?
                    """,
                    (delivery.repository, issue_number),
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
                        issue_number,
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

    def active_run(self, repository: str) -> dict[str, object] | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT run_id, repository, issue_number, status, created_at
                FROM issue_runs
                WHERE repository = ? AND status = 'running'
                """,
                (repository,),
            ).fetchone()
        if row is None:
            return None
        run = self._run_dict(row, created=False)
        run.pop("created")
        return run

    def active_runs(self) -> list[dict[str, object]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT run_id, repository, issue_number, status, created_at
                FROM issue_runs
                WHERE status = 'running'
                ORDER BY created_at, run_id
                """
            ).fetchall()
        records: list[dict[str, object]] = []
        for row in rows:
            run = self._run_dict(row, created=False)
            run.pop("created")
            records.append(run)
        return records

    def record_recovery_event(
        self,
        *,
        run_id: str,
        phase: str,
        operation_key: str,
        outcome: str,
        recorded_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO recovery_events (
                    event_id, run_id, phase, operation_key, outcome, recorded_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(run_id, phase, operation_key) DO NOTHING
                """,
                (
                    str(uuid.uuid4()),
                    run_id,
                    phase,
                    operation_key,
                    outcome,
                    recorded_at,
                ),
            )

    def workflow_recovery(self, run_id: str) -> dict[str, object] | None:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT event_id, phase, operation_key, outcome, recorded_at
                FROM recovery_events
                WHERE run_id = ?
                ORDER BY rowid
                """,
                (run_id,),
            ).fetchall()
        if not rows:
            return None
        events = [
            {
                "id": row["event_id"],
                "phase": row["phase"],
                "operation_key": row["operation_key"],
                "outcome": row["outcome"],
                "recorded_at": row["recorded_at"],
            }
            for row in rows
        ]
        return {
            "status": (
                "failed" if any(event["outcome"] == "failed" for event in events) else "completed"
            ),
            "events": events,
        }

    def run_for_pull_request(
        self, repository: str, pull_request_number: int
    ) -> dict[str, object] | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT r.run_id, r.repository, r.issue_number, r.status, r.created_at
                FROM issue_runs AS r
                JOIN draft_pr_publications AS p ON p.run_id = r.run_id
                WHERE r.repository = ? AND p.pull_request_number = ?
                """,
                (repository, pull_request_number),
            ).fetchone()
        if row is None:
            return None
        run = self._run_dict(row, created=False)
        run.pop("created")
        return run

    def complete_run(self, run_id: str) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                "UPDATE issue_runs SET status = 'completed' WHERE run_id = ? AND status = 'running'",
                (run_id,),
            )

    def complete_human_merge(
        self,
        *,
        run_id: str,
        delivery_id: str,
        pull_request_number: int,
        head_sha: str,
        actor: str,
        completed_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                "UPDATE issue_runs SET status = 'completed' WHERE run_id = ? AND status = 'running'",
                (run_id,),
            )
            self._connection.execute(
                """
                INSERT INTO run_completions (
                    run_id, delivery_id, reason, pull_request_number,
                    head_sha, actor, completed_at
                ) VALUES (?, ?, 'human-merged', ?, ?, ?, ?)
                ON CONFLICT(run_id) DO NOTHING
                """,
                (
                    run_id,
                    delivery_id,
                    pull_request_number,
                    head_sha,
                    actor,
                    completed_at,
                ),
            )

    def workflow_completion(self, run_id: str) -> dict[str, object] | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT delivery_id, reason, pull_request_number, head_sha, actor, completed_at
                FROM run_completions WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "reason": row["reason"],
            "delivery_id": row["delivery_id"],
            "pull_request_number": row["pull_request_number"],
            "head_sha": row["head_sha"],
            "actor": row["actor"],
            "completed_at": row["completed_at"],
        }

    def workflow_claim(self, run_id: str) -> dict[str, str] | None:
        with self._lock:
            row = self._connection.execute(
                "SELECT label, projected_at FROM claim_projections WHERE run_id = ?",
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        return {"label": row["label"], "projected_at": row["projected_at"]}

    def record_disposition(
        self,
        delivery: Delivery,
        *,
        issue_number: int,
        status: str,
        reason: str | None,
        issue_type: str,
        evaluated_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO candidate_dispositions (
                    repository, issue_number, delivery_id, status, reason,
                    issue_type, evaluated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(repository, issue_number) DO UPDATE SET
                    delivery_id = excluded.delivery_id,
                    status = excluded.status,
                    reason = excluded.reason,
                    issue_type = excluded.issue_type,
                    evaluated_at = excluded.evaluated_at
                """,
                (
                    delivery.repository,
                    issue_number,
                    delivery.delivery_id,
                    status,
                    reason,
                    issue_type,
                    evaluated_at,
                ),
            )

    def workflow_disposition(self, repository: str, issue_number: int) -> dict[str, str | None] | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT status, reason, issue_type, evaluated_at
                FROM candidate_dispositions
                WHERE repository = ? AND issue_number = ?
                """,
                (repository, issue_number),
            ).fetchone()
        if row is None:
            return None
        return {
            "status": row["status"],
            "reason": row["reason"],
            "issue_type": row["issue_type"],
            "evaluated_at": row["evaluated_at"],
        }

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

    def complete_implementation_with_intervention(
        self,
        *,
        run_id: str,
        result: dict[str, object],
        diagnostic_events: list[dict[str, object]],
        phase: str,
        role: str,
        operation_key: str,
        request: dict[str, object],
        completed_at: str,
    ) -> str:
        result_json = json.dumps(result, sort_keys=True)
        diagnostics_json = json.dumps(diagnostic_events, sort_keys=True)
        request_json = json.dumps(request, sort_keys=True)
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                self._connection.execute(
                    """
                    UPDATE implementation_executions
                    SET status = 'completed', result_json = ?, diagnostic_events_json = ?,
                        error = NULL, completed_at = ?
                    WHERE run_id = ? AND status = 'running'
                    """,
                    (result_json, diagnostics_json, completed_at, run_id),
                )
                intervention_id = str(uuid.uuid4())
                self._connection.execute(
                    """
                    INSERT INTO interventions (
                        intervention_id, run_id, phase, role, operation_key, status,
                        request_json, source_result_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, 'pending_delivery', ?, ?, ?)
                    ON CONFLICT(operation_key) DO NOTHING
                    """,
                    (
                        intervention_id,
                        run_id,
                        phase,
                        role,
                        operation_key,
                        request_json,
                        result_json,
                        completed_at,
                    ),
                )
                row = self._connection.execute(
                    """
                    SELECT intervention_id, run_id, phase, role, request_json,
                           source_result_json
                    FROM interventions WHERE operation_key = ?
                    """,
                    (operation_key,),
                ).fetchone()
                if row is None or (
                    row["run_id"] != run_id
                    or row["phase"] != phase
                    or row["role"] != role
                    or row["request_json"] != request_json
                    or row["source_result_json"] != result_json
                ):
                    raise RuntimeError(
                        "intervention operation identity was reused with different content"
                    )
                self._connection.commit()
                return str(row["intervention_id"])
            except Exception:
                self._connection.rollback()
                raise

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

    def reject_publication(self, *, run_id: str, reason: str, rejected_at: str) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO draft_pr_publications (
                    run_id, status, reason, started_at, completed_at
                ) VALUES (?, 'rejected', ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    status = 'rejected', reason = excluded.reason,
                    completed_at = excluded.completed_at
                WHERE draft_pr_publications.status != 'published'
                """,
                (run_id, reason, rejected_at, rejected_at),
            )

    def begin_publication(
        self,
        *,
        run_id: str,
        evidence: list[dict[str, object]],
        branch: str,
        started_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO draft_pr_publications (
                    run_id, status, evidence_json, branch, started_at
                ) VALUES (?, 'publishing', ?, ?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    evidence_json = excluded.evidence_json,
                    branch = excluded.branch
                WHERE draft_pr_publications.status = 'publishing'
                """,
                (run_id, json.dumps(evidence, sort_keys=True), branch, started_at),
            )

    def complete_publication(
        self,
        *,
        run_id: str,
        branch: str,
        head_sha: str,
        body: str,
        pull_request_number: int,
        pull_request_url: str,
        completed_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE draft_pr_publications
                SET status = 'published', branch = ?, head_sha = ?, body = ?,
                    pull_request_number = ?, pull_request_url = ?, is_draft = 1,
                    reason = NULL, completed_at = ?
                WHERE run_id = ? AND status = 'publishing'
                """,
                (
                    branch,
                    head_sha,
                    body,
                    pull_request_number,
                    pull_request_url,
                    completed_at,
                    run_id,
                ),
            )

    def update_publication(
        self,
        *,
        run_id: str,
        evidence: list[dict[str, object]],
        head_sha: str,
        body: str,
        completed_at: str,
    ) -> None:
        with self._lock, self._connection:
            cursor = self._connection.execute(
                """
                UPDATE draft_pr_publications
                SET evidence_json = ?, head_sha = ?, body = ?, reason = NULL,
                    completed_at = ?
                WHERE run_id = ? AND status = 'published'
                """,
                (
                    json.dumps(evidence, sort_keys=True),
                    head_sha,
                    body,
                    completed_at,
                    run_id,
                ),
            )
        if cursor.rowcount != 1:
            raise RuntimeError("published draft pull request could not be updated")

    def workflow_publication(self, run_id: str) -> dict[str, object] | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT status, evidence_json, branch, head_sha, body,
                       pull_request_number, pull_request_url, is_draft,
                       reason, started_at, completed_at
                FROM draft_pr_publications WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
        if row is None:
            return None
        pull_request = None
        if row["pull_request_number"] is not None:
            pull_request = {
                "number": row["pull_request_number"],
                "url": row["pull_request_url"],
                "draft": bool(row["is_draft"]),
            }
        return {
            "status": row["status"],
            "evidence": json.loads(row["evidence_json"]) if row["evidence_json"] else [],
            "branch": row["branch"],
            "head_sha": row["head_sha"],
            "body": row["body"],
            "pull_request": pull_request,
            "reason": row["reason"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
        }

    def begin_review_batch(
        self,
        *,
        run_id: str,
        head_sha: str,
        pull_request_number: int,
        started_at: str,
    ) -> str:
        with self._lock, self._connection:
            batch_id = str(uuid.uuid4())
            self._connection.execute(
                """
                INSERT INTO review_batches (
                    batch_id, run_id, head_sha, pull_request_number, status, started_at
                ) VALUES (?, ?, ?, ?, 'running', ?)
                ON CONFLICT(run_id, head_sha) DO NOTHING
                """,
                (batch_id, run_id, head_sha, pull_request_number, started_at),
            )
            row = self._connection.execute(
                "SELECT batch_id FROM review_batches WHERE run_id = ? AND head_sha = ?",
                (run_id, head_sha),
            ).fetchone()
        if row is None:
            raise RuntimeError("review batch could not be created")
        return str(row["batch_id"])

    def record_review_result(
        self,
        *,
        batch_id: str,
        axis: str,
        assignment: dict[str, object],
        result: dict[str, object],
        policy: dict[str, object],
        route_axis: str,
        skills: list[dict[str, str]],
        access_profile: dict[str, object],
        diagnostic_events: list[dict[str, object]],
        completed_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO review_results (
                    batch_id, axis, assignment_json, result_json, policy_json,
                    route_axis, skills_json, access_profile_json,
                    diagnostic_events_json, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(batch_id, axis) DO NOTHING
                """,
                (
                    batch_id,
                    axis,
                    json.dumps(assignment, sort_keys=True),
                    json.dumps(result, sort_keys=True),
                    json.dumps(policy, sort_keys=True),
                    route_axis,
                    json.dumps(skills, sort_keys=True),
                    json.dumps(access_profile, sort_keys=True),
                    json.dumps(diagnostic_events, sort_keys=True),
                    completed_at,
                ),
            )

    def block_review_batch(self, *, batch_id: str, reason: str, completed_at: str) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE review_batches
                SET status = 'blocked', reason = ?, projected_labels_json = NULL,
                    completed_at = ?
                WHERE batch_id = ? AND status = 'running'
                """,
                (reason, completed_at, batch_id),
            )

    def complete_review_batch(
        self,
        *,
        batch_id: str,
        projected_labels: frozenset[str],
        completed_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE review_batches
                SET status = 'verified', reason = NULL, projected_labels_json = ?,
                    completed_at = ?
                WHERE batch_id = ? AND status = 'running'
                """,
                (json.dumps(sorted(projected_labels)), completed_at, batch_id),
            )

    def workflow_review(self, run_id: str) -> dict[str, object] | None:
        history = self.workflow_review_history(run_id)
        return history[-1] if history else None

    def workflow_review_history(self, run_id: str) -> list[dict[str, object]]:
        with self._lock:
            batches = self._connection.execute(
                """
                SELECT batch_id, status, head_sha, pull_request_number, reason,
                       projected_labels_json, started_at, completed_at
                FROM review_batches
                WHERE run_id = ?
                ORDER BY rowid
                """,
                (run_id,),
            ).fetchall()
            results = self._connection.execute(
                """
                SELECT batch_id, axis, assignment_json, result_json, policy_json,
                       route_axis, skills_json, access_profile_json,
                       diagnostic_events_json, completed_at
                FROM review_results
                WHERE batch_id IN (SELECT batch_id FROM review_batches WHERE run_id = ?)
                ORDER BY batch_id, CASE axis
                    WHEN 'requirements' THEN 1
                    WHEN 'code' THEN 2
                    WHEN 'architecture' THEN 3
                END
                """,
                (run_id,),
            ).fetchall()
        results_by_batch: dict[str, list[dict[str, object]]] = {}
        for row in results:
            results_by_batch.setdefault(str(row["batch_id"]), []).append(
                {
                    "axis": row["axis"],
                    "assignment": json.loads(row["assignment_json"]),
                    "verdict": json.loads(row["result_json"]),
                    "policy": json.loads(row["policy_json"]),
                    "route_axis": row["route_axis"],
                    "skills": json.loads(row["skills_json"]),
                    "access_profile": json.loads(row["access_profile_json"]),
                    "diagnostic_events": json.loads(row["diagnostic_events_json"]),
                    "completed_at": row["completed_at"],
                }
            )
        return [
            {
                "id": batch["batch_id"],
                "status": batch["status"],
                "head_sha": batch["head_sha"],
                "pull_request_number": batch["pull_request_number"],
                "reason": batch["reason"],
                "projected_labels": (
                    json.loads(batch["projected_labels_json"])
                    if batch["projected_labels_json"] is not None
                    else []
                ),
                "results": results_by_batch.get(str(batch["batch_id"]), []),
                "started_at": batch["started_at"],
                "completed_at": batch["completed_at"],
            }
            for batch in batches
        ]

    def begin_repair_batch(
        self,
        *,
        run_id: str,
        initial_review_batch_id: str,
        started_at: str,
    ) -> str:
        with self._lock, self._connection:
            repair_batch_id = str(uuid.uuid4())
            self._connection.execute(
                """
                INSERT INTO repair_batches (
                    repair_batch_id, run_id, initial_review_batch_id, status, started_at
                ) VALUES (?, ?, ?, 'running', ?)
                ON CONFLICT(initial_review_batch_id) DO NOTHING
                """,
                (repair_batch_id, run_id, initial_review_batch_id, started_at),
            )
            row = self._connection.execute(
                """
                SELECT repair_batch_id FROM repair_batches
                WHERE initial_review_batch_id = ?
                """,
                (initial_review_batch_id,),
            ).fetchone()
        if row is None:
            raise RuntimeError("repair batch could not be created")
        return str(row["repair_batch_id"])

    def begin_repair_attempt(
        self,
        *,
        repair_batch_id: str,
        round_number: int,
        assignment: dict[str, object],
        started_at: str,
    ) -> str:
        if round_number not in {1, 2, 3}:
            raise ValueError("repair round must be between one and three")
        with self._lock, self._connection:
            batch = self._connection.execute(
                "SELECT status FROM repair_batches WHERE repair_batch_id = ?",
                (repair_batch_id,),
            ).fetchone()
            if batch is None:
                raise LookupError("repair batch not found")
            if batch["status"] != "running":
                raise RuntimeError("terminal repair batch cannot start another attempt")
            attempt_id = str(uuid.uuid4())
            self._connection.execute(
                """
                INSERT INTO repair_attempts (
                    attempt_id, repair_batch_id, round_number, status,
                    assignment_json, started_at
                ) VALUES (?, ?, ?, 'running', ?, ?)
                ON CONFLICT(repair_batch_id, round_number) DO NOTHING
                """,
                (
                    attempt_id,
                    repair_batch_id,
                    round_number,
                    json.dumps(assignment, sort_keys=True),
                    started_at,
                ),
            )
            row = self._connection.execute(
                """
                SELECT attempt_id FROM repair_attempts
                WHERE repair_batch_id = ? AND round_number = ?
                """,
                (repair_batch_id, round_number),
            ).fetchone()
        if row is None:
            raise RuntimeError("repair attempt could not be created")
        return str(row["attempt_id"])

    def record_repair_invocation(
        self,
        *,
        attempt_id: str,
        invocation_number: int,
        policy: dict[str, object],
        skills: list[dict[str, str]],
        access_profile: dict[str, object],
        result: dict[str, object],
        diagnostic_events: list[dict[str, object]],
        started_at: str,
        completed_at: str,
    ) -> None:
        if invocation_number < 1:
            raise ValueError("repair invocation number must be positive")
        with self._lock, self._connection:
            self._connection.execute(
                """
                INSERT INTO repair_invocations (
                    attempt_id, invocation_number, policy_json, skills_json,
                    access_profile_json, result_json, diagnostic_events_json,
                    started_at, completed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(attempt_id, invocation_number) DO NOTHING
                """,
                (
                    attempt_id,
                    invocation_number,
                    json.dumps(policy, sort_keys=True),
                    json.dumps(skills, sort_keys=True),
                    json.dumps(access_profile, sort_keys=True),
                    json.dumps(result, sort_keys=True),
                    json.dumps(diagnostic_events, sort_keys=True),
                    started_at,
                    completed_at,
                ),
            )

    def complete_repair_attempt(
        self,
        *,
        attempt_id: str,
        status: str,
        head_sha: str | None,
        deterministic_verification: dict[str, object] | None,
        review_batch_id: str | None,
        remaining_findings: list[dict[str, object]],
        completed_at: str,
    ) -> None:
        if status not in {"unsuccessful", "verified", "blocked", "failed"}:
            raise ValueError("unsupported repair attempt status")
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE repair_attempts
                SET status = ?, head_sha = ?, deterministic_verification_json = ?,
                    review_batch_id = ?, remaining_findings_json = ?, completed_at = ?
                WHERE attempt_id = ? AND status = 'running'
                """,
                (
                    status,
                    head_sha,
                    (
                        json.dumps(deterministic_verification, sort_keys=True)
                        if deterministic_verification is not None
                        else None
                    ),
                    review_batch_id,
                    json.dumps(remaining_findings, sort_keys=True),
                    completed_at,
                    attempt_id,
                ),
            )

    def complete_repair_batch(
        self,
        *,
        repair_batch_id: str,
        status: str,
        open_findings: list[dict[str, object]],
        projected_labels: frozenset[str],
        completed_at: str,
    ) -> None:
        if status not in {"verified", "needs-info", "ready-for-human"}:
            raise ValueError("unsupported terminal repair status")
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE repair_batches
                SET status = ?, open_findings_json = ?, projected_labels_json = ?,
                    completed_at = ?
                WHERE repair_batch_id = ? AND status = 'running'
                """,
                (
                    status,
                    json.dumps(open_findings, sort_keys=True),
                    json.dumps(sorted(projected_labels)),
                    completed_at,
                    repair_batch_id,
                ),
            )

    def workflow_repair(self, run_id: str) -> dict[str, object] | None:
        with self._lock:
            batch = self._connection.execute(
                """
                SELECT repair_batch_id, initial_review_batch_id, round_limit, status,
                       open_findings_json, projected_labels_json, started_at, completed_at
                FROM repair_batches
                WHERE run_id = ?
                ORDER BY started_at DESC, repair_batch_id DESC
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
            if batch is None:
                return None
            attempts = self._connection.execute(
                """
                SELECT attempt_id, round_number, status, assignment_json, head_sha,
                       deterministic_verification_json, review_batch_id,
                       remaining_findings_json, started_at, completed_at
                FROM repair_attempts
                WHERE repair_batch_id = ?
                ORDER BY round_number
                """,
                (batch["repair_batch_id"],),
            ).fetchall()
            invocation_rows = self._connection.execute(
                """
                SELECT attempt_id, invocation_number, policy_json, skills_json,
                       access_profile_json, result_json, diagnostic_events_json,
                       started_at, completed_at
                FROM repair_invocations
                WHERE attempt_id IN (
                    SELECT attempt_id FROM repair_attempts WHERE repair_batch_id = ?
                )
                ORDER BY attempt_id, invocation_number
                """,
                (batch["repair_batch_id"],),
            ).fetchall()
        invocations_by_attempt: dict[str, list[dict[str, object]]] = {}
        for row in invocation_rows:
            invocations_by_attempt.setdefault(str(row["attempt_id"]), []).append(
                {
                    "number": row["invocation_number"],
                    "policy": json.loads(row["policy_json"]),
                    "skills": json.loads(row["skills_json"]),
                    "access_profile": json.loads(row["access_profile_json"]),
                    "result": json.loads(row["result_json"]),
                    "diagnostic_events": json.loads(row["diagnostic_events_json"]),
                    "started_at": row["started_at"],
                    "completed_at": row["completed_at"],
                }
            )
        attempt_records = [
            {
                "id": row["attempt_id"],
                "round": row["round_number"],
                "status": row["status"],
                "assignment": json.loads(row["assignment_json"]),
                "head_sha": row["head_sha"],
                "deterministic_verification": (
                    json.loads(row["deterministic_verification_json"])
                    if row["deterministic_verification_json"] is not None
                    else None
                ),
                "review_batch_id": row["review_batch_id"],
                "remaining_findings": json.loads(row["remaining_findings_json"]),
                "invocations": invocations_by_attempt.get(str(row["attempt_id"]), []),
                "started_at": row["started_at"],
                "completed_at": row["completed_at"],
            }
            for row in attempts
        ]
        return {
            "id": batch["repair_batch_id"],
            "initial_review_batch_id": batch["initial_review_batch_id"],
            "round_limit": batch["round_limit"],
            "round_count": len(attempt_records),
            "status": batch["status"],
            "open_findings": json.loads(batch["open_findings_json"]),
            "projected_labels": (
                json.loads(batch["projected_labels_json"])
                if batch["projected_labels_json"] is not None
                else []
            ),
            "attempts": attempt_records,
            "started_at": batch["started_at"],
            "completed_at": batch["completed_at"],
        }

    def begin_intervention(
        self,
        *,
        run_id: str,
        phase: str,
        role: str,
        operation_key: str,
        request: dict[str, object],
        source_result: dict[str, object],
        created_at: str,
    ) -> str:
        request_json = json.dumps(request, sort_keys=True)
        source_result_json = json.dumps(source_result, sort_keys=True)
        with self._lock, self._connection:
            intervention_id = str(uuid.uuid4())
            self._connection.execute(
                """
                INSERT INTO interventions (
                    intervention_id, run_id, phase, role, operation_key, status,
                    request_json, source_result_json, created_at
                ) VALUES (?, ?, ?, ?, ?, 'pending_delivery', ?, ?, ?)
                ON CONFLICT(operation_key) DO NOTHING
                """,
                (
                    intervention_id,
                    run_id,
                    phase,
                    role,
                    operation_key,
                    request_json,
                    source_result_json,
                    created_at,
                ),
            )
            row = self._connection.execute(
                """
                SELECT intervention_id, run_id, phase, role, request_json, source_result_json
                FROM interventions WHERE operation_key = ?
                """,
                (operation_key,),
            ).fetchone()
        if row is None:
            raise RuntimeError("intervention could not be persisted")
        if (
            row["run_id"] != run_id
            or row["phase"] != phase
            or row["role"] != role
            or row["request_json"] != request_json
            or row["source_result_json"] != source_result_json
        ):
            raise RuntimeError("intervention operation identity was reused with different content")
        return str(row["intervention_id"])

    def workflow_interventions(self, run_id: str) -> dict[str, object]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT intervention_id, phase, role, operation_key, status,
                       request_json, codex_thread_id, delivery_turn_id,
                       answer_turn_id, answer_text, delivery_error,
                       created_at, delivered_at, answered_at, applied_at
                FROM interventions
                WHERE run_id = ?
                ORDER BY rowid
                """,
                (run_id,),
            ).fetchall()
        requests = [
            {
                "id": row["intervention_id"],
                "phase": row["phase"],
                "role": row["role"],
                "operation_key": row["operation_key"],
                "status": row["status"],
                "request": json.loads(row["request_json"]),
                "session": (
                    {
                        "thread_id": row["codex_thread_id"],
                        "delivery_turn_id": row["delivery_turn_id"],
                    }
                    if row["codex_thread_id"] is not None
                    else None
                ),
                "answer": (
                    {
                        "turn_id": row["answer_turn_id"],
                        "text": row["answer_text"],
                    }
                    if row["answer_turn_id"] is not None
                    else None
                ),
                "delivery_error": row["delivery_error"],
                "created_at": row["created_at"],
                "delivered_at": row["delivered_at"],
                "answered_at": row["answered_at"],
                "applied_at": row["applied_at"],
            }
            for row in rows
        ]
        return {
            "status": (
                "waiting"
                if any(
                    request["status"]
                    in {"pending_delivery", "open", "answered", "applying"}
                    for request in requests
                )
                else (
                    "delivery_blocked"
                    if any(request["status"] == "delivery_blocked" for request in requests)
                    else "idle"
                )
            ),
            "requests": requests,
        }

    def run_has_pending_intervention(self, run_id: str) -> bool:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT 1 FROM interventions
                WHERE run_id = ? AND status IN (
                    'pending_delivery', 'open', 'answered', 'applying'
                )
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
        return row is not None

    def complete_intervention_delivery(
        self,
        *,
        intervention_id: str,
        thread_id: str,
        delivery_turn_id: str,
        delivered_at: str,
    ) -> None:
        if not thread_id or not delivery_turn_id:
            raise ValueError("intervention session identities must be non-empty")
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                row = self._connection.execute(
                    """
                    SELECT status, codex_thread_id, delivery_turn_id
                    FROM interventions WHERE intervention_id = ?
                    """,
                    (intervention_id,),
                ).fetchone()
                if row is None:
                    raise LookupError("intervention not found")
                if row["codex_thread_id"] is not None:
                    if (
                        row["codex_thread_id"] != thread_id
                        or row["delivery_turn_id"] != delivery_turn_id
                    ):
                        raise RuntimeError(
                            "intervention delivery was already completed with a different session"
                        )
                    self._connection.commit()
                    return
                if row["status"] != "pending_delivery":
                    raise RuntimeError("intervention is not pending delivery")
                self._connection.execute(
                    """
                    UPDATE interventions
                    SET status = 'open', codex_thread_id = ?, delivery_turn_id = ?,
                        delivered_at = ?, delivery_error = NULL
                    WHERE intervention_id = ? AND status = 'pending_delivery'
                    """,
                    (thread_id, delivery_turn_id, delivered_at, intervention_id),
                )
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise

    def pending_intervention_deliveries(self) -> list[dict[str, object]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT intervention_id, run_id, request_json
                FROM interventions
                WHERE status = 'pending_delivery'
                ORDER BY rowid
                """
            ).fetchall()
        return [
            {
                "id": row["intervention_id"],
                "run_id": row["run_id"],
                "request": json.loads(row["request_json"]),
            }
            for row in rows
        ]

    def open_intervention_sessions(self) -> list[dict[str, str]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT intervention_id, codex_thread_id, delivery_turn_id
                FROM interventions
                WHERE status = 'open'
                ORDER BY rowid
                """
            ).fetchall()
        return [
            {
                "id": str(row["intervention_id"]),
                "thread_id": str(row["codex_thread_id"]),
                "delivery_turn_id": str(row["delivery_turn_id"]),
            }
            for row in rows
        ]

    def block_intervention_delivery(
        self,
        *,
        intervention_id: str,
        reason: str,
    ) -> None:
        if reason not in {
            "stable_surface_unavailable",
            "stable_surface_invalid_response",
            "stable_surface_turn_failed",
        }:
            reason = "stable_surface_unavailable"
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE interventions
                SET status = 'delivery_blocked', delivery_error = ?
                WHERE intervention_id = ? AND status = 'pending_delivery'
                """,
                (reason, intervention_id),
            )

    def capture_intervention_answer(
        self,
        *,
        intervention_id: str,
        answer_turn_id: str,
        answer_text: str,
        answered_at: str,
    ) -> bool:
        if not answer_turn_id or not answer_text.strip():
            raise ValueError("intervention answer identity and text must be non-empty")
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                row = self._connection.execute(
                    """
                    SELECT status, delivery_turn_id
                    FROM interventions WHERE intervention_id = ?
                    """,
                    (intervention_id,),
                ).fetchone()
                if row is None:
                    raise LookupError("intervention not found")
                if row["status"] != "open" or row["delivery_turn_id"] == answer_turn_id:
                    self._connection.commit()
                    return False
                updated = self._connection.execute(
                    """
                    UPDATE interventions
                    SET status = 'answered', answer_turn_id = ?, answer_text = ?,
                        answered_at = ?
                    WHERE intervention_id = ? AND status = 'open'
                    """,
                    (answer_turn_id, answer_text.strip(), answered_at, intervention_id),
                )
                self._connection.commit()
                return updated.rowcount == 1
            except sqlite3.IntegrityError:
                self._connection.rollback()
                return False
            except Exception:
                self._connection.rollback()
                raise

    def claim_intervention_application(self, intervention_id: str) -> bool:
        with self._lock, self._connection:
            updated = self._connection.execute(
                """
                UPDATE interventions SET status = 'applying'
                WHERE intervention_id = ? AND status = 'answered'
                """,
                (intervention_id,),
            )
        return updated.rowcount == 1

    def intervention_application_for_operation(
        self, operation_key: str
    ) -> dict[str, object] | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT intervention_id, run_id, status, answer_turn_id, answer_text
                FROM interventions WHERE operation_key = ?
                """,
                (operation_key,),
            ).fetchone()
        if row is None:
            return None
        return {
            "id": row["intervention_id"],
            "run_id": row["run_id"],
            "status": row["status"],
            "answer_turn_id": row["answer_turn_id"],
            "answer_text": row["answer_text"],
        }

    def interventions_for_application(self) -> list[dict[str, object]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT intervention_id, run_id, status, answer_turn_id, answer_text
                FROM interventions
                WHERE status IN ('answered', 'applying')
                ORDER BY rowid
                """
            ).fetchall()
        return [
            {
                "id": row["intervention_id"],
                "run_id": row["run_id"],
                "status": row["status"],
                "answer_turn_id": row["answer_turn_id"],
                "answer_text": row["answer_text"],
            }
            for row in rows
        ]

    def begin_implementation_continuation(
        self,
        *,
        run_id: str,
        intervention_id: str,
    ) -> None:
        with self._lock, self._connection:
            updated = self._connection.execute(
                """
                UPDATE implementation_executions
                SET status = 'running', completed_at = NULL
                WHERE run_id = ? AND status = 'completed'
                  AND EXISTS (
                      SELECT 1 FROM interventions
                      WHERE intervention_id = ? AND run_id = ?
                        AND phase = 'implementation' AND status = 'applying'
                  )
                """,
                (run_id, intervention_id, run_id),
            )
        if updated.rowcount != 1:
            current = self.workflow_implementation(run_id)
            if current is None or current["status"] != "running":
                raise RuntimeError("implementation continuation could not start")

    def complete_implementation_continuation(
        self,
        *,
        run_id: str,
        intervention_id: str,
        result: dict[str, object],
        diagnostic_events: list[dict[str, object]],
        completed_at: str,
    ) -> None:
        with self._lock:
            self._connection.execute("BEGIN IMMEDIATE")
            try:
                implementation = self._connection.execute(
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
                intervention = self._connection.execute(
                    """
                    UPDATE interventions SET status = 'applied', applied_at = ?
                    WHERE intervention_id = ? AND run_id = ? AND status = 'applying'
                    """,
                    (completed_at, intervention_id, run_id),
                )
                if implementation.rowcount != 1 or intervention.rowcount != 1:
                    raise RuntimeError("implementation continuation could not complete atomically")
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise

    def complete_intervention_application(
        self,
        *,
        intervention_id: str,
        applied_at: str,
    ) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE interventions
                SET status = 'applied', applied_at = ?
                WHERE intervention_id = ? AND status = 'applying'
                """,
                (applied_at, intervention_id),
            )

    def begin_feedback_batch(
        self,
        *,
        run_id: str,
        delivery_id: str,
        pull_request_number: int,
        starting_head_sha: str,
        author: str,
        source_id: str,
        feedback: tuple[str, ...],
        superseded_evidence: list[dict[str, object]],
        superseded_review_batch_id: str | None,
        created_at: str,
    ) -> str:
        with self._lock, self._connection:
            feedback_batch_id = str(uuid.uuid4())
            self._connection.execute(
                """
                INSERT INTO human_feedback_batches (
                    feedback_batch_id, run_id, delivery_id, pull_request_number,
                    starting_head_sha, author, source_id, feedback_json,
                    superseded_evidence_json, superseded_review_batch_id, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(delivery_id) DO NOTHING
                """,
                (
                    feedback_batch_id,
                    run_id,
                    delivery_id,
                    pull_request_number,
                    starting_head_sha,
                    author,
                    source_id,
                    json.dumps(list(feedback), sort_keys=True),
                    json.dumps(superseded_evidence, sort_keys=True),
                    superseded_review_batch_id,
                    created_at,
                ),
            )
            row = self._connection.execute(
                """
                SELECT feedback_batch_id FROM human_feedback_batches
                WHERE delivery_id = ?
                """,
                (delivery_id,),
            ).fetchone()
        if row is None:
            raise RuntimeError("human feedback batch could not be created")
        return str(row["feedback_batch_id"])

    def workflow_feedback(self, run_id: str) -> dict[str, object]:
        with self._lock:
            batches = self._connection.execute(
                """
                SELECT feedback_batch_id, delivery_id, pull_request_number,
                       starting_head_sha, author, source_id, feedback_json,
                       superseded_evidence_json, superseded_review_batch_id, round_limit,
                       status, projected_labels_json, created_at, completed_at
                FROM human_feedback_batches
                WHERE run_id = ?
                ORDER BY rowid
                """,
                (run_id,),
            ).fetchall()
            attempts = self._connection.execute(
                """
                SELECT attempt_id, feedback_batch_id, round_number, status,
                       assignment_json, result_json, head_sha, evidence_json,
                       deterministic_verification_json, review_batch_id,
                       projected_labels_json, invalidation_labels_json,
                       policy_json, skills_json,
                       access_profile_json, diagnostic_events_json,
                       started_at, completed_at
                FROM human_feedback_attempts
                WHERE feedback_batch_id IN (
                    SELECT feedback_batch_id FROM human_feedback_batches WHERE run_id = ?
                )
                ORDER BY feedback_batch_id, round_number
                """,
                (run_id,),
            ).fetchall()
        attempts_by_batch: dict[str, list[dict[str, object]]] = {}
        for row in attempts:
            attempts_by_batch.setdefault(str(row["feedback_batch_id"]), []).append(
                {
                    "id": row["attempt_id"],
                    "round": row["round_number"],
                    "status": row["status"],
                    "assignment": json.loads(row["assignment_json"]),
                    "result": json.loads(row["result_json"]) if row["result_json"] else None,
                    "head_sha": row["head_sha"],
                    "evidence": json.loads(row["evidence_json"]) if row["evidence_json"] else [],
                    "deterministic_verification": (
                        json.loads(row["deterministic_verification_json"])
                        if row["deterministic_verification_json"]
                        else None
                    ),
                    "review_batch_id": row["review_batch_id"],
                    "projected_labels": (
                        json.loads(row["projected_labels_json"])
                        if row["projected_labels_json"]
                        else []
                    ),
                    "invalidation_labels": (
                        json.loads(row["invalidation_labels_json"])
                        if row["invalidation_labels_json"]
                        else []
                    ),
                    "policy": json.loads(row["policy_json"]) if row["policy_json"] else None,
                    "skills": json.loads(row["skills_json"]) if row["skills_json"] else [],
                    "access_profile": (
                        json.loads(row["access_profile_json"])
                        if row["access_profile_json"]
                        else None
                    ),
                    "diagnostic_events": (
                        json.loads(row["diagnostic_events_json"])
                        if row["diagnostic_events_json"]
                        else []
                    ),
                    "started_at": row["started_at"],
                    "completed_at": row["completed_at"],
                }
            )
        records = []
        for row in batches:
            batch_attempts = attempts_by_batch.get(str(row["feedback_batch_id"]), [])
            records.append(
                {
                    "id": row["feedback_batch_id"],
                    "delivery_id": row["delivery_id"],
                    "pull_request_number": row["pull_request_number"],
                    "starting_head_sha": row["starting_head_sha"],
                    "author": row["author"],
                    "feedback": json.loads(row["feedback_json"]),
                    "superseded": {
                        "head_sha": row["starting_head_sha"],
                        "evidence": json.loads(row["superseded_evidence_json"]),
                        "review_batch_id": row["superseded_review_batch_id"],
                    },
                    "round_limit": row["round_limit"],
                    "round_count": len(batch_attempts),
                    "status": row["status"],
                    "projected_labels": (
                        json.loads(row["projected_labels_json"])
                        if row["projected_labels_json"]
                        else []
                    ),
                    "attempts": batch_attempts,
                    "created_at": row["created_at"],
                    "completed_at": row["completed_at"],
                }
            )
        return {"batches": records}

    def recoverable_feedback_batches(self, run_id: str) -> list[dict[str, object]]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT feedback_batch_id, pull_request_number, starting_head_sha,
                       source_id, feedback_json, status
                FROM human_feedback_batches
                WHERE run_id = ? AND status IN ('pending', 'running')
                ORDER BY rowid
                """,
                (run_id,),
            ).fetchall()
        return [
            {
                "id": row["feedback_batch_id"],
                "pull_request_number": row["pull_request_number"],
                "starting_head_sha": row["starting_head_sha"],
                "source_id": row["source_id"],
                "feedback": tuple(json.loads(row["feedback_json"])),
                "status": row["status"],
            }
            for row in rows
        ]

    def begin_feedback_attempt(
        self,
        *,
        feedback_batch_id: str,
        round_number: int,
        assignment: dict[str, object],
        started_at: str,
    ) -> str:
        if round_number not in {1, 2, 3}:
            raise ValueError("feedback round must be between one and three")
        with self._lock, self._connection:
            batch = self._connection.execute(
                "SELECT status FROM human_feedback_batches WHERE feedback_batch_id = ?",
                (feedback_batch_id,),
            ).fetchone()
            if batch is None or batch["status"] not in {"pending", "running"}:
                raise RuntimeError("terminal feedback batch cannot start another attempt")
            self._connection.execute(
                """
                UPDATE human_feedback_batches SET status = 'running'
                WHERE feedback_batch_id = ? AND status = 'pending'
                """,
                (feedback_batch_id,),
            )
            attempt_id = str(uuid.uuid4())
            self._connection.execute(
                """
                INSERT INTO human_feedback_attempts (
                    attempt_id, feedback_batch_id, round_number, status,
                    assignment_json, started_at
                ) VALUES (?, ?, ?, 'running', ?, ?)
                ON CONFLICT(feedback_batch_id, round_number) DO NOTHING
                """,
                (
                    attempt_id,
                    feedback_batch_id,
                    round_number,
                    json.dumps(assignment, sort_keys=True),
                    started_at,
                ),
            )
            row = self._connection.execute(
                """
                SELECT attempt_id FROM human_feedback_attempts
                WHERE feedback_batch_id = ? AND round_number = ?
                """,
                (feedback_batch_id, round_number),
            ).fetchone()
        if row is None:
            raise RuntimeError("human feedback attempt could not be created")
        return str(row["attempt_id"])

    def complete_feedback_attempt(
        self,
        *,
        attempt_id: str,
        status: str,
        result: dict[str, object],
        head_sha: str | None,
        evidence: list[dict[str, object]],
        deterministic_verification: dict[str, object] | None,
        review_batch_id: str | None,
        projected_labels: frozenset[str],
        invalidation_labels: frozenset[str],
        policy: dict[str, object],
        skills: list[dict[str, str]],
        access_profile: dict[str, object],
        diagnostic_events: list[dict[str, object]],
        completed_at: str,
    ) -> None:
        if status not in {"unsuccessful", "verified", "blocked", "failed"}:
            raise ValueError("unsupported feedback attempt status")
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE human_feedback_attempts
                SET status = ?, result_json = ?, head_sha = ?, evidence_json = ?,
                    deterministic_verification_json = ?, review_batch_id = ?,
                    projected_labels_json = ?, invalidation_labels_json = ?,
                    policy_json = ?, skills_json = ?,
                    access_profile_json = ?, diagnostic_events_json = ?, completed_at = ?
                WHERE attempt_id = ? AND status = 'running'
                """,
                (
                    status,
                    json.dumps(result, sort_keys=True),
                    head_sha,
                    json.dumps(evidence, sort_keys=True),
                    (
                        json.dumps(deterministic_verification, sort_keys=True)
                        if deterministic_verification is not None
                        else None
                    ),
                    review_batch_id,
                    json.dumps(sorted(projected_labels)),
                    json.dumps(sorted(invalidation_labels)),
                    json.dumps(policy, sort_keys=True),
                    json.dumps(skills, sort_keys=True),
                    json.dumps(access_profile, sort_keys=True),
                    json.dumps(diagnostic_events, sort_keys=True),
                    completed_at,
                    attempt_id,
                ),
            )

    def complete_feedback_batch(
        self,
        *,
        feedback_batch_id: str,
        status: str,
        projected_labels: frozenset[str],
        completed_at: str,
    ) -> None:
        if status not in {"verified", "needs-info", "ready-for-human"}:
            raise ValueError("unsupported terminal feedback status")
        with self._lock, self._connection:
            self._connection.execute(
                """
                UPDATE human_feedback_batches
                SET status = ?, projected_labels_json = ?, completed_at = ?
                WHERE feedback_batch_id = ? AND status IN ('pending', 'running')
                """,
                (
                    status,
                    json.dumps(sorted(projected_labels)),
                    completed_at,
                    feedback_batch_id,
                ),
            )

    def close(self) -> None:
        with self._lock:
            self._connection.close()
