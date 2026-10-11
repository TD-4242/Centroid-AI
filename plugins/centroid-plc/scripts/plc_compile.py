#!/usr/bin/env python3
"""Compile-check a Centroid CNC12 PLC .src with mpucomp.exe (natively on Windows, via Wine elsewhere)."""
import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NamedTuple

from mpucomp_locate import locate

RUNNER = subprocess.run
FAILED_RE = re.compile(r"Compilation failed|^Error|Error Line", re.IGNORECASE | re.MULTILINE)

NOT_FOUND_HELP = """\
To check your PLC program for errors I need mpucomp.exe, Centroid's PLC compiler. It's the
same program CNC12 uses to build your PLC when you load it on the machine. It comes with every
CNC12 install, but it can't be shipped with these tools.

Where to look: on your control PC it's usually in C:\\cncm (mill) or C:\\cncr (router). If you
copied your CNC12 folder to this computer, look there. If you don't have CNC12 here, the free
CNC12 download from centroidcnc.com includes it.

Paste the path to mpucomp.exe (or its folder), or skip compiling for now."""


class SetupError(RuntimeError):
    pass


class Result(NamedTuple):
    ok: bool
    errors: list[str]
    warnings: list[str]
    summary: list[str]


def wine_help():
    if platform.system() == "Darwin":
        install = "brew install --cask wine-stable"
    elif shutil.which("dnf"):
        install = "sudo dnf install wine"
    else:
        install = "sudo apt install wine"
    return ("mpucomp.exe is a Windows program. On this computer it runs through Wine, a free "
            "tool that runs Windows programs on Linux and macOS, and Wine isn't installed.\n"
            f"Install it with:  {install}\nthen try again.")


def parse_log(log, returncode):
    lines = [l.strip() for l in log.splitlines() if l.strip()]
    failed = returncode != 0 or bool(FAILED_RE.search(log))
    errors = [l for l in lines if re.search(r"Error|Compilation failed", l, re.IGNORECASE)]
    if failed and not errors:
        errors = lines
    warnings = [l for l in lines if re.match(r"Warning:", l, re.IGNORECASE)]
    summary = [l for l in lines if re.search(r"Compilation successful|Program size", l, re.IGNORECASE)]
    return Result(not failed, errors, warnings, summary)


def build_command(compiler, src_name, out_plc, is_windows):
    cmd = [str(compiler), "-w", src_name, out_plc]
    return cmd if is_windows else ["wine", *cmd]


def compile_src(src, compiler, out=None, runner=None, is_windows=None):
    runner = runner or RUNNER
    if is_windows is None:
        is_windows = os.name == "nt"
    if not is_windows and shutil.which("wine") is None:
        raise SetupError(wine_help())
    src = Path(src).resolve()
    fd, tmp = tempfile.mkstemp(suffix=".plc")
    os.close(fd)
    try:
        env = dict(os.environ, WINEDEBUG="-all")
        r = runner(build_command(compiler, src.name, tmp, is_windows), cwd=src.parent,
                   capture_output=True, text=True, errors="replace", env=env)
        result = parse_log((r.stdout or "") + (r.stderr or ""), r.returncode)
        if result.ok and out:
            shutil.copyfile(tmp, out)
        return result
    finally:
        os.unlink(tmp)


def main(argv):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("src", type=Path)
    p.add_argument("-v", "--verbose", action="store_true", help="print every warning")
    p.add_argument("-o", "--output", type=Path, help="keep the compiled program here")
    p.add_argument("--compiler", help="path to mpucomp.exe or its folder")
    args = p.parse_args(argv)
    if not args.src.is_file():
        print(f"error: PLC source {args.src} not found")
        return 2
    try:
        found = locate(args.src, explicit=args.compiler)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}")
        return 2
    if found is None:
        print(NOT_FOUND_HELP)
        return 2
    if found.origin == "cnc12":
        print(f"CONFIRM COMPILER: {found.path}")
        return 3
    print(f"Compiling {args.src.name} with {found.path} ...")
    try:
        result = compile_src(args.src, found.path, args.output)
    except SetupError as e:
        print(e)
        return 2
    if not result.ok:
        print("\n".join(result.errors))
        print("ERROR: compilation failed")
        return 1
    print("\n".join(result.summary))
    print(f"Warnings: {len(result.warnings)}")
    if args.verbose and result.warnings:
        print("----\n" + "\n".join(result.warnings) + "\n----")
    if args.output:
        print(f"Wrote compiled program to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
