---
name: fetcher-catalog
description: >
  Keep the Linear "Fetcher Catalog" project (P-FDE-320) in step with the
  paramify-fetchers repo and with client engagement work: one issue per
  fetcher, Done when it's on main, client Build/Extend/Fix/Validators issues
  linked as Related, renames and splits recorded. Use whenever you create,
  rename, split, cancel or finish a fetcher issue in any FDE project; when a
  fetcher PR merges; when doing a client gap analysis or deciding reuse vs
  extend vs build; when someone asks "do we already have a fetcher for X",
  "which clients use X", or asks to sync, refresh or audit the fetcher catalog.
---

# Fetcher catalog

**Where:** Linear project **Fetcher Catalog** (`P-FDE-320`,
https://linear.app/paramify/project/fetcher-catalog-5bfac7677312), team
Forward Deployed Engineers. Seeded 2026-10-20 from `main` @ `5c0314a` (242
fetchers) plus the Vastian engagement (41 fetchers not yet merged).

**What it answers:** does a fetcher exist, is someone building it, and which
clients build, extend, validate or use it. The repo stays the source of truth
for *what a fetcher does*; the catalog adds what the repo can't hold (in-flight
work and client usage).

Use the Linear MCP tools (`save_issue`, `list_issues`, `get_issue`). The
`linear-api` skill's curl route returns 401 in this workspace.

## Entry format

- **Title:** the fetcher's exact `name` from `fetcher.yaml`
  (`azure_entra_service_principals`). Nothing else in the title.
- **Milestone:** the platform folder under `fetchers/`: Azure, AWS, GCP, Wiz,
  Datadog, Okta, CrowdStrike, Splunk, KnowBe4, SentinelOne, GitLab, Checkov,
  Kubernetes (`k8s`), Paramify, Rippling, ServiceNow, Better Stack, Jira, and
  **Client-specific systems** for a client's in-house tool (e.g.
  `vastian_qms_*`, `custom_cd_releases`). A new platform folder gets a new
  milestone named after the product.
- **Status:**

  | Status | Meaning |
  |---|---|
  | Done | On `main` |
  | In Progress | A Build issue is In Progress, In Review or Under Client Review |
  | Todo | A Build issue is Todo |
  | Backlog | Conditional or someday |
  | Canceled | Every Build issue was canceled and it never merged |

- **Related:** every client issue about this fetcher: Build, Extend, Fix,
  Validators, and verification issues (e.g. "Verify SQL MI fetchers…").
- **Description, on main:** generate it, don't hand-write it. Run
  `scripts/scan_repo.py --json` and use the fetcher's `entry_markdown`. If the
  entry has a **Former names** line, keep that line (insert it after
  **Secrets**).
- **Description, not on main:**

  ```
  **Status:** Not on `main` yet. Build issue: FDE-123 (In Review)
  **Former names:** planned as `old_name` (FDE-123)      ← only if any

  Code path, KSIs and evidence set get filled in from `fetcher.yaml` once it merges. Until then, the Build issue has the plan.

  ---
  Which clients use this fetcher: see the **Related** issues. Repo facts from `main` @ `<sha>` (<date>). Kept current by the `fetcher-catalog` skill.
  ```

  With no Build issue yet: `**Status:** Not on `main` and no Build issue found yet. First seen in FDE-123 (Todo)`.
  Canceled: `**Status:** Planned, then canceled. See FDE-123 for why.`

## Client issue titles

The catalog depends on these, so hold client issues to them (and fix titles
that drift):

- `Build <fetcher_name> fetcher`
- `Extend <fetcher_name>: <what>`
- `Fix <fetcher_name>: <what>`
- `Validators for <fetcher_name>`
- Renamed while building: `Build <new_name> fetcher (planned as <old_name>)`
- Waiting on a client answer: `[Conditional] Build <fetcher_name> fetcher`.
  Search on the fetcher name, not the full title, so the prefix doesn't hide
  it. Treat the issue as Backlog for the entry's status.

## When to update it

Do these in the same turn as the triggering change. Search the catalog by
title first (`list_issues` project `P-FDE-320`, `query` = name); never create a
second entry for a name that has one.

1. **A Build issue is created** in any FDE project → find the entry; if none,
   create it (status from the table, not-on-main description). Add the Build
   issue to its Related.
2. **Extend / Fix / Validators / Verify issue created** → add it to the
   entry's Related. If the fetcher has no entry, create one.
3. **Fetcher renamed** → retitle the entry, add or extend
   `**Former names:** planned as \`old\` (FDE-n)`, and retitle the client issue
   with `(planned as old)`.
4. **Fetcher split into several** (as FDE-14 SQL MI → 3, FDE-16 Sentinel → 4,
   FDE-28 Front Door → 4) → one entry per new fetcher, each with
   `**Former names:** split from planned \`old\` (FDE-n)` and the parent issue
   in Related. If an entry exists under the old name, cancel it with a
   comment naming the new entries.
5. **PR merges / fetcher lands on main** → status Done, description from
   `entry_markdown`, keeping Former names.
