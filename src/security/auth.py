from typing import Protocol, Sequence

from langgraph_sdk import Auth
from pydantic import BaseModel, Field

from security.db import get_session_from_token, validate_api_key

auth = Auth()


class UserContext(BaseModel):
    """User context for authentication."""

    identity: str = Field(...)
    is_authenticated: bool = Field(True)
    permissions: Sequence[str] | None = Field(None)
    organization_id: str | None = Field(None)
    email: str | None = Field(None)


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

    user = UserContext(
        identity=str(session["user_id"]),
        is_authenticated=True,
        organization_id=str(session["active_organization_id"]),
    )

    return user


@auth.authenticate
async def authenticate(headers: dict[str, bytes]) -> UserContext:
    """Authenticate requests using LangSmith API key or session token."""
    try:
        # First check for LangSmith API key - try both string and bytes keys
        api_key = headers.get("x-api-key") or headers.get(b"x-api-key")

        # Convert bytes to string if needed
        if isinstance(api_key, bytes):
            api_key = api_key.decode()
        if api_key and validate_api_key(api_key):
            return UserContext(
                identity="backend",
                is_authenticated=True,
            )

        # If no valid API key, try session auth - handle both string and bytes
        authorization = headers.get("authorization") or headers.get(b"authorization")

        # Convert bytes to string if needed
        if isinstance(authorization, bytes):
            authorization = authorization.decode()

        token = authorization.split(" ")[1]

        return await authenticate_session(token)
    except Exception as e:
        raise Auth.exceptions.HTTPException(
            status_code=401,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@auth.on
async def scope_to_organization(
    ctx: AuthContext,
    value: dict,
) -> dict:
    """Scope resources to organization for non-admin users."""
    # Check if it's a LangGraph studio user (admin)
    if ctx.user.identity == "langgraph-studio-user" or ctx.user.identity == "backend":
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


# Thread handlers
@auth.on.threads
async def on_thread(ctx: AuthContext, value: Auth.types.on.threads.value):
    """Block thread access for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to create threads"
        )
    return {}


@auth.on.threads.read
async def on_thread_read(ctx: AuthContext, value: Auth.types.ThreadsRead.values):
    """Allow thread reading (streaming, etc.) for all authenticated users, scoped to organization."""
    if ctx.user.identity in ["langgraph-studio-user", "backend"]:
        return {}
    return {"organization_id": ctx.user.organization_id}


# Assistant handler
@auth.on.assistants
async def on_assistants_read(ctx: AuthContext, value: Auth.types.on.assistants.value):
    """Block assistant reading for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to read assistants"
        )
    return {}


# Cron handler
@auth.on.crons
async def on_crons_read(ctx: AuthContext, value: Auth.types.on.crons.value):
    """Block cron reading for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to read crons"
        )
    return {}
