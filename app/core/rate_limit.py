from fastapi import Request
from fastapi_limiter.identifier import default_identifier
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Rate, Limiter, RedisBucket
from redis.asyncio import Redis
from dataclasses import dataclass


@dataclass(frozen=True)
class RateLimiters:
    login: RateLimiter
    authenticated: RateLimiter
    ai: RateLimiter

async def user_identifier(request: Request) -> str:
    return f"user:{request.app.state.user_id}"


async def _create_rate_limiter(
        redis: Redis,
        *,
        key: str,
        requests: int,
        duration: Duration,
        identifier
) -> RateLimiter:
    # is awaitable, just the typechecker underlining it because of improper return types
    bucket = await RedisBucket.init(
        rates=[Rate(requests, duration)],
        redis=redis,
        bucket_key=f"rate-limit:{key}"
    )

    return RateLimiter(
        limiter=Limiter(bucket),
        identifier=identifier
    )

async def create_rate_limiters(redis: Redis) -> RateLimiters:
    return RateLimiters(
        login=await _create_rate_limiter(
            redis,
            key="login",
            requests=5,
            duration=Duration.MINUTE,
            identifier=default_identifier
        ),
        authenticated=await _create_rate_limiter(
            redis,
            key="authenticated",
            requests=120,
            duration=Duration.MINUTE,
            identifier=user_identifier
        ),
        ai=await _create_rate_limiter(
            redis,
            key="ai",
            requests=10,
            duration=Duration.MINUTE,
            identifier=user_identifier
        )
    )