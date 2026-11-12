#!/usr/bin/env python3
"""Preview and synchronize only labels.json; never delete or rename labels.

Requires Python 3.9+ and an authenticated GitHub CLI, including for --dry-run.
"""

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import subprocess

LABELS_FILE = Path(__file__).resolve().parent.parent / "labels.json"
REPO_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
COLOR_PATTERN = re.compile(r"^[0-9a-fA-F]{6}$")
LEGACY_LABELS = {"bug": "C-bug", "enhancement": "C-enhancement", "documentation": "C-docs"}


class SyncError(Exception):
    pass


def gh(*arguments, as_json=False):
    try:
        result = subprocess.run(
            ["gh", *arguments], check=False, capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise SyncError(str(error)) from error
    if result.returncode:
        raise SyncError((result.stderr or result.stdout).strip() or f"gh exited {result.returncode}")
    if as_json:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as error:
            raise SyncError("GitHub CLI returned invalid JSON") from error
    return result.stdout


def load_labels(path):
    labels = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(labels, list) or not labels:
        raise ValueError("labels.json must contain a non-empty array")
    names = set()
    for label in labels:
        if not isinstance(label, dict):
            raise ValueError("Each label must be an object")
        name, color, description = (label.get(key) for key in ("name", "color", "description"))
        if not isinstance(name, str) or not name.strip() or len(name) > 50:
            raise ValueError(f"Invalid label name: {name!r}")
        if name.casefold() in names:
            raise ValueError(f"Duplicate label name: {name}")
        if not isinstance(color, str) or not COLOR_PATTERN.fullmatch(color):
            raise ValueError(f"Invalid color for {name}: {color!r}")
        if not isinstance(description, str) or len(description) > 100:
            raise ValueError(f"Invalid description for {name}")
        names.add(name.casefold())
    return labels


def label_state(label):
    return {"color": label["color"].lower(), "description": label.get("description") or ""}


def read_labels(repo):
    pages = gh("api", "--method", "GET", f"repos/{repo}/labels?per_page=100",
               "--paginate", "--slurp", as_json=True)
    return {label["name"].casefold(): label for page in pages for label in page}


def make_plan(labels, existing, overwrite):
    plan = []
    for label in labels:
        previous = existing.get(label["name"].casefold())
        before = label_state(previous) if previous else None
        after = label_state(label)
        if before is None:
            action = "create"
        elif before == after:
            action = "unchanged"
        else:
            action = "update" if overwrite else "blocked"
        plan.append({"name": label["name"], "remote_name": previous["name"] if previous else None,
                     "action": action, "before": before, "after": after})
    return plan


def sync_repository(repo, labels, dry_run, overwrite):
    report = {"repository": repo, "status": "failed", "plan": [], "errors": [], "legacy_labels": []}
    print(f"\n== {repo} ==", flush=True)
    try:
        metadata = gh("api", "--method", "GET", f"repos/{repo}", as_json=True)
        if metadata.get("archived") or metadata.get("disabled"):
            raise SyncError("Repository is archived or disabled; no changes attempted")
        existing = read_labels(repo)
        for old, new in LEGACY_LABELS.items():
            if old in existing:
                report["legacy_labels"].append({"old": old, "new": new, "target_exists": new.casefold() in existing})
                print(f"  LEGACY {old} -> {new}: preserved; migration requires a separate decision")
        report["plan"] = make_plan(labels, existing, overwrite)
        for item in report["plan"]:
            print(f"  {item['action'].upper():9} {item['name']}")
            if item["action"] != "unchanged":
                print("    before:", json.dumps(item["before"], ensure_ascii=False))
                print("    after: ", json.dumps(item["after"], ensure_ascii=False))
            if item["action"] == "blocked":
                report["errors"].append(f"{item['name']}: differs; use --overwrite to update color/description")
            if dry_run or item["action"] not in ("create", "update"):
                continue
            # create without --force: a concurrently created label must not be overwritten.
            command = ("label", "create", item["name"]) if item["action"] == "create" else ("label", "edit", item["remote_name"])
            try:
                gh(*command, "--repo", repo, "--color", item["after"]["color"],
                   "--description", item["after"]["description"])
                item["result"] = "applied"
            except SyncError as error:
                item["result"] = "failed"
                report["errors"].append(f"{item['name']}: {error}")
        if not dry_run:
            actual = read_labels(repo)
            for label in labels:
                remote = actual.get(label["name"].casefold())
                if remote is None or label_state(remote) != label_state(label):
                    report["errors"].append(f"Verification mismatch: {label['name']}")
        if not report["errors"]:
            report["status"] = "planned" if dry_run else "verified"
    except SyncError as error:
        report["errors"].append(str(error))
    for error in report["errors"]:
        print(f"  ERROR {error}")
    counts = Counter(item["action"] for item in report["plan"])
    print(f"  {report['status'].upper()}: " + ", ".join(f"{key}={counts[key]}" for key in ("create", "update", "unchanged", "blocked")))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repositories", nargs="+", metavar="OWNER/REPO")
    parser.add_argument("--dry-run", action="store_true", help="Read remote state and show differences without writing to GitHub")
    parser.add_argument("--overwrite", action="store_true", help="Update differing standard labels; otherwise report them as blocked")
    parser.add_argument("--report", type=Path, help="Write a JSON plan/result report (may contain private repository names)")
    args = parser.parse_args()
    try:
        labels = load_labels(LABELS_FILE)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    for repo in args.repositories:
        if not REPO_PATTERN.fullmatch(repo):
            parser.error(f"Expected OWNER/REPO, got: {repo!r}")
    if shutil.which("gh") is None:
        parser.error("GitHub CLI 'gh' is required, including for --dry-run. Run 'gh auth login'.")
    # Open the report before any remote mutation so an unwritable destination fails early.
    report_file = None
    if args.report:
        protected = {LABELS_FILE.resolve(), Path(__file__).resolve()}
        if args.report.resolve() in protected:
            parser.error("Report must not overwrite labels.json or this script")
        try:
            report_file = args.report.open("w", encoding="utf-8")
        except OSError as error:
            parser.error(str(error))
    try:
        repositories = list({repo.casefold(): repo for repo in args.repositories}.values())
        results = [sync_repository(repo, labels, args.dry_run, args.overwrite) for repo in repositories]
        counts = Counter(result["status"] for result in results)
        report = {"dry_run": args.dry_run, "overwrite": args.overwrite,
                  "summary": dict(counts), "repositories": results}
        if report_file:
            json.dump(report, report_file, ensure_ascii=False, indent=2)
            report_file.write("\n")
    finally:
        if report_file:
            report_file.close()
    print(f"\nRepositories: verified={counts['verified']}, planned={counts['planned']}, failed={counts['failed']}.")
    print("Dry run only; no GitHub changes made." if args.dry_run else "Finished; no labels were deleted or renamed.")
    return 1 if counts["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
