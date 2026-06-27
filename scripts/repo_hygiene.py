#!/usr/bin/env python3
"""Repository hygiene checks for local development and CI."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
CHECKS = ("secrets", "local-paths", "node-modules", "generated-artifacts")
TEXT_SIZE_LIMIT = 2_000_000

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9][A-Za-z0-9._-]{20,}"),
    re.compile(r"Bearer\s+(?!REDACTED|redacted|example|token|<|\[)[A-Za-z0-9._-]{30,}"),
    re.compile(
        r"(?i)(DASHSCOPE_API_KEY|OPENAI_API_KEY|QWENPAW_AUTH_PASSWORD)\s*=\s*"
        r"(?!$|<|\{|\$\{|REDACTED|redacted|example|placeholder|your_|xxx|fake_|secret)"
        r"[^\s'\"`]{8,}"
    ),
    re.compile(r"AKIA[0-9A-Z]{16}"),
]

LOCAL_PATH_PATTERNS = [
    re.compile(r"[A-Za-z]:[\\/](?:Users|rz|codex-home)[\\/][^\s'\"`)]+"),
    re.compile(r"/Users/[^/\s'\"`)]+/[^\s'\"`)]+"),
    re.compile(r"/home/[^/\s'\"`)]+/[^\s'\"`)]+"),
]

GENERATED_ARTIFACT_PATTERNS = [
    re.compile(r"^docs/research/assets/.+\.png$", re.IGNORECASE),
    re.compile(r"^apps/web/test-results/"),
    re.compile(r"^apps/web/playwright-report/"),
]


@dataclass(frozen=True)
class Finding:
    check: str
    path: str
    message: str


def run_git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=check,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def git_output(args: list[str], *, check: bool = True) -> str:
    return run_git(args, check=check).stdout


def nul_split(output: str) -> list[str]:
    return [item for item in output.split("\0") if item]


def tracked_files() -> list[str]:
    return nul_split(git_output(["ls-files", "-z"]))


def changed_files(base: str | None) -> list[str]:
    if not base or set(base) == {"0"}:
        return []
    merge_base = run_git(["merge-base", "--is-ancestor", base, "HEAD"], check=False)
    if merge_base.returncode != 0:
        return []
    return nul_split(git_output(["diff", "--name-only", "-z", f"{base}...HEAD"]))


def is_probably_text(path: Path) -> bool:
    try:
        if path.stat().st_size > TEXT_SIZE_LIMIT:
            return False
        data = path.read_bytes()
    except OSError:
        return False
    if b"\0" in data:
        return False
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def scan_text_files(patterns: Iterable[re.Pattern[str]], check_name: str) -> list[Finding]:
    findings: list[Finding] = []
    for rel_path in tracked_files():
        path = ROOT / rel_path
        if not path.is_file() or not is_probably_text(path):
            continue
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in patterns:
                match = pattern.search(line)
                if match:
                    findings.append(
                        Finding(
                            check=check_name,
                            path=f"{rel_path}:{line_no}",
                            message=f"matched {pattern.pattern}",
                        )
                    )
                    break
    return findings


def check_secrets(_: argparse.Namespace) -> list[Finding]:
    return scan_text_files(SECRET_PATTERNS, "secrets")


def check_local_paths(_: argparse.Namespace) -> list[Finding]:
    return scan_text_files(LOCAL_PATH_PATTERNS, "local-paths")


def check_node_modules(_: argparse.Namespace) -> list[Finding]:
    findings: list[Finding] = []
    for rel_path in tracked_files():
        parts = Path(rel_path).parts
        if "node_modules" in parts:
            findings.append(
                Finding(
                    check="node-modules",
                    path=rel_path,
                    message="tracked dependency directory is not allowed",
                )
            )
    return findings


def check_generated_artifacts(args: argparse.Namespace) -> list[Finding]:
    findings: list[Finding] = []
    for rel_path in changed_files(args.base):
        normalized = rel_path.replace(os.sep, "/")
        for pattern in GENERATED_ARTIFACT_PATTERNS:
            if pattern.search(normalized):
                findings.append(
                    Finding(
                        check="generated-artifacts",
                        path=rel_path,
                        message="generated evidence artifact changed without an explicit refresh task",
                    )
                )
                break
    return findings


CHECK_FUNCTIONS: dict[str, Callable[[argparse.Namespace], list[Finding]]] = {
    "secrets": check_secrets,
    "local-paths": check_local_paths,
    "node-modules": check_node_modules,
    "generated-artifacts": check_generated_artifacts,
}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="append",
        choices=CHECKS,
        help="Run only the selected check. May be repeated. Defaults to all checks.",
    )
    parser.add_argument(
        "--base",
        help="Base commit/ref for changed-file checks. If omitted, generated-artifacts has no diff scope.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    selected_checks = args.check or list(CHECKS)
    all_findings: list[Finding] = []

    for check_name in selected_checks:
        findings = CHECK_FUNCTIONS[check_name](args)
        all_findings.extend(findings)
        if findings:
            print(f"[fail] {check_name}: {len(findings)} finding(s)")
        else:
            print(f"[pass] {check_name}")

    if not all_findings:
        print("Repository hygiene checks passed.")
        return 0

    print("")
    print("Repository hygiene findings:")
    for finding in all_findings:
        print(f"- {finding.check}: {finding.path} - {finding.message}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
