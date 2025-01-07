from typing import Protocol, Sequence

from langgraph_sdk import Auth
from pydantic import BaseModel, Field

from src.security.db import get_session_from_token, validate_api_key

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

    return UserContext(
        identity=str(session["user_id"]),
        organization_id=str(session["active_organization_id"]),
        email=session["email"],
    )


@auth.authenticate
async def authenticate(headers: dict[str, bytes]) -> UserContext:
    """Authenticate requests using LangSmith API key or session token."""
    # First check for LangSmith API key - try both string and bytes keys
    api_key = headers.get("x-api-key") or headers.get(b"x-api-key")

    # Convert bytes to string if needed
    if isinstance(api_key, bytes):
        api_key = api_key.decode()

    if api_key and validate_api_key(api_key):
        return UserContext(
            identity="backend",
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


# Resource-specific handlers


# Thread handlers
@auth.on.threads.create
async def on_thread_create(
    ctx: AuthContext,
    value: Auth.types.ThreadsCreate.values,
):
    """Block thread creation for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to create threads"
        )
    return {}


@auth.on.threads.read
async def on_thread_read(
    ctx: AuthContext,
    value: Auth.types.ThreadsRead.values,
):
    """Allow thread reading for all authenticated users, scoped to organization."""
    if ctx.user.identity in ["langgraph-studio-user", "backend"]:
        return {}
    return {"organization_id": ctx.user.organization_id}


@auth.on.threads.update
async def on_thread_update(
    ctx: AuthContext,
    value: Auth.types.ThreadsUpdate.values,
):
    """Block thread updates for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to update threads"
        )
    return {}


@auth.on.threads.delete
async def on_thread_delete(
    ctx: AuthContext,
    value: Auth.types.ThreadsDelete.values,
):
    """Block thread deletion for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to delete threads"
        )
    return {}


@auth.on.threads.search
async def on_thread_search(
    ctx: AuthContext,
    value: Auth.types.ThreadsSearch.values,
):
    """Block thread search for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to search threads"
        )
    return {}


@auth.on.threads.create_run
async def on_thread_create_run(
    ctx: AuthContext,
    value: Auth.types.RunsCreate.values,
):
    """Allow run creation for all authenticated users, scoped to organization."""
    if ctx.user.identity in ["langgraph-studio-user", "backend"]:
        return {}
    return {"organization_id": ctx.user.organization_id}


# Assistant handlers
@auth.on.assistants.create
async def on_assistants_create(
    ctx: AuthContext,
    value: Auth.types.AssistantsCreate.values,
):
    """Block assistant creation for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to create assistants"
        )
    return {}


@auth.on.assistants.read
async def on_assistants_read(
    ctx: AuthContext,
    value: Auth.types.AssistantsRead.values,
):
    """Block assistant reading for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to read assistants"
        )
    return {}


@auth.on.assistants.update
async def on_assistants_update(
    ctx: AuthContext,
    value: Auth.types.AssistantsUpdate.values,
):
    """Block assistant updates for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to update assistants"
        )
    return {}


@auth.on.assistants.delete
async def on_assistants_delete(
    ctx: AuthContext,
    value: Auth.types.AssistantsDelete.values,
):
    """Block assistant deletion for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to delete assistants"
        )
    return {}


@auth.on.assistants.search
async def on_assistants_search(
    ctx: AuthContext,
    value: Auth.types.AssistantsSearch.values,
):
    """Block assistant search for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to search assistants"
        )
    return {}


# Cron handlers
@auth.on.crons.create
async def on_crons_create(
    ctx: AuthContext,
    value: Auth.types.CronsCreate.values,
):
    """Block cron creation for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to create crons"
        )
    return {}


@auth.on.crons.read
async def on_crons_read(
    ctx: AuthContext,
    value: Auth.types.CronsRead.values,
):
    """Block cron reading for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to read crons"
        )
    return {}


@auth.on.crons.update
async def on_crons_update(
    ctx: AuthContext,
    value: Auth.types.CronsUpdate.values,
):
    """Block cron updates for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to update crons"
        )
    return {}


@auth.on.crons.delete
async def on_crons_delete(
    ctx: AuthContext,
    value: Auth.types.CronsDelete.values,
):
    """Block cron deletion for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to delete crons"
        )
    return {}


@auth.on.crons.search
async def on_crons_search(
    ctx: AuthContext,
    value: Auth.types.CronsSearch.values,
):
    """Block cron search for non-admin users."""
    if ctx.user.identity not in ["langgraph-studio-user", "backend"]:
        raise Auth.exceptions.HTTPException(
            status_code=403, detail="Insufficient permissions to search crons"
        )
    return {}
