import json
import subprocess

import pytest
from test_source_acquisition import no_network as no_network

from bsl.infrastructure.j13_authority import UnicodeHelper, decode

_UNICODE_HELPER = pytest.StashKey[UnicodeHelper]()


@pytest.fixture(scope="session")
def unicode_helper(request):
    if _UNICODE_HELPER in request.config.stash:
        return request.config.stash[_UNICODE_HELPER]
    helper = UnicodeHelper()
    request.config.stash[_UNICODE_HELPER] = helper
    request.session.addfinalizer(helper.close)
    request.config.pluginmanager.get_plugin("terminalreporter").write_line(
        "J13_NATIVE_RUNTIME "
        + json.dumps(
            {
                "swift_version": helper.runtime,
                "os_identity": helper.os_identity,
                "helper_source_sha256": helper.source_sha256,
            }
        )
    )
    return helper


REJECTED = (
    "# Heading",
    "> Block quote",
    ">Block quote",
    "- List item",
    "* List item",
    "+ List item",
    "1. Ordered item",
    "1) Ordered item",
    "---",
    "***",
    "___",
    "*emphasis*",
    "_emphasis_",
    "**strong**",
    "__strong__",
    "***strong emphasis***",
    "___strong emphasis___",
    "~~strikethrough~~",
    "[id]: ftp://example.invalid",
    "<https://example.invalid>",
    "<user@example.invalid>",
    "<!-- comment -->",
    "<!DOCTYPE example>",
    "mailto:user@example.invalid",
    "data:text/html,example",
    "ftp://example.invalid",
    "file:///tmp/example",
    "tel:+15555555555",
    "sms:+15555555555",
    "custom-scheme://example.invalid",
    " leading",
    "trailing ",
    "line\nbreak",
    "<b>markup</b>",
    "[label](destination)",
    "[label][reference]",
    "~~~fenced text~~~",
    "https://example.invalid",
    "www.example.invalid",
    "javascript:alert(1)",
    "plain `code`",
    "",
    "bad\u0001control",
    "ſms:",
    "ﬁle:",
    "a\u0301_x_",
    "²_x_",
    "\u200bplain",
)
ACCEPTED = (
    "The symbol # appears in the source.",
    "A * may mark a textual note in another context.",
    "The value is greater than > zero.",
    "John 3:16 is a Scripture reference.",
    "The issue ID tan:john.13.10:example is discussed as text.",
    "The profile: value is synthetic.",
    "Metadata: remains plain prose.",
    "English—Greek λόγος; Hebrew שָׁלוֹם; emoji 😀.",
    "An unmatched ` remains ordinary punctuation.",
    'Plain_identifier - brackets [remain], parentheses (remain), and apostrophe\'s quotation "marks".',
    "<\u0345>",
    "`\u0301a`",
    "ſ://x",
    "a\u0345_x_",
)


@pytest.mark.parametrize("value,valid", [(v, False) for v in REJECTED] + [(v, True) for v in ACCEPTED])
def test_frozen_foundation_profile(unicode_helper, value, valid):
    item = {"text": value, "plainText": True, "endpoints": []}
    result = unicode_helper.check([item])[0]
    assert (result["plainTextError"] is None) is valid
    assert result["scalarCount"] == len(value)


def test_real_utf16_and_grapheme_boundaries(unicode_helper):
    result = unicode_helper.check([{"text": "😀a\u0301", "plainText": False, "endpoints": [-1, 0, 1, 2, 3, 4, 5]}])[0]
    assert result["endpointErrors"] == [
        "invalidUTF16Range",
        None,
        "invalidStringBoundary",
        None,
        "graphemeSplit",
        None,
        "invalidUTF16Range",
    ]


@pytest.mark.parametrize("data", [b'{"a":1,"\\u0061":2}', b'{"a":NaN}', b'{"a":1e999}', b'"\\ud800"'])
def test_duplicate_nonfinite_and_surrogate_rejection(data):
    with pytest.raises((ValueError, UnicodeError)):
        decode(data)


@pytest.mark.parametrize(
    "response",
    [
        [],
        [{}],
        b"{",
        *[
            [{"plainTextError": None, "scalarCount": 5, "endpointErrors": []} | {key: value}]
            for key, value in (
                ("plainTextError", "unknown"),
                ("scalarCount", True),
                ("scalarCount", 4),
                ("endpointErrors", "bad"),
                ("endpointErrors", ["unknown"]),
            )
        ],
    ],
)
def test_malformed_helper_response_fails(unicode_helper, monkeypatch, response):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(
            [], 0, response if isinstance(response, bytes) else json.dumps(response).encode()
        ),
    )
    with pytest.raises(RuntimeError):
        unicode_helper.check([{"text": "hello", "plainText": True, "endpoints": []}])


def test_helper_failure_is_not_a_record_decision(unicode_helper, monkeypatch):
    def failure(*args, **kwargs):
        raise subprocess.TimeoutExpired("profile", 30)

    monkeypatch.setattr(subprocess, "run", failure)
    with pytest.raises(subprocess.TimeoutExpired):
        unicode_helper.check([])


@pytest.mark.parametrize("failure", ["missing", "compile", "timeout"])
def test_compiler_failure_cleans_temporary_directory(monkeypatch, tmp_path, failure):
    import tempfile

    import bsl.infrastructure.j13_authority as module

    directories = []
    original = tempfile.TemporaryDirectory

    def directory(**kwargs):
        result = original(dir=tmp_path, **kwargs)
        directories.append(result.name)
        return result

    def compiler(args, **kwargs):
        if failure == "missing":
            raise FileNotFoundError("swiftc unavailable")
        if args == ["swiftc", "--version"]:
            return subprocess.CompletedProcess(args, 0, b"synthetic compiler boundary")
        if failure == "compile":
            raise subprocess.CalledProcessError(1, args)
        raise subprocess.TimeoutExpired(args, 120)

    monkeypatch.setattr(module, "TemporaryDirectory", directory)
    monkeypatch.setattr(subprocess, "run", compiler)
    with pytest.raises((FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired)):
        UnicodeHelper()
    assert len(directories) == 1 and not list(tmp_path.iterdir())


def test_foundation_control_and_whitespace_boundaries(unicode_helper):
    controls = [chr(value) for value in (*range(0x20), *range(0x7F, 0xA0))]
    whitespace = [" ", "\t", "\n", "\r", "\u00a0", "\u200b", "\u2028", "\u2029", "\u202f"]
    values = ["before" + value + "after" for value in controls]
    values += [edge for value in whitespace for edge in (value + "text", "text" + value)]
    results = unicode_helper.check([{"text": value, "plainText": True, "endpoints": []} for value in values])
    assert all(result["plainTextError"] is not None for result in results)
    valid = unicode_helper.check([{"text": "Greek λόγος\u00a0Hebrew שָׁלוֹם 😀", "plainText": True, "endpoints": []}])[0]
    assert valid["plainTextError"] is None
