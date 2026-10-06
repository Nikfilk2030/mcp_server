import base64
import io
import json
from pathlib import Path

import jsonschema
from PIL import Image
import pytest
from mcp.shared.exceptions import MCPError


pytestmark = [pytest.mark.anyio, pytest.mark.assignment]
CASES = json.loads((Path(__file__).parent / "fixtures" / "identicons.json").read_text())


def decode_image(result):
    assert not result.is_error
    images = [block for block in result.content if block.type == "image"]
    assert len(images) == 1, "Return exactly one MCP image block"
    assert images[0].mime_type == "image/png"
    raw = base64.b64decode(images[0].data, validate=True)
    with Image.open(io.BytesIO(raw)) as image:
        assert image.format == "PNG"
        assert image.mode in {"RGB", "RGBA"}
        if image.mode == "RGBA":
            assert image.getchannel("A").getextrema() == (255, 255)
        return image.convert("RGB")


async def test_identicon_schema(identicon_tool):
    assert identicon_tool.description and identicon_tool.description.strip()
    validator = jsonschema.Draft202012Validator(identicon_tool.input_schema)
    for data in ({"seed": "x"}, {"seed": "😀" * 256, "cell_size": 64}, {"seed": "x", "cell_size": 8}):
        validator.validate(data)
    for data in ({}, {"seed": ""}, {"seed": "x" * 257}, {"seed": "x", "cell_size": 7},
                 {"seed": "x", "cell_size": 65}, {"seed": "x", "cell_size": 8.5}):
        assert not validator.is_valid(data), f"Input schema must reject {data!r}"


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
async def test_identicon_pixels(session, identicon_tool, case):
    result = await session.call_tool("render_identicon", case["arguments"])
    image = decode_image(result)
    cell_size = case["arguments"].get("cell_size", 32)
    assert image.size == (7 * cell_size, 7 * cell_size)
    pixels = image.load()
    for y in range(image.height):
        for x in range(image.width):
            cell_x, cell_y = x // cell_size, y // cell_size
            active = 1 <= cell_x <= 5 and 1 <= cell_y <= 5 and case["rows"][cell_y - 1][cell_x - 1] == "1"
            expected = tuple(case["color"]) if active else (255, 255, 255)
            assert pixels[x, y] == expected, f"Unexpected pixel at ({x}, {y})"
    assert image.tobytes() == image.transpose(Image.Transpose.FLIP_LEFT_RIGHT).tobytes()


async def test_identicon_upper_boundary_and_determinism(session, identicon_tool):
    arguments = {"seed": "😀" * 256, "cell_size": 64}
    first = decode_image(await session.call_tool("render_identicon", arguments))
    assert first.size == (448, 448)
    await session.call_tool("render_identicon", {"seed": "another"})
    second = decode_image(await session.call_tool("render_identicon", arguments))
    assert first.tobytes() == second.tobytes()


@pytest.mark.parametrize("arguments", [
    {}, {"seed": ""}, {"seed": []}, {"seed": "x" * 257},
    {"seed": "x", "cell_size": 7}, {"seed": "x", "cell_size": 65},
    {"seed": "x", "cell_size": 8.5},
])
async def test_identicon_rejects_invalid_input_and_recovers(session, identicon_tool, arguments):
    try:
        result = await session.call_tool("render_identicon", arguments)
    except MCPError as error:
        assert error.error.code == -32602
    else:
        assert result.is_error
        assert any(block.type == "text" and block.text.strip() for block in result.content)
    valid = decode_image(await session.call_tool("render_identicon", {"seed": "valid"}))
    assert valid.size == (224, 224)
