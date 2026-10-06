import argparse
import asyncio
import base64
import json
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def run(args):
    async with streamable_http_client(args.url) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=15) as session:
            await session.initialize()
            if args.tool is None:
                result = await session.list_tools()
                print(result.model_dump_json(by_alias=True, indent=2))
                return
            result = await session.call_tool(args.tool, json.loads(args.arguments))
            for index, block in enumerate(result.content):
                if block.type == "text":
                    print(block.text)
                elif block.type in {"image", "audio"}:
                    print(f"{block.type}: {block.mime_type}, {len(block.data)} base64 characters")
                    if args.save_dir:
                        destination = Path(args.save_dir)
                        destination.mkdir(parents=True, exist_ok=True)
                        suffix = {"image/png": ".png", "audio/wav": ".wav"}.get(block.mime_type, ".bin")
                        path = destination / f"result-{index}{suffix}"
                        path.write_bytes(base64.b64decode(block.data, validate=True))
                        print(path)
            if result.structured_content is not None:
                print(json.dumps(result.structured_content, ensure_ascii=True, indent=2))
            if result.is_error:
                raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser(description="MCP client without an LLM")
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp")
    parser.add_argument("--tool")
    parser.add_argument("--arguments", default="{}")
    parser.add_argument("--save-dir")
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
