"""Tests for template rendering.

``render_template`` replaces an earlier ``str.format`` call. The behaviour that
matters is that it never raises on template content the user controls: a
transcript can represent minutes of GPU time, so a typo in a template must
degrade gracefully instead of discarding the result.
"""

import pytest

from src.config import render_template


def test_substitutes_known_placeholders():
    result = render_template(
        "# {filename}\n\n{transcript_content}",
        {"filename": "talk.mp3", "transcript_content": "hello world"},
    )
    assert result == "# talk.mp3\n\nhello world"


def test_unknown_placeholder_is_left_intact():
    """str.format would raise KeyError here."""
    result = render_template("{filename} / {nonexistent}", {"filename": "a.mp3"})
    assert result == "a.mp3 / {nonexistent}"


def test_literal_braces_survive():
    """str.format would raise ValueError on the unmatched/JSON-ish braces."""
    template = 'Config: {"key": "value"} and {filename}'
    result = render_template(template, {"filename": "a.mp3"})
    assert result == 'Config: {"key": "value"} and a.mp3'


def test_json_code_block_is_not_mangled():
    template = "```json\n{\n  \"model\": \"medium\"\n}\n```\n{filename}"
    result = render_template(template, {"filename": "a.mp3"})
    assert '"model": "medium"' in result
    assert result.endswith("a.mp3")


def test_value_containing_braces_is_not_re_substituted():
    """A transcript that happens to contain {filename} must stay verbatim."""
    result = render_template(
        "{transcript_content}",
        {"transcript_content": "he said {filename} out loud", "filename": "a.mp3"},
    )
    assert result == "he said {filename} out loud"


def test_non_string_values_are_coerced():
    assert render_template("{count}", {"count": 42}) == "42"


def test_empty_template_returns_empty():
    assert render_template("", {"filename": "a.mp3"}) == ""


def test_no_placeholders_returns_template_unchanged():
    assert render_template("plain text", {"filename": "a.mp3"}) == "plain text"


@pytest.mark.parametrize(
    "template",
    ["{}", "{ spaced }", "{123numeric}", "{with-dash}", "{nested{inner}}"],
)
def test_malformed_placeholders_never_raise(template):
    """Whatever the user writes, rendering must not blow up."""
    result = render_template(template, {"filename": "a.mp3"})
    assert isinstance(result, str)
