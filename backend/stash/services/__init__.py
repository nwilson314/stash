import httpx
from fastapi import Depends

from stash.services.ai import AIService
from stash.services.links import LinkService


async def get_link_service() -> LinkService:
    """Factory for LinkService instances.

    Creates a new httpx client for each request.
    Client will be automatically closed when the request is done.
    """
    async with httpx.AsyncClient() as client:
        yield LinkService(client)


async def get_ai_service() -> AIService:
    """Factory for AIService instances.

    Creates a new httpx client for each request.
    Client will be automatically closed when the request is done.
    """
    yield AIService()
