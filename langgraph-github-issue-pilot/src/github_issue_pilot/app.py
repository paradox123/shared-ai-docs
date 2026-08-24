from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
from collections.abc import Callable, Mapping
from contextlib import asynccontextmanager, suppress
from datetime import datetime
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from github_issue_pilot.evidence import redact_text
from github_issue_pilot.github import (
    REPOSITORY_ADAPTER_VERSION,
    RepositoryAdapter,
)
from github_issue_pilot.implementation import ImplementationServices
from github_issue_pilot.reconciliation import system_boot_session_id
from github_issue_pilot.storage import Delivery, WorkflowStore
from github_issue_pilot.workflow import WorkflowRuntime


async def _bounded_body(request: Request, maximum: int) -> bytes:
    declared_length = request.headers.get("content-length")
    if declared_length is not None:
        try:
            if int(declared_length) > maximum:
                raise HTTPException(status_code=413, detail="request body too large")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="invalid content length") from exc

    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > maximum:
            raise HTTPException(status_code=413, detail="request body too large")
    return bytes(body)


def _verify_signature(message: bytes, supplied: str | None, secret: bytes) -> None:
    expected = "sha256=" + hmac.new(secret, message, hashlib.sha256).hexdigest()
    if supplied is None or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="invalid signature")


def _delivery_from_request(
    *,
    body: bytes,
    request: Request,
    repository_adapters: Mapping[str, RepositoryAdapter],
    now: datetime,
    sensitive_values: tuple[str, ...] = (),
) -> Delivery:
    delivery_id = request.headers.get("x-github-delivery", "").strip()
    event = request.headers.get("x-github-event", "").strip()
    if not delivery_id:
        raise HTTPException(status_code=400, detail="missing delivery id")
    try:
        payload = json.loads(body)
        action = payload["action"]
        repository = payload["repository"]["full_name"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=400, detail="invalid delivery payload") from exc

    if not isinstance(repository, str) or repository not in repository_adapters:
        raise HTTPException(status_code=403, detail="repository not allowed")
    adapter = repository_adapters[repository]
    if adapter.repository != repository or adapter.contract_version != REPOSITORY_ADAPTER_VERSION:
        raise HTTPException(status_code=403, detail="repository adapter not compatible")
    if not isinstance(action, str) or (event, action) not in adapter.allowed_event_actions:
        raise HTTPException(status_code=403, detail="event action not allowed")

    kind = "issue"
    actor_login: str | None = None
    feedback: tuple[str, ...] = ()
    head_sha: str | None = None
    merged = False
    pull_request_number: int | None = None
    source_id: str | None = None
    try:
        if event == "issues":
            issue_number = payload["issue"]["number"]
        elif event in {"pull_request_review", "pull_request_review_comment"}:
            pull_request = payload["pull_request"]
            pull_request_number = pull_request["number"]
            head_sha = pull_request["head"]["sha"]
            source = payload["review"] if event == "pull_request_review" else payload["comment"]
            source_id = str(source["id"])
            user = source["user"]
            actor_login = str(user["login"])
            actor_type = str(user["type"])
            text = str(source.get("body") or "").strip()
            if event == "pull_request_review" and str(source.get("state", "")).casefold() != (
                "changes_requested"
            ):
                raise HTTPException(status_code=403, detail="review is not a change request")
            if not adapter.is_configured_human(actor_login, actor_type):
                raise HTTPException(status_code=403, detail="feedback author is not configured human")
            if not text:
                raise HTTPException(status_code=403, detail="feedback is empty")
            feedback = (redact_text(text, sensitive_values),)
            issue_number = pull_request_number
            kind = "human_feedback"
        elif event == "pull_request":
            pull_request = payload["pull_request"]
            pull_request_number = pull_request["number"]
            head = pull_request.get("head")
            head_sha = str(head.get("sha")) if isinstance(head, dict) and head.get("sha") else None
            merged = pull_request.get("merged") is True
            merger = pull_request.get("merged_by")
            actor_login = str(merger.get("login", "")) if isinstance(merger, dict) else ""
            actor_type = str(merger.get("type", "")) if isinstance(merger, dict) else ""
            issue_number = pull_request_number
            if (
                merged
                and actor_login
                and adapter.is_configured_human(actor_login, actor_type)
            ):
                kind = "human_merge"
            elif head_sha is None and not isinstance(merger, dict):
                kind = "repository_activity"
            else:
                kind = "pull_request_activity"
        else:
            raise HTTPException(status_code=403, detail="event not supported")
    except HTTPException:
        raise
    except (KeyError, TypeError) as exc:
        raise HTTPException(status_code=400, detail="invalid delivery payload") from exc

    if not isinstance(issue_number, int) or isinstance(issue_number, bool) or issue_number <= 0:
        raise HTTPException(status_code=400, detail="invalid issue number")
    if pull_request_number is not None and (
        not isinstance(pull_request_number, int)
        or isinstance(pull_request_number, bool)
        or pull_request_number <= 0
    ):
        raise HTTPException(status_code=400, detail="invalid pull request number")

    command_key = f"delivery:{delivery_id}"
    if event == "issues" and action == "labeled":
        label_payload = payload.get("label")
        label_name = (
            str(label_payload.get("name", "")).strip().casefold()
            if isinstance(label_payload, dict)
            else ""
        )
        if label_name:
            command_key = f"issue-label:{repository}:{issue_number}:{label_name}"
    elif kind == "human_merge" and pull_request_number is not None and head_sha is not None:
        command_key = (
            f"pull-merged:{repository}:{pull_request_number}:{head_sha.casefold()}"
        )
    elif (
        kind == "human_feedback"
        and pull_request_number is not None
        and source_id is not None
        and head_sha is not None
    ):
        command_key = (
            f"pull-feedback:{repository}:{pull_request_number}:"
            f"{source_id}:{head_sha.casefold()}"
        )

    return Delivery(
        delivery_id=delivery_id,
        body_digest=hashlib.sha256(body).hexdigest(),
        repository=repository,
        issue_number=issue_number,
        event=event,
        action=action,
        accepted_at=now.isoformat(),
        kind=kind,
        pull_request_number=pull_request_number,
        actor_login=actor_login,
        feedback=feedback,
        head_sha=head_sha,
        merged=merged,
        source_id=source_id,
        command_key=command_key,
    )


