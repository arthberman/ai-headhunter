import os
import json
from datetime import UTC, datetime
from typing import Optional

import asyncpg
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from upstash_redis.asyncio import Redis

# Load environment variables
load_dotenv()


# ---------------------------
# Pydantic Schemas for Redis session
# ---------------------------


class RedisSessionData(BaseModel):
    """Pydantic schema for the session data stored in Redis."""

    token: str = Field(..., alias="token")
    expires_at: datetime = Field(..., alias="expiresAt")
    user_id: str = Field(..., alias="userId")
    active_organization_id: str = Field(..., alias="activeOrganizationId")

    class Config:
        """Pydantic configuration for the Redis session data."""

        extra = "allow"
        allow_population_by_field_name = True


class RedisSession(BaseModel):
    """Pydantic schema for the Redis session data."""

    user: dict  # This holds extra user info but is not used in our current logic
    session: RedisSessionData

    class Config:
        """Pydantic configuration for the Redis session data."""

        extra = "allow"


# ---------------------------
# Existing helper functions
# ---------------------------


def validate_api_key(api_key: str) -> bool:
    """Validate API key against possible environment variables."""
    valid_keys = [
        os.getenv("LANGSMITH_API_KEY"),
        os.getenv("LANGCHAIN_API_KEY"),
        os.getenv("LANGGRAPH_API_KEY"),
    ]
    print("-" * 30)
    print("-" * 30)
    print("valid_keys", valid_keys)
    print("api_key", api_key)
    print("-" * 30)
    print("-" * 30)
    return api_key in [key for key in valid_keys if key]  # Filter out None values


async def get_session_from_token(token: str) -> Optional[dict]:
    """Validate session token by first checking Redis and, if not found or expired, querying the database."""
    # Try to get session from Redis first.
    redis = Redis(
        url=os.getenv("UPSTASH_REDIS_REST_URL"),
        token=os.getenv("UPSTASH_REDIS_REST_TOKEN"),
    )
    redis_data = await redis.get(token)
    if redis_data:
        try:
            # Parse the Redis session string into JSON first
            if isinstance(redis_data, str):
                redis_data = json.loads(redis_data)
            # Parse the Redis session JSON using our Pydantic schema.
            redis_session = RedisSession.model_validate(redis_data)
        except Exception as e:
            print(f"Error parsing redis session: {e}")
        else:
            # Check if the session is not expired.
            # Use datetime.now(UTC) to be consistent with our DB query.
            if redis_session.session.expires_at > datetime.now(UTC):
                # Return an object similar to the DB query result.
                return {
                    "session_id": redis_session.session.token,  # Using token as the session identifier
                    "expires_at": redis_session.session.expires_at,
                    "user_id": redis_session.session.user_id,
                    "active_organization_id": redis_session.session.active_organization_id,
                }
            else:
                print("Redis session is expired.")

    # Fallback: Query the database if nothing was found in Redis or if the session is expired.
    pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    try:
        async with pool.acquire() as conn:
            # Ensure timezone-aware datetime is used for the comparison.
            current_time = datetime.now(UTC)

            result = await conn.fetchrow(
                """
                SELECT 
                    s.id as session_id,
                    s.expires_at,
                    s.active_organization_id,
                    u.id as user_id
                FROM session s
                JOIN "user" u ON s.user_id = u.id
                WHERE s.token = $1 
                AND s.expires_at > $2::timestamptz
                """,
                token,
                current_time,
            )
            if result:
                return dict(result)
        return None
    finally:
        await pool.close()
