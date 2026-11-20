import argparse

import uvicorn
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.responses import JSONResponse

from tools import ping


def create_app():
    mcp = MCPServer("Клубное расписание", version="0.1.0")
    mcp.tool()(ping)

    @mcp.custom_route("/healthz", methods=["GET"])
    async def healthz(request):
        return JSONResponse({"status": "ok"})

    return mcp.streamable_http_app(
        stateless_http=True,
        json_response=True,
        max_request_body_size=16384,
        transport_security=TransportSecuritySettings(
            allowed_hosts=["localhost:*", "127.0.0.1:*"],
            allowed_origins=["http://localhost:*", "http://127.0.0.1:*"],
        ),
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(create_app(), host=args.host, port=args.port, access_log=False)
