"""Write GitHub job summaries and enforce dependency results using the stdlib."""

import argparse
import json
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


STAGES = {
    "validate": ("Source validation", "Compile source, tests and CI scripts; validate release version."),
    "quality": ("Code quality", "Ruff and actionlint checks; Pylint score at least 8/10 with no errors or fatal findings."),
    "security": ("Dependency security", "Audit resolved application and test dependencies for known vulnerabilities."),
    "unit-tests": ("Tests and coverage", "Run the complete suite with branch coverage; require at least 85%."),
    "platform-tests": ("Platform tests", "Run the suite on Windows, macOS and Linux with Python 3.12 and 3.13."),
    "gate": ("Quality gate", "Require every validation and test branch to succeed before packaging."),
    "package": ("Build distributions", "Build and validate a wheel and source archive; record SHA-256 checksums."),
    "install-smoke": ("Installed game smoke tests", "Install the wheel and exercise its module and command on all three OSes."),
    "release": ("GitHub Release", "Publish the tested packages only for a matching version tag on main."),
}


def write_summary(markdown):
    print(markdown)
    destination = os.environ.get("GITHUB_STEP_SUMMARY")
    if destination:
        with Path(destination).open("a", encoding="utf-8") as stream:
            stream.write(markdown + "\n")


def write_outputs(values):
    destination = os.environ.get("GITHUB_OUTPUT")
    if destination:
        with Path(destination).open("a", encoding="utf-8") as stream:
            for name, value in values.items():
                stream.write(f"{name}={value}\n")


def job_summary(args):
    lines = [f"## {args.title}", "", args.description, "", f"**Result:** {os.environ.get('JOB_RESULT', 'local')}"]
    outputs = {}
    if args.junit and Path(args.junit).is_file():
        cases = list(ET.parse(args.junit).getroot().iter("testcase"))
        failed = sum(case.find("failure") is not None or case.find("error") is not None for case in cases)
        skipped = sum(case.find("skipped") is not None for case in cases)
        lines += ["", "| Tests | Passed | Failed / errors | Skipped |", "| --- | --- | --- | --- |",
                  f"| {len(cases)} | {len(cases) - failed - skipped} | {failed} | {skipped} |"]
        outputs.update(tests_total=len(cases), tests_passed=len(cases) - failed - skipped,
                       tests_failed=failed, tests_skipped=skipped)
    if args.coverage_json and Path(args.coverage_json).is_file():
        totals = json.loads(Path(args.coverage_json).read_text(encoding="utf-8"))["totals"]
        percent = totals["percent_covered"]
        lines += ["", f"### Code coverage: {percent:.2f}%", "",
                  "Combined statement/branch coverage, measured by coverage.py. **Required: at least 85%.**"]
        outputs["coverage_percent"] = f"{percent:.2f}"
    if args.coverage and Path(args.coverage).is_file():
        coverage = ET.parse(args.coverage).getroot()
        lines += ["", f"**Line coverage:** {float(coverage.attrib['line-rate']):.1%}; "
                  f"**branch coverage:** {float(coverage.attrib['branch-rate']):.1%}. "
                  "The enforced 85% threshold uses pytest-cov's combined statement/branch total."]
        outputs.update(line_coverage=f"{float(coverage.attrib['line-rate']) * 100:.2f}",
                       branch_coverage=f"{float(coverage.attrib['branch-rate']) * 100:.2f}")
    if args.lint and Path(args.lint).is_file():
        report = json.loads(Path(args.lint).read_text(encoding="utf-8"))
        score = report["statistics"]["score"]
        counts = report["statistics"]["messageTypeCount"]
        lines += ["", f"### Lint score: {score:.2f}/10 (Pylint)", "",
                  "Application source: `snake_game/` and `main.py`. **Required: at least 8/10, with no errors or fatal findings.**",
                  "", "| Fatal | Errors | Warnings | Refactor | Convention |", "| --- | --- | --- | --- | --- |",
                  "| " + " | ".join(str(counts.get(key, 0)) for key in
                                     ("fatal", "error", "warning", "refactor", "convention")) + " |",
                  "", "The downloadable `pylint-report` artifact contains every finding. Ruff and actionlint also run as required checks."]
        outputs.update(lint_score=f"{score:.2f}", lint_findings=len(report["messages"]))
    if args.audit and Path(args.audit).is_file():
        report = json.loads(Path(args.audit).read_text(encoding="utf-8"))
        dependencies = report.get("dependencies", [])
        findings = sum(len(item.get("vulns", [])) for item in dependencies)
        lines += ["", f"**Dependencies audited:** {len(dependencies)}; **vulnerability findings:** {findings}."]
    if args.artifacts and Path(args.artifacts).is_dir():
        lines += ["", "**Built files:**"]
        lines += [f"- `{path.name}` ({path.stat().st_size:,} bytes)"
                  for path in sorted(Path(args.artifacts).iterdir()) if path.is_file()]
    if args.note:
        lines += ["", args.note]
    if os.environ.get("GITHUB_RUN_ID"):
        url = (f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
               f"/actions/runs/{os.environ['GITHUB_RUN_ID']}")
        lines += ["", f"[Run graph, logs and downloadable artifacts]({url})"]
    write_outputs(outputs)
    write_summary("\n".join(lines))


