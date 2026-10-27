#!/usr/bin/env python3
"""Scan paramify-fetchers and compare it with the Linear Fetcher Catalog.

Run with:  uv run --with pyyaml scan_repo.py --repo <path to paramify-fetchers> [--catalog catalog.tsv] [--json out.json]

--catalog is a TSV you write from Linear (list_issues on project P-FDE-320):
    <identifier>\t<title>\t<status>
one line per catalog entry. With it, the script prints what needs doing.
Without it, it prints how many fetchers are on main per platform.

--json writes every fetcher on main as JSON, each with `entry_markdown`: the
exact description a Done catalog entry should have.
"""
import argparse, glob, json, os, subprocess, sys
from collections import Counter

import yaml

SKIP = {"demo"}
REPO_URL = "https://github.com/paramify/paramify-fetchers/tree/main/"


def commit_info(repo):
    try:
        out = subprocess.check_output(["git", "-C", repo, "log", "-1", "--format=%h %cs"], text=True).split()
        return out[0], out[1]
    except Exception:
        return "unknown", "unknown"


def scan(repo):
    fetchers = []
    for p in sorted(glob.glob(os.path.join(repo, "fetchers", "*", "*", "fetcher.yaml"))):
        platform = p.split(os.sep)[-3]
        if platform.startswith("_") or platform in SKIP:
            continue
        try:
            y = yaml.safe_load(open(p)) or {}
        except Exception as e:
            print(f"WARN could not parse {p}: {e}", file=sys.stderr)
            continue
        ev = y.get("evidence_set") or {}
        fetchers.append(dict(
            name=y.get("name"),
            platform=platform,
            path=os.path.relpath(os.path.dirname(p), repo),
            version=y.get("version"),
            runtime=(y.get("runtime") or {}).get("type"),
            description=" ".join((y.get("description") or "").split()),
            ksis=y.get("ksis") or [],
            evidence_ref=ev.get("reference_id"),
            evidence_name=ev.get("name"),
            secrets=[s.get("name") if isinstance(s, dict) else s for s in (y.get("secrets") or [])],
        ))
    return fetchers


def entry_markdown(f, sha, date, former=None):
    lines = [
        "**Status:** Available on `main`",
        f"**Code:** [{f['path']}]({REPO_URL}{f['path']}) · v{f['version']} · {f['runtime']}",
    ]
    if f["evidence_ref"]:
        lines.append(f"**Evidence set:** `{f['evidence_ref']}` — {f['evidence_name']}")
    lines.append("**KSIs:** " + (", ".join(f["ksis"]) if f["ksis"] else "none tagged"))
    lines.append("**Secrets:** " + (", ".join(f"`{s}`" for s in f["secrets"]) if f["secrets"] else "none listed in fetcher.yaml"))
    if former:
        lines.append(f"**Former names:** {former}")
    return ("\n".join(lines) + "\n\n" + f["description"] +
            f"\n\n---\nWhich clients use this fetcher: see the **Related** issues. "
            f"Repo facts from `main` @ `{sha}` ({date}). Kept current by the `fetcher-catalog` skill.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--catalog")
    ap.add_argument("--json")
    a = ap.parse_args()

    sha, date = commit_info(a.repo)
    fetchers = scan(a.repo)
    for f in fetchers:
        f["entry_markdown"] = entry_markdown(f, sha, date)
    on_main = {f["name"]: f for f in fetchers}
    print(f"main @ {sha} ({date}): {len(fetchers)} fetchers")

    if a.json:
        json.dump(fetchers, open(a.json, "w"), indent=1)
        print(f"wrote {a.json}")

    if not a.catalog:
        for k, v in sorted(Counter(f["platform"] for f in fetchers).items()):
            print(f"  {k:14s} {v}")
        return

    catalog = {}
    for line in open(a.catalog):
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3:
            catalog[parts[1].strip()] = (parts[0].strip(), parts[2].strip())

    missing = sorted(n for n in on_main if n not in catalog)
    merged = sorted(n for n, (_, st) in catalog.items() if n in on_main and st != "Done")
    gone = sorted(n for n, (_, st) in catalog.items() if st == "Done" and n not in on_main)

    print(f"\nOn main, no catalog entry ({len(missing)}): create as Done")
    for n in missing:
        print(f"  {n}  [{on_main[n]['platform']}]")
    print(f"\nCatalog entry not Done but now on main ({len(merged)}): set Done and fill repo facts")
    for n in merged:
        print(f"  {catalog[n][0]}  {n}  (was {catalog[n][1]})")
    print(f"\nCatalog says Done but not on main ({len(gone)}): renamed or removed? Ask before changing")
    for n in gone:
        print(f"  {catalog[n][0]}  {n}")


if __name__ == "__main__":
    main()
