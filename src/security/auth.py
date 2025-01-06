from typing import Literal, Protocol

from langgraph_sdk import Auth
from pydantic import BaseModel

from src.security.db import get_session_from_token, validate_api_key

auth = Auth()


class UserContext(BaseModel):
    """User context for authentication."""

    identity: str
    is_authenticated: bool = True
    organization_id: str | None = None  # Optional for admin
    email: str
    name: str
    auth_type: Literal["session", "admin"]


class AuthContext(Protocol):
    """Auth context for organization scoping."""

    user: UserContext


async def authenticate_session(token: str) -> UserContext:
    """Authenticate using session token."""
    session = await get_session_from_token(token)
    if not session:
        raise Auth.exceptions.HTTPException(
            status_code=401, detail="Invalid or expired session"
        )

    return UserContext(
        identity=str(session["user_id"]),
        organization_id=str(session["active_organization_id"]),
        email=session["email"],
        name=session["name"],
        auth_type="session",
    )


@auth.authenticate
async def authenticate(headers: dict) -> UserContext:
    """Authenticate requests using LangSmith API key or session token."""
    # First check for LangSmith API key - try both string and bytes keys
    api_key = headers.get("x-api-key") or headers.get(b"x-api-key")

    # Convert bytes to string if needed
    if isinstance(api_key, bytes):
        api_key = api_key.decode()

    if api_key and validate_api_key(api_key):
        return UserContext(
            identity="admin",
            email="arthur@repio.co",
            name="Arthur",
            auth_type="admin",
        )

    # If no valid API key, try session auth - handle both string and bytes
    session_token = headers.get("session") or headers.get(b"session")
    if session_token:
        if isinstance(session_token, bytes):
            session_token = session_token.decode()
        return await authenticate_session(session_token)

    raise Auth.exceptions.HTTPException(
        status_code=401,
        detail="Invalid authentication. Use either LangSmith API key or session token",
    )


@auth.on
async def scope_to_organization(
    ctx: AuthContext,
    value: dict,
) -> dict:
    """Scope resources to organization for non-admin users."""
    # Check if it's a LangGraph studio user (admin)
    if ctx.user.identity == "langgraph-studio-user":
        return {}

    if ctx.user.auth_type == "admin":
        # Our admin users have full access
        return {}

    # Regular users are scoped to their organization
    org_id = ctx.user.organization_id
    if not org_id:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="No organization specified"
        )

    filters = {"organization_id": org_id}
    metadata = value.setdefault("metadata", {})
    metadata.update(filters)
    return filters


# Resource-specific handlers
""" @auth.on.threads.create """


async def on_thread_create(
    ctx: AuthContext,
    value: Auth.types.on.threads.create.value,
):
    """Add organization and owner metadata when creating threads."""
    metadata = value.setdefault("metadata", {})
    metadata.update({"organization_id": ctx.user.organization_id})
    return {"organization_id": ctx.user.organization_id}


""" @auth.on.threads.read """


async def on_thread_read(
    ctx: AuthContext,
    value: Auth.types.on.threads.read.value,
):
    """Only allow access to threads in user's organization."""
    return {"organization_id": ctx.user.organization_id}


""" @auth.on.assistants """


async def on_assistants(
    ctx: AuthContext,
    value: Auth.types.on.assistants.value,
):
    """Scope assistants to organization."""
    return {"organization_id": ctx.user.organization_id}


""" @auth.on.crons """


async def on_crons(
    ctx: AuthContext,
    value: Auth.types.on.crons.value,
):
    """Scope cron jobs to organization."""
    return {"organization_id": ctx.user.organization_id}
