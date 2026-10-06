import json

import httpx2
import pytest


pytestmark = [pytest.mark.anyio, pytest.mark.starter]


async def test_echo_discovery_and_call(session):
    tools = (await session.list_tools()).tools
    echo = next(tool for tool in tools if tool.name == "echo")
    assert echo.description
    result = await session.call_tool("echo", {"text": "Привет, Алиса 👋"})
    assert not result.is_error
    assert any(block.type == "text" and block.text == "Привет, Алиса 👋" for block in result.content)


async def test_health(server_url):
    async with httpx2.AsyncClient() as client:
        response = await client.get(server_url.removesuffix("/mcp") + "/healthz")
    assert response.status_code == 200
    assert json.loads(response.text) == {"status": "ok"}


async def test_repeated_calls_are_independent(session):
    for text in ("first", "second", "first"):
        result = await session.call_tool("echo", {"text": text})
        assert not result.is_error
        assert any(block.type == "text" and block.text == text for block in result.content)
