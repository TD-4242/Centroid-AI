#!/usr/bin/env python3
"""Tests for plcfmt. Run with `python3 -m unittest tools.tests.test_plcfmt`.

Tests are plain functions using assert; load_tests adapts them for unittest. The
compile-gate integration tests need CENTROID_AI_TEST_SRC (a .src with mpucomp.exe
beside it) and Wine, and self-skip otherwise.
"""
import contextlib
import io
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "shared"))
sys.path.insert(0, str(REPO / "plugins" / "centroid-plc" / "scripts"))
import plcfmt
import mpucomp_locate

TEST_SRC = os.environ.get("CENTROID_AI_TEST_SRC")

Skip = unittest.SkipTest


def _raises(exc, fn, *a, **k):
    try:
        fn(*a, **k)
    except exc:
        return True
    raise AssertionError("expected %s to be raised" % exc.__name__)


# --------------------------------------------------------------------------- #
# Task 1: helpers, I/O, CRLF
# --------------------------------------------------------------------------- #
def test_split_comment_basic():
    assert plcfmt.split_comment("IF a THEN b  ; c") == ("IF a THEN b  ", "; c")
    assert plcfmt.split_comment("no comment here") == ("no comment here", "")
    assert plcfmt.split_comment(";banner") == ("", ";banner")


def test_format_text_preserves_crlf_and_single_final_newline():
    out = plcfmt.format_text("line1\r\nline2\r\n")
    assert out.endswith("\r\n")
    assert "\n" not in out.replace("\r\n", "")     # only CRLF, no lone LF
    assert out == "line1\r\nline2\r\n"


def test_format_text_strips_trailing_blank_lines_to_one_newline():
    assert plcfmt.format_text("a\r\n\r\n\r\n") == "a\r\n"


def test_read_src_rejects_non_ascii():
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.src")
        with open(p, "wb") as f:
            f.write("ok\r\n".encode("ascii") + b"\xe2\x80\x94\r\n")
        _raises(ValueError, plcfmt.read_src, p)


def test_read_src_rejects_bare_lf_or_cr():
    # lone LF input would otherwise flow through format_text and emit mixed
    # newlines, violating the CRLF-only contract
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.src")
        with open(p, "wb") as f:
            f.write(b"a\nb\r\n")
        _raises(ValueError, plcfmt.read_src, p)
        with open(p, "wb") as f:
            f.write(b"a\rb\r\n")
        _raises(ValueError, plcfmt.read_src, p)


# --------------------------------------------------------------------------- #
# Task 2: Rule 1 -- tabs
# --------------------------------------------------------------------------- #
def test_tabs_expanded_to_spaces():
    out = plcfmt.format_text("\tSV_X = 1\r\n")
    assert "\t" not in out
    assert out == "        SV_X = 1\r\n"


# --------------------------------------------------------------------------- #
# Task 3: Rule 4 -- IS alignment
# --------------------------------------------------------------------------- #
def test_align_is_pads_short_name_to_column_33():
    out = plcfmt.align_is("Foo_C IS 1    ;note")
    assert out == "Foo_C" + " " * 26 + " IS 1    ;note"
    assert out.index("IS ") == 32                  # 0-based 32 == column 33


def test_align_is_long_name_gets_single_space():
    long = "A_Really_Long_Symbol_Name_Over_31c_M"
    assert plcfmt.align_is(long + "   IS MEM5") == long + " IS MEM5"


def test_align_is_uppercases_the_keyword():
    assert plcfmt.align_is("Foo_M is MEM1").endswith(" IS MEM1")


def test_align_is_ignores_logic_lines():
    line = "IF True_M THEN SET Foo"
    assert plcfmt.align_is(line) == line


# --------------------------------------------------------------------------- #
# Task 4: Rule 5 -- comment spacing
# --------------------------------------------------------------------------- #
def test_comment_space_inserted():
    assert plcfmt.fix_comment_space("IS 1 ;note") == "IS 1 ; note"
    assert plcfmt.fix_comment_space("Foo IS 2  ;(2+256*0)") == "Foo IS 2  ; (2+256*0)"