def dependency_summary(args):
    dependencies = json.loads(os.environ["NEEDS_JSON"])
    required = set(args.required.split(","))
    if os.environ.get("GITHUB_REF", "").startswith("refs/tags/v") and "release" in dependencies:
        required.add("release")
    lines = [f"## {args.title}"]
    if "quality" in dependencies and "unit-tests" in dependencies:
        lint = dependencies["quality"].get("outputs", {})
        tests = dependencies["unit-tests"].get("outputs", {})
        coverage = tests.get("coverage_percent")
        score = lint.get("lint_score")
        lines += ["", "### Code quality scorecard", "",
                  "| Metric | Measured result | Required |", "| --- | --- | --- |",
                  f"| **Code coverage** | **{coverage + '%' if coverage else 'Unavailable'}** | At least 85% combined statement/branch coverage |",
                  f"| Line coverage | {tests.get('line_coverage', 'Unavailable')}{'%' if tests.get('line_coverage') else ''} | Included in combined coverage |",
                  f"| Branch coverage | {tests.get('branch_coverage', 'Unavailable')}{'%' if tests.get('branch_coverage') else ''} | Included in combined coverage |",
                  f"| **Lint score (Pylint)** | **{score + '/10' if score else 'Unavailable'}** | At least 8/10; no error or fatal findings |",
                  f"| Lint findings | {lint.get('lint_findings', 'Unavailable')} | Details in pylint-report artifact |"]
        if "tests_total" in tests:
            lines.append(f"| Tests | {tests['tests_passed']}/{tests['tests_total']} passed; "
                         f"{tests['tests_failed']} failed; {tests['tests_skipped']} skipped | No test failures |")
        lines += ["", "Values come from this run's coverage.py and Pylint reports. Unavailable means no metric was produced."]
    lines += ["", "### Stage results", "", "| Stage | Result | Summary |", "| --- | --- | --- |"]
    for job_id, data in dependencies.items():
        name, description = STAGES[job_id]
        result = data["result"]
        if job_id == "release" and result == "skipped" and job_id not in required:
            result = "skipped (runs on version tags)"
        lines.append(f"| {name} | {result} | {description} |")
    failed = sorted(job_id for job_id in required if dependencies.get(job_id, {}).get("result") != "success")
    lines += ["", f"**Required checks:** {'FAILED: ' + ', '.join(failed) if failed else 'all passed'}." ]
    lines += ["", "Test XML, coverage HTML/XML, the dependency audit and distributable packages are available "
              "in this run's **Artifacts** section when their producing jobs reach those steps."]
    write_summary("\n".join(lines))
    return bool(failed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", default="")
    parser.add_argument("--junit")
    parser.add_argument("--coverage")
    parser.add_argument("--coverage-json")
    parser.add_argument("--lint")
    parser.add_argument("--audit")
    parser.add_argument("--artifacts")
    parser.add_argument("--note")
    parser.add_argument("--required", help="Comma-separated required job IDs; read their results from NEEDS_JSON.")
    args = parser.parse_args()
    if args.required:
        return dependency_summary(args)
    job_summary(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
