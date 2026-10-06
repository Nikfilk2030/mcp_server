import argparse
import os
from typing import Annotated

import uvicorn
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import Field
from starlette.responses import JSONResponse

from custom_tools import register_tools as register_custom_tools
from tools import register_tools


def create_app(public_host: str = "localhost"):
    mcp = MCPServer("Alice MCP Workshop", version="0.1.0")

    @mcp.tool(description="Return the supplied text unchanged. Use this tool to check that the MCP connection works.")
    def echo(text: Annotated[str, Field(max_length=256)]) -> str:
        return text

    @mcp.custom_route("/healthz", methods=["GET"])
    async def healthz(request):
        return JSONResponse({"status": "ok"})

    register_tools(mcp)
    register_custom_tools(mcp)
    return mcp.streamable_http_app(
        stateless_http=True,
        json_response=True,
        max_request_body_size=16384,
        transport_security=TransportSecuritySettings(
            allowed_hosts=["localhost:*", "127.0.0.1:*", public_host],
            allowed_origins=["http://localhost:*", "http://127.0.0.1:*", f"https://{public_host}"],
        ),
    )


def main():
    parser = argparse.ArgumentParser(description="MCP Workshop server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--public-host", default=os.environ.get("MCP_PUBLIC_HOST", "localhost"))
    args = parser.parse_args()
    uvicorn.run(create_app(args.public_host), host=args.host, port=args.port,
                access_log=False, limit_concurrency=8, timeout_keep_alive=5)


if __name__ == "__main__":
    main()
