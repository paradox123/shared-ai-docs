from __future__ import annotations

import hashlib
import hmac
import json
from collections.abc import Callable, Mapping
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from github_issue_pilot.github import (
    REPOSITORY_ADAPTER_VERSION,
    RepositoryAdapter,
)
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


def _verify_signature(body: bytes, supplied: str | None, secret: bytes) -> None:
    expected = "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()
    if supplied is None or not hmac.compare_digest(supplied, expected):
        raise HTTPException(status_code=401, detail="invalid signature")


def _delivery_from_request(
    *,
    body: bytes,
    request: Request,
    repository_adapters: Mapping[str, RepositoryAdapter],
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
        subject = payload.get("issue") or payload.get("pull_request")
        issue_number = subject["number"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=400, detail="invalid delivery payload") from exc

    if not isinstance(repository, str) or repository not in repository_adapters:
        raise HTTPException(status_code=403, detail="repository not allowed")
    adapter = repository_adapters[repository]
    if adapter.repository != repository or adapter.contract_version != REPOSITORY_ADAPTER_VERSION:
        raise HTTPException(status_code=403, detail="repository adapter not compatible")
    if not isinstance(action, str) or (event, action) not in adapter.allowed_event_actions:
        raise HTTPException(status_code=403, detail="event action not allowed")
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
    webhook_secret: bytes,
    clock: Callable[[], datetime],
    repository_adapters: Mapping[str, RepositoryAdapter],
    max_request_bytes: int = 1_048_576,
) -> FastAPI:
    store = WorkflowStore(database_path)
    runtime = WorkflowRuntime(
        database_path=database_path,
        store=store,
        repository_adapters=repository_adapters,
        clock=clock,
    )

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
        _verify_signature(body, request.headers.get("x-hub-signature-256"), webhook_secret)
        delivery = _delivery_from_request(
            body=body,
            request=request,
            repository_adapters=repository_adapters,
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