def create_app(
    *,
    database_path: Path,
    webhook_secret: bytes | None,
    clock: Callable[[], datetime],
    repository_adapters: Mapping[str, RepositoryAdapter],
    internal_webhook_secret: bytes | None = None,
    max_request_bytes: int = 1_048_576,
    implementation: ImplementationServices | None = None,
    boot_session_id: Callable[[], str] = system_boot_session_id,
    heartbeat_interval_seconds: float = 60.0,
) -> FastAPI:
    if (webhook_secret is None) == (internal_webhook_secret is None):
        raise ValueError("exactly one webhook authentication mode must be configured")
    if heartbeat_interval_seconds <= 0:
        raise ValueError("heartbeat interval must be positive")

    store = WorkflowStore(database_path)
    runtime = WorkflowRuntime(
        database_path=database_path,
        store=store,
        repository_adapters=repository_adapters,
        clock=clock,
        implementation=implementation,
    )

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        heartbeat_task: asyncio.Task[None] | None = None

        async def heartbeat() -> None:
            while True:
                await asyncio.sleep(heartbeat_interval_seconds)
                await asyncio.to_thread(runtime.reconcile_interventions)
                store.touch_liveness(clock().isoformat())

        try:
            boot_id = boot_session_id()
            _, reconciliation_required = store.begin_startup_reconciliation(
                boot_id=boot_id,
                now=clock(),
                threshold_seconds=24 * 60 * 60,
            )
            if reconciliation_required:
                counts = runtime.reconcile_current_state(boot_id)
                store.complete_startup_reconciliation(
                    boot_id=boot_id,
                    completed_at=clock().isoformat(),
                    **counts,
                )
            runtime.reconcile_interventions()
            runtime.recover()
            heartbeat_task = asyncio.create_task(heartbeat())
            yield
        finally:
            if heartbeat_task is not None:
                heartbeat_task.cancel()
                with suppress(asyncio.CancelledError):
                    await heartbeat_task
            store.touch_liveness(clock().isoformat())
            runtime.close()
            store.close()

    app = FastAPI(lifespan=lifespan)

    @app.post("/webhooks/github")
    async def accept_github_delivery(request: Request, background_tasks: BackgroundTasks) -> JSONResponse:
        body = await _bounded_body(request, max_request_bytes)
        if webhook_secret is not None:
            signed_message = body
            supplied_signature = request.headers.get("x-hub-signature-256")
            authentication_secret = webhook_secret
        else:
            delivery_id = request.headers.get("x-github-delivery", "").strip()
            event = request.headers.get("x-github-event", "").strip()
            signed_message = b"\n".join((delivery_id.encode(), event.encode(), body))
            supplied_signature = request.headers.get("x-pilot-signature-256")
            if internal_webhook_secret is None:  # Guarded during application construction.
                raise RuntimeError("internal webhook secret is unavailable")
            authentication_secret = internal_webhook_secret
        _verify_signature(signed_message, supplied_signature, authentication_secret)
        delivery = _delivery_from_request(
            body=body,
            request=request,
            repository_adapters=repository_adapters,
            now=clock(),
            sensitive_values=implementation.sensitive_values if implementation else (),
        )
        result = store.accept(delivery)
        if result == "conflict":
            raise HTTPException(status_code=409, detail="delivery id reused with different content")
        if result == "accepted":
            background_tasks.add_task(runtime.dispatch, delivery)
        status_code = 202 if result == "accepted" else 200
        response_status = (
            "already_accepted"
            if result in {"duplicate", "command_duplicate"}
            else result
        )
        return JSONResponse(
            status_code=status_code,
            content={"delivery_id": delivery.delivery_id, "status": response_status},
        )

    @app.get("/workflows/{owner}/{repository}/issues/{issue_number}")
    async def workflow_state(owner: str, repository: str, issue_number: int) -> dict[str, object]:
        state = runtime.workflow_state(f"{owner}/{repository}", issue_number)
        if state is None:
            raise HTTPException(status_code=404, detail="workflow not found")
        return state

    return app
