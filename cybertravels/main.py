"""The BFF / orchestrator — the only thing a browser talks to.

It authenticates the person, starts an agent run, streams the trace back as
server-sent events, and holds the endpoint a human uses to approve or refuse a
high-risk action. It holds no downstream authority of its own: every action
that touches a booking goes through a token exchange first.

**This application is deliberately vulnerable.** `LABELS.md` lists eight real
defects that are in here on purpose, including a SQL injection and a path
traversal that now execute rather than merely parse. It binds to 127.0.0.1 and
it must never be exposed to a network, put behind a tunnel, or deployed.

    uvicorn cybertravels.main:app --host 127.0.0.1 --port 8000
"""
# step:file G1.1
import asyncio
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from pathlib import Path

from . import config, db, identity, runtime

app = FastAPI(title="CyberTravels", docs_url=None, redoc_url=None)
STATIC = Path(__file__).resolve().parent / "static"


@app.on_event("startup")
async def _startup():
    db.conn()
    (Path(config.DATA_DIR) / "invoices").mkdir(parents=True, exist_ok=True)
    manager = runtime.MCPManager()
    await manager.connect()
    runtime.set_manager(manager)
    app.state.manager = manager


@app.on_event("shutdown")
async def _shutdown():
    await app.state.manager.close()


@app.get("/", response_class=HTMLResponse)
async def index():
    return (STATIC / "index.html").read_text()


@app.post("/login")
async def login(request: Request):
    """No password. It is a demo login and it looks like one on purpose —
    wiring it to real OIDC is A2.1's exercise, not a detail we pretend is done."""
    body = await request.json()
    try:
        token = identity.mint_user_token(body.get("username", ""))
    except identity.IdentityError as e:
        raise HTTPException(401, str(e))
    user = config.USERS[body["username"]]
    return {"token": token, "user": body["username"], "display": user["display"],
            "role": user["role"],
            "may_delegate": sorted(config.ROLE_ALLOWED_SCOPES[user["role"]])}


def _bearer(request: Request) -> str:
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "no bearer token")
    return auth[7:]


@app.post("/agent/run")
async def agent_run(request: Request):
    """Start a run and stream its spans. The token rides the Authorization
    header, never a query string — a token in a URL is a token in every proxy
    log between here and the browser."""
    token = _bearer(request)
    body = await request.json()
    try:
        claims = __import__("jwt").decode(
            token, config.IDP_SECRET, algorithms=[config.JWT_ALG],
            audience=config.AUD_BFF)
    except Exception as e:  # noqa: BLE001
        raise HTTPException(401, f"invalid token: {e}")

    q: asyncio.Queue = asyncio.Queue()
    asyncio.create_task(runtime.run(token, claims["sub"], "workflow",
                                    body.get("message", ""), q))

    async def stream():
        while True:
            span = await q.get()
            if span is None:
                break
            yield f"data: {json.dumps(span, default=str)}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/agent/approve")
async def approve(request: Request):
    """The human gate. Approving is an action by a named person and it is
    audited as one."""
    _bearer(request)
    body = await request.json()
    fut = runtime.PENDING.get(body.get("approval_id"))
    if fut is None or fut.done():
        raise HTTPException(404, "no such pending approval")
    fut.set_result(bool(body.get("granted")))
    return {"ok": True}


@app.get("/audit")
async def audit(request: Request):
    _bearer(request)
    return db.recent_audit()
