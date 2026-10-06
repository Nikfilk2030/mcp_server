import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def server_url(tmp_path_factory):
    external = os.environ.get("MCP_TEST_URL")
    if external:
        yield external
        return
    root = Path(__file__).resolve().parents[1]
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    log_path = tmp_path_factory.mktemp("server") / "server.log"
    with log_path.open("w+") as log:
        process = subprocess.Popen(
            [sys.executable, str(root / "server.py"), "--host", "127.0.0.1", "--port", str(port)],
            cwd=root, stdout=log, stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    break
                try:
                    with urllib.request.urlopen(f"http://127.0.0.1:{port}/healthz", timeout=0.5) as response:
                        if response.status == 200:
                            yield f"http://127.0.0.1:{port}/mcp"
                            return
                except OSError:
                    time.sleep(0.1)
            log.seek(0)
            pytest.fail("Server failed to start:\n" + log.read()[-6000:])
        finally:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


@pytest.fixture
async def session(server_url):
    async with streamable_http_client(server_url) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=5) as client:
            await client.initialize()
            yield client


@pytest.fixture
async def unicode_tool(session):
    tools = (await session.list_tools()).tools
    tool = next((tool for tool in tools if tool.name == "inspect_unicode"), None)
    assert tool is not None, "Implement and register inspect_unicode: docs/contracts.md"
    return tool


@pytest.fixture
async def identicon_tool(session):
    tools = (await session.list_tools()).tools
    tool = next((tool for tool in tools if tool.name == "render_identicon"), None)
    assert tool is not None, "Implement and register render_identicon: docs/contracts.md"
    return tool