def test_comment_space_leaves_banners_and_blank():
    assert plcfmt.fix_comment_space(";----------") == ";----------"
    assert plcfmt.fix_comment_space(";==== X ====") == ";==== X ===="
    assert plcfmt.fix_comment_space(";##########") == ";##########"
    assert plcfmt.fix_comment_space(";") == ";"


def test_comment_space_does_not_touch_pre_semicolon_gap():
    assert plcfmt.fix_comment_space("SET Foo    ;go") == "SET Foo    ; go"


# --------------------------------------------------------------------------- #
# Task 5: Rule 6 -- keyword case
# --------------------------------------------------------------------------- #
def test_keyword_case_uppercases_code_only():
    assert plcfmt.fix_keyword_case("if a then set b") == "IF a THEN SET b"


def test_keyword_case_does_not_touch_comments():
    assert plcfmt.fix_keyword_case("SET b  ; this is if then set") == \
        "SET b  ; this is if then set"


def test_keyword_case_whole_token_only():
    assert plcfmt.fix_keyword_case("RST ResetSet") == "RST ResetSet"
    assert plcfmt.fix_keyword_case("SET Ifget_M") == "SET Ifget_M"


# --------------------------------------------------------------------------- #
# Task 6: Rule 7 -- continuation alignment
# --------------------------------------------------------------------------- #
def test_continuation_comma_block_aligns_under_action():
    src = ("IF True_M THEN AAA = 1,\r\n"
           "\t BBB = 2,\r\n"
           "         CCC = 3\r\n")
    lines = plcfmt.format_text(src).split("\r\n")
    assert lines[0] == "IF True_M THEN AAA = 1,"
    assert lines[1] == " " * 15 + "BBB = 2,"
    assert lines[2] == " " * 15 + "CCC = 3"


def test_wrapped_condition_aligns_under_if():
    src = ("IF (A) ||\r\n"
           "\tB\r\n"
           "  THEN (X_M)\r\n")
    lines = plcfmt.format_text(src).split("\r\n")
    assert lines[0] == "IF (A) ||"
    assert lines[1] == "   B"
    assert lines[2] == "   THEN (X_M)"


def test_continuation_preserves_inline_comment_gap():
    src = ("IF True_M THEN AAA = 1,  ; first\r\n"
           "\tBBB = 2  ; second\r\n")
    lines = plcfmt.format_text(src).split("\r\n")
    assert lines[1] == " " * 15 + "BBB = 2  ; second"


def test_non_if_lines_unchanged_by_continuation():
    src = "SET Foo\r\nRST Bar\r\n"
    assert plcfmt.format_text(src) == src


def test_continuation_mid_block_comment_documented_behavior():
    # Known limitation: a full-line comment inside a block is re-indented to
    # the target column and terminates the block (rest left untouched).
    # Semantically safe and idempotent; no occurrences in the real source.
    src = ("IF A THEN X = 1,\r\n"
           "; note\r\n"
           "      Y = 2\r\n")
    out = plcfmt.format_text(src)
    lines = out.split("\r\n")
    assert lines[1] == " " * 10 + "; note"
    assert lines[2] == "      Y = 2"                   # untouched
    assert plcfmt.format_text(out) == out              # idempotent


# --------------------------------------------------------------------------- #
# Task 7: Rules 8-9 -- report-only
# --------------------------------------------------------------------------- #
def test_naming_report_flags_suffix_mismatch():
    text = "GoodOne_I IS INP5\r\nBadName_M IS INP6\r\n"
    msgs = [(ln, msg) for (ln, rule, msg) in plcfmt.report_findings(text)
            if rule == "naming"]
    assert len(msgs) == 1
    assert msgs[0][0] == 2
    assert "_I" in msgs[0][1]


def test_naming_report_ignores_alias_and_stage():
    text = "Foo_M IS Bar_M\r\nMainStage IS STG4\r\n"
    naming = [f for f in plcfmt.report_findings(text) if f[1] == "naming"]
    assert naming == []


