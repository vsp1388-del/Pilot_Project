"""Write results/summary.md and results/summary.json from a Robot output.xml."""

import json
import sys
from pathlib import Path

from robot.api import ExecutionResult


def collect(output_xml: Path) -> dict:
    result = ExecutionResult(str(output_xml))
    stats = result.statistics.total
    suites = []

    def walk(suite):
        if suite.tests:
            suites.append(
                {
                    "suite": suite.longname,
                    "passed": sum(t.passed for t in suite.tests),
                    "failed": sum(t.failed for t in suite.tests),
                    "skipped": sum(t.skipped for t in suite.tests),
                    "failures": [
                        {"test": t.name, "message": t.message} for t in suite.tests if t.failed
                    ],
                }
            )
        for child in suite.suites:
            walk(child)

    walk(result.suite)
    return {
        "status": "PASS" if stats.failed == 0 else "FAIL",
        "total": stats.total,
        "passed": stats.passed,
        "failed": stats.failed,
        "skipped": stats.skipped,
        "elapsed_seconds": round(result.suite.elapsed_time.total_seconds(), 2),
        "suites": suites,
    }


def to_markdown(summary: dict) -> str:
    lines = [
        "# Data Validation Summary",
        "",
        f"**Overall status:** {summary['status']}  ",
        f"**Tests:** {summary['total']} total, {summary['passed']} passed, "
        f"{summary['failed']} failed, {summary['skipped']} skipped  ",
        f"**Duration:** {summary['elapsed_seconds']} s",
        "",
        "| Suite | Passed | Failed | Skipped |",
        "|---|---|---|---|",
    ]
    lines += [
        f"| {s['suite']} | {s['passed']} | {s['failed']} | {s['skipped']} |"
        for s in summary["suites"]
    ]
    failures = [(s["suite"], f) for s in summary["suites"] for f in s["failures"]]
    if failures:
        lines += ["", "## Failures", ""]
        for suite, f in failures:
            message = f["message"].replace("\n", " ")
            lines.append(f"- **{suite} / {f['test']}**: {message}")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    output_xml = Path(argv[1] if len(argv) > 1 else "results/output.xml")
    out_dir = Path(argv[2] if len(argv) > 2 else output_xml.parent)
    if not output_xml.exists():
        print(f"{output_xml} not found", file=sys.stderr)
        return 1
    summary = collect(output_xml)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "summary.md").write_text(to_markdown(summary), encoding="utf-8")
    print(f"{summary['status']}: {summary['passed']}/{summary['total']} passed -> {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
