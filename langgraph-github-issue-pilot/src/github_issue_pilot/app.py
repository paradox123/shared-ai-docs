from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Callable
from collections.abc import Set as AbstractSet
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from github_issue_pilot.github import GitHubPort
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
    allowed_repositories: AbstractSet[str],
    allowed_event_actions: AbstractSet[tuple[str, str]],
    now: datetime,
) -> Delivery:
    delivery_id = request.headers.get("x-github-delivery", "").strip()
    event = request.headers.get("x-github-event", "").strip()
    if not delivery_id:
        raise HTTPException(status_code=400, detail="missing delivery id")
    try:
        payload = json.loads(body)
        action = payload["action"]
        repository = payload["repository"]["full_name"]
        issue_number = payload["issue"]["number"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=400, detail="invalid delivery payload") from exc

    if not isinstance(action, str) or (event, action) not in allowed_event_actions:
        raise HTTPException(status_code=403, detail="event action not allowed")
    if not isinstance(repository, str) or repository not in allowed_repositories:
        raise HTTPException(status_code=403, detail="repository not allowed")
    if not isinstance(issue_number, int) or isinstance(issue_number, bool) or issue_number <= 0:
        raise HTTPException(status_code=400, detail="invalid issue number")

    return Delivery(
        delivery_id=delivery_id,
        body_digest=hashlib.sha256(body).hexdigest(),
        repository=repository,
        issue_number=issue_number,
        event=event,
        action=action,
        accepted_at=now.isoformat(),
    )


def create_app(
    *,
    database_path: Path,
    webhook_secret: bytes | None,
    allowed_repositories: AbstractSet[str],
    github: GitHubPort,
    clock: Callable[[], datetime],
    internal_webhook_secret: bytes | None = None,
    max_request_bytes: int = 1_048_576,
    allowed_event_actions: AbstractSet[tuple[str, str]] | None = None,
) -> FastAPI:
    if (webhook_secret is None) == (internal_webhook_secret is None):
        raise ValueError("exactly one webhook authentication mode must be configured")

    store = WorkflowStore(database_path)
    runtime = WorkflowRuntime(database_path=database_path, store=store, github=github, clock=clock)
    event_actions = {("issues", "labeled")} if allowed_event_actions is None else allowed_event_actions

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        try:
            yield
        finally:
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
            allowed_repositories=allowed_repositories,
            allowed_event_actions=event_actions,
            now=clock(),
        )
        result = store.accept(delivery)
        if result == "conflict":
            raise HTTPException(status_code=409, detail="delivery id reused with different content")
        if result == "accepted":
            background_tasks.add_task(runtime.dispatch, delivery)
        status_code = 202 if result == "accepted" else 200
        response_status = "already_accepted" if result == "duplicate" else result
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