6. **Build issue canceled** → if no other open Build issue and not on main,
   status Canceled. Keep the entry: it records that a client once needed it.
7. **Fetcher removed from main** → don't delete or cancel on your own; tell
   the user which entries and ask.

## Gap analysis: reuse, extend or build

When scoping a client's system (Phase 1 *Perform Gap Analysis*, or
*Review Coverage Tab*):

1. Scan the repo (`scan_repo.py --json`) and match the client's system and
   KSIs against `platform`, `ksis` and `description`.
2. Look for work already under way that would cover the need. A fetcher being
   built for another client often isn't on main yet, so check all four places:
   - **The catalog.** Search for the system and candidate names. Entries that
     are In Progress, Todo or Backlog have the client issue in Related, which
     tells you whose it is and when it's due.
   - **The other engagement projects.** Run `list_issues` with team FDE, the
     system or fetcher name as `query`, and no status filter. Then drop Done
     and Canceled. Look for `Build …` and `Extend …` issues in any
     `- FDE Engagement` project. This finds issues nobody has linked to the
     catalog yet; link them now (step 2 of "When to update it").
   - **Open PRs and branches** in paramify-fetchers:
     `gh pr list --repo paramify/paramify-fetchers --state open --search "<system or name>"`.
     Also look for the fetcher's folder name in `git ls-remote --heads origin`.
   - **Shared needs.** In `paramify/fde-workbook`, run `fde-gaps --all`. It
     lists each system and KSI with every engagement that needs it.
3. Sort each need:
   - **Reuse:** Done, same system, same claim, same credential.
   - **Extend:** Done but missing something → `Extend <name>: …` issue.
   - **Build:** nothing fits → `Build <name> fetcher` issue.
   - **Join:** another engagement has an open Build or Extend issue, or an
     open PR, that would cover the need. Don't start a second build:
     - add your engagement's issue as `relatedTo` that issue, and to the
       catalog entry's Related;
     - comment on that issue with what your client needs and by when;
     - if it doesn't cover everything, open an `Extend` issue that is
       `blockedBy` it.
4. If two or more clients need a fetcher nobody has built, it belongs in
   **Fetcher Coverage** (`P-FDE-309`), per that project's rules. Link the
   Coverage issue to the catalog entry.

## Full sync

When asked to sync or audit, or when the catalog looks stale:

1. Get the repo: `git -C <clone> pull`, or
   `git clone --depth 1 https://github.com/paramify/paramify-fetchers.git` into
   the scratchpad.
2. List the catalog: `list_issues` project `P-FDE-320`, fields
   `["id","title","status"]`, limit 250, follow `cursor` until done. Write it to
   `catalog.tsv` as `id\ttitle\tstatus`.
3. Run:
   `uv run --with pyyaml <this skill's folder>/scripts/scan_repo.py --repo <clone> --catalog catalog.tsv --json fetchers.json`
4. Act on the three lists it prints: create missing entries as Done, flip
   merged entries to Done with fresh descriptions, and ask about entries that
   are Done but no longer on main.
5. Check FDE engagement projects for fetcher issues not yet linked (titles
   matching the formats above) and add them to Related.
6. Report counts: created, updated, linked, and anything left for the user.

For more than ~40 writes, put the payloads in JSON files and hand them to
parallel subagents, each appending `title\tFDE-n` to a results file, as the
seed did.

## Rules

- Client names stay in Linear. `paramify-fetchers` is public: never add client
  names to `fetcher.yaml`, code, or commit messages.
- Never complete the Fetcher Catalog project; it stays In Progress so Linear
  doesn't auto-archive its issues.
- Don't edit the description of a client's engagement issue to suit the
  catalog, except to fix a title to the formats above.
- Comparators (`comparators/`) aren't in the catalog yet; leave them out
  unless the user asks.
- Linear rewrites stored descriptions: URLs get wrapped in `<…>`, a blank
  line appears after `---`, and `FDE-n` becomes an issue link. Don't treat
  those differences as drift when comparing an entry with `entry_markdown`;
  compare the Status, Code, Evidence set, KSIs and Secrets lines instead.
- `save_issue` responses can show the issue as it was before the update. Check
  a write with `get_issue` (`includeRelations: true` for Related) rather than
  trusting the echo.

## Client engagements

Every engagement project is named `<Client> - FDE Engagement` and is made from
the FDE project template (see the fde-engagement skill). To find them all, run
`list_projects` with team FDE and `query` `FDE Engagement`.

As of 2026-10-27:

| Project | State |
|---|---|
| **Vastian** (`P-FDE-313`) | All Build/Extend/Fix/Validators issues are linked, as of 2026-10-20 |
| **HealthEdge** (`P-FDE-322`), **Decebo** (`P-FDE-323`), **Kentro** (`P-FDE-324`), **EPICOR** (`P-FDE-325`) | No fetcher issues yet; link them as they're created |

Projects from before the template:
- **TTEC - Splunk** (`P-FDE-307`): FDE-44 → the 7 `splunk_*` entries.
- **Epicor - Fetchers** (`P-FDE-308`): nothing linked.