# --------------------------------------------------------------------------- #
# Task 8: CLI + idempotency
# --------------------------------------------------------------------------- #
def test_idempotent():
    sample = ("if True_M then AAA = 1,\r\n"
              "\tBBB = 2\r\n"
              "Foo_C IS 1 ;x\r\n")
    once = plcfmt.format_text(sample)
    assert plcfmt.format_text(once) == once


def test_run_check_returns_1_when_changes_needed():
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.src")
        with open(p, "wb") as f:
            f.write(b"if a then b\r\n")
        with contextlib.redirect_stdout(io.StringIO()):
            assert plcfmt.run(p, fix=False, verify=False) == 1
        assert open(p, "rb").read() == b"if a then b\r\n"   # check writes nothing


def test_run_fix_writes_and_returns_0():
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.src")
        with open(p, "wb") as f:
            f.write(b"if a then b\r\n")
        assert plcfmt.run(p, fix=True, verify=False) == 0
        assert open(p, "rb").read() == b"IF a THEN b\r\n"


def test_check_findings_are_advisory_exit_0():
    # a formatted file with only naming findings must NOT fail check mode
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "x.src")
        text = "BadName_M" + " " * 22 + " IS INP6\r\n"     # formatted, bad suffix
        with open(p, "wb") as f:
            f.write(text.encode("ascii"))
        assert plcfmt.run(p, fix=False, verify=False) == 0


def test_verify_compiles_the_given_file():
    seen = []
    orig_compile, orig_fp = plcfmt._compile, plcfmt.plc_fingerprint
    plcfmt._compile = lambda src, out, compiler: seen.append(os.path.basename(src))
    plcfmt.plc_fingerprint = lambda p: ((), "A", "B")
    try:
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "any_name.src")
            with open(p, "wb") as f:
                f.write(b"if a then b\r\n")
            plcfmt.verify_compile_identical(p, "if a then b\r\n", "IF a THEN b\r\n", Path("x.exe"))
    finally:
        plcfmt._compile, plcfmt.plc_fingerprint = orig_compile, orig_fp
    assert seen == ["any_name.src", "any_name.src"]


def test_wizard_detection():
    assert plcfmt.looks_wizard_generated("; DO NOT MODIFY\r\n; #wizardregion Date\r\n")
    assert not plcfmt.looks_wizard_generated("; plain program\r\n")


def test_fix_on_wizard_file_warns_before_writing():
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "acorn.src")
        with open(p, "wb") as f:
            f.write(b"; #wizardregion Date\r\nif a then b\r\n")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            assert plcfmt.main(["--fix", "--no-verify", p]) == 0
        assert "Acorn Wizard" in err.getvalue()


def test_fix_without_compiler_refuses_and_explains():
    orig = plcfmt.locate
    plcfmt.locate = lambda *a, **k: None
    try:
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "x.src")
            with open(p, "wb") as f:
                f.write(b"if a then b\r\n")
            out = io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
                assert plcfmt.main(["--fix", p]) == 2
            assert open(p, "rb").read() == b"if a then b\r\n"
            assert "--no-verify" in out.getvalue()
    finally:
        plcfmt.locate = orig


def test_gate_reverts_when_fingerprint_extraction_fails():
    # If plc_fingerprint raises AFTER the candidate is written (bad .plc
    # header), the original bytes must be restored (monkeypatched, no compiler)
    orig_compile, orig_fp = plcfmt._compile, plcfmt.plc_fingerprint
    calls = []

    def fake_compile(src, out, compiler):
        with open(out, "wb") as f:
            f.write(b"dummy")

    def fake_fp(p):
        calls.append(p)
        if len(calls) == 1:
            return (("w",), "2", "4")
        raise RuntimeError("no checksum header found")

    plcfmt._compile, plcfmt.plc_fingerprint = fake_compile, fake_fp
    try:
        with tempfile.TemporaryDirectory() as td:
            p = os.path.join(td, "x.src")
            with open(p, "wb") as f:
                f.write(b"if a then b\r\n")
            _raises(RuntimeError, plcfmt.verify_compile_identical,
                    p, "if a then b\r\n", "IF a THEN b\r\n", Path("x.exe"))
            assert open(p, "rb").read() == b"if a then b\r\n"   # reverted
    finally:
        plcfmt._compile, plcfmt.plc_fingerprint = orig_compile, orig_fp


