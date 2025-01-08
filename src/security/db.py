import os
from datetime import UTC, datetime
from typing import Optional

import asyncpg
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def validate_api_key(api_key: str) -> bool:
    """Validate API key against possible environment variables."""
    valid_keys = [
        os.getenv("LANGSMITH_API_KEY"),
        os.getenv("LANGCHAIN_API_KEY"),
        os.getenv("LANGGRAPH_API_KEY"),
    ]

    return api_key in [key for key in valid_keys if key]  # Filter out None values


async def get_session_from_token(token: str) -> Optional[dict]:
    """Validate session token and return user info."""
    pool = await asyncpg.create_pool(os.getenv("DATABASE_URL"))
    try:
        async with pool.acquire() as conn:
            # Make sure we use timezone-aware datetime for comparison
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
