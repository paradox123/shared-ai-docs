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

    def complete_run(self, run_id: str) -> None:
        with self._lock, self._connection:
            self._connection.execute(
                "UPDATE issue_runs SET status = 'completed' WHERE run_id = ? AND status = 'running'",
                (run_id,),
            )

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
                ON CONFLICT(run_id) DO NOTHING
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
        with self._lock:
            batch = self._connection.execute(
                """
                SELECT batch_id, status, head_sha, pull_request_number, reason,
                       projected_labels_json, started_at, completed_at
                FROM review_batches
                WHERE run_id = ?
                ORDER BY rowid DESC
                LIMIT 1
                """,
                (run_id,),
            ).fetchone()
            if batch is None:
                return None
            rows = self._connection.execute(
                """
                SELECT axis, assignment_json, result_json, policy_json, route_axis,
                       skills_json, access_profile_json, diagnostic_events_json,
                       completed_at
                FROM review_results
                WHERE batch_id = ?
                ORDER BY CASE axis
                    WHEN 'requirements' THEN 1
                    WHEN 'code' THEN 2
                    WHEN 'architecture' THEN 3
                END
                """,
                (batch["batch_id"],),
            ).fetchall()
        results = [
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
            for row in rows
        ]
        return {
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
            "results": results,
            "started_at": batch["started_at"],
            "completed_at": batch["completed_at"],
        }

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

    def close(self) -> None:
        with self._lock:
            self._connection.close()