def test_main_reports_gate_error_cleanly():
    # RuntimeError surfaces as exit code 2, not a traceback
    orig = plcfmt._compile
    def failing(src, out, compiler):
        raise RuntimeError("compile failed")
    plcfmt._compile = failing
    try:
        with tempfile.TemporaryDirectory() as td:
            exe = os.path.join(td, "mpucomp.exe")
            open(exe, "wb").close()
            p = os.path.join(td, "other-name.src")
            with open(p, "wb") as f:
                f.write(b"if a then b\r\n")
            with contextlib.redirect_stderr(io.StringIO()):
                assert plcfmt.main(["--fix", "--compiler", exe, p]) == 2
            assert open(p, "rb").read() == b"if a then b\r\n"   # nothing written
    finally:
        plcfmt._compile = orig


# --------------------------------------------------------------------------- #
# Task 9: compile-checksum gate (integration; self-skips without compiler)
# --------------------------------------------------------------------------- #
def _test_source():
    if not TEST_SRC:
        raise Skip("CENTROID_AI_TEST_SRC not set")
    found = mpucomp_locate.locate(Path(TEST_SRC))
    if found is None:
        raise Skip("no mpucomp.exe next to the test source")
    return found.path


def _copy_src(td):
    target = os.path.join(td, os.path.basename(TEST_SRC))
    shutil.copyfile(TEST_SRC, target)
    return target


def test_real_src_reformats_fingerprint_identical():
    compiler = _test_source()
    with tempfile.TemporaryDirectory() as td:
        target = _copy_src(td)
        original = plcfmt.read_src(target)
        formatted = plcfmt.format_text(original)
        # (the committed .src may already be fully formatted; the gate must
        # hold either way)
        plcfmt.verify_compile_identical(target, original, formatted, compiler)  # must not raise
        assert plcfmt.read_src(target) == formatted


def test_gate_reverts_on_logic_change():
    # SET -> RST is a real logic edit: it moves the compiled program words.
    compiler = _test_source()
    with tempfile.TemporaryDirectory() as td:
        target = _copy_src(td)
        original = plcfmt.read_src(target)
        broken = original.replace("THEN SET ", "THEN RST ", 1)
        assert broken != original
        _raises(RuntimeError, plcfmt.verify_compile_identical, target, original, broken, compiler)
        assert plcfmt.read_src(target) == original       # reverted


def test_gate_reverts_on_io_rebind():
    # Rebinding a symbol's resource (INP1 -> INP2) leaves the logic words alone
    # but moves the I/O-map checksum C4; the gate must still catch it.
    compiler = _test_source()
    with tempfile.TemporaryDirectory() as td:
        target = _copy_src(td)
        original = plcfmt.read_src(target)
        broken = original.replace("IS INP1 ", "IS INP2 ", 1)
        assert broken != original
        _raises(RuntimeError, plcfmt.verify_compile_identical, target, original, broken, compiler)
        assert plcfmt.read_src(target) == original       # reverted


# --------------------------------------------------------------------------- #
# runner
# --------------------------------------------------------------------------- #
def _run():
    g = globals()
    tests = sorted(n for n in g if n.startswith("test_") and callable(g[n]))
    passed = failed = skipped = 0
    for n in tests:
        try:
            g[n]()
            print("PASS", n)
            passed += 1
        except Skip as e:
            print("SKIP", n, "-", e)
            skipped += 1
        except AssertionError as e:
            print("FAIL", n, "-", e)
            failed += 1
        except Exception as e:
            print("ERROR", n, "-", repr(e))
            failed += 1
    print("--- %d passed, %d failed, %d skipped" % (passed, failed, skipped))
    return 1 if failed else 0


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    for name in sorted(n for n in globals() if n.startswith("test_") and callable(globals()[n])):
        suite.addTest(unittest.FunctionTestCase(globals()[name]))
    return suite


if __name__ == "__main__":
    raise SystemExit(_run())
