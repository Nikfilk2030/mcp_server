import copy
import json
from pathlib import Path

import jsonschema
import pytest
from mcp.shared.exceptions import MCPError


pytestmark = [pytest.mark.anyio, pytest.mark.assignment]
CASES = json.loads((Path(__file__).parent / "fixtures" / "unicode.json").read_text())


async def test_unicode_schema(unicode_tool):
    assert unicode_tool.description and unicode_tool.description.strip()
    assert unicode_tool.output_schema is not None, "Declare an output schema for structured data"
    validator = jsonschema.Draft202012Validator(unicode_tool.input_schema)
    for data in ({"text": ""}, {"text": "😀" * 256}, {"text": "x", "normalization": "NFKC"}):
        validator.validate(data)
    for data in ({}, {"text": []}, {"text": "x" * 257}, {"text": "x", "normalization": "BAD"}):
        assert not validator.is_valid(data), f"Input schema must reject {data!r}"


async def test_unicode_output_schema(unicode_tool):
    validator = jsonschema.Draft202012Validator(unicode_tool.output_schema)
    valid = next(case["expected"] for case in CASES if case["id"] == "mixed")
    validator.validate(valid)
    assert not validator.is_valid({}), "Output schema must require the documented fields"
    for field, wrong_value in (("length", "two"), ("utf8_bytes", []), ("normalized", []), ("characters", "text")):
        invalid = copy.deepcopy(valid)
        invalid[field] = wrong_value
        assert not validator.is_valid(invalid), f"Output schema must describe {field}"
    invalid = copy.deepcopy(valid)
    invalid["characters"][0]["index"] = "zero"
    assert not validator.is_valid(invalid), "Output schema must describe character objects"


@pytest.mark.parametrize("case", CASES, ids=[case["id"] for case in CASES])
async def test_unicode_results(session, unicode_tool, case):
    result = await session.call_tool("inspect_unicode", case["arguments"])
    assert not result.is_error
    data = result.structured_content
    assert isinstance(data, dict), "Return structuredContent, not just a JSON string"
    jsonschema.Draft202012Validator(unicode_tool.output_schema).validate(data)
    for field, expected in case["expected"].items():
        if field != "characters":
            assert data[field] == expected
        else:
            assert len(data[field]) == len(expected)
            for actual_char, expected_char in zip(data[field], expected, strict=True):
                for key, value in expected_char.items():
                    assert actual_char[key] == value
    assert type(data["length"]) is int
    assert type(data["utf8_bytes"]) is int


async def test_unicode_upper_boundary_and_independence(session, unicode_tool):
    first = await session.call_tool("inspect_unicode", {"text": "😀" * 256})
    assert not first.is_error
    assert first.structured_content["length"] == 256
    assert first.structured_content["utf8_bytes"] == 1024
    assert len(first.structured_content["characters"]) == 256
    await session.call_tool("inspect_unicode", {"text": "other"})
    repeated = await session.call_tool("inspect_unicode", {"text": "😀" * 256})
    assert repeated.structured_content == first.structured_content


@pytest.mark.parametrize("arguments", [
    {}, {"text": []}, {"text": "x" * 257}, {"text": "x", "normalization": "BAD"},
])
async def test_unicode_rejects_invalid_input_and_recovers(session, unicode_tool, arguments):
    try:
        result = await session.call_tool("inspect_unicode", arguments)
    except MCPError as error:
        assert error.error.code == -32602
    else:
        assert result.is_error, "Invalid arguments must not be a successful tool result"
        assert any(block.type == "text" and block.text.strip() for block in result.content)
    valid = await session.call_tool("inspect_unicode", {"text": "A"})
    assert not valid.is_error
    assert valid.structured_content["length"] == 1
