# fde-linear

A Claude Code plugin for running Paramify FDE client engagements in Linear.

| Skill | Use it to |
|---|---|
| `fde-engagement` | Start an engagement from the project template, add a system with the System Delivery template, and keep fetcher and validator issues and their statuses current |
| `fetcher-catalog` | Check whether a fetcher already exists or is being built for another client, and keep the Fetcher Catalog project in step with the repo |

## Install

```
/plugin marketplace add paramify/fde-claude-plugins
/plugin install fde-linear@paramify-fde
```

Both skills use Linear's claude.ai connector, so connect Linear under
claude.ai → Settings → Connectors first. The catalog's full sync also needs
`gh` and `uv`.

## Briefing other sessions

Skills load when a task looks like it needs them. A background session or
subagent working from a brief may not notice that it does. Paste this block
into any brief that reads or writes Linear, builds, extends or renames a
fetcher, or writes a PR description:

> **Linear:** before any Linear read or write, load `/fde-linear:fde-engagement`, plus `/fde-linear:fetcher-catalog` for anything about a fetcher, and follow them. Before building a fetcher, run the catalog's reuse check (catalog, other engagement projects, open PRs) and report any Join/Extend match instead of building. When you create, rename or split a fetcher issue, update its catalog entry in the same turn. The branch is the issue's Linear `gitBranchName`. A new PR's description gets `Fixes FDE-n` (or `Part of` / `Related to`), with no IDs in titles, commits or code. Don't add those lines to PRs that are already open. Leave comments about a push to the session that pushes.

A session started before the plugin was installed doesn't have the skills.
Restart it first.

## Changing it

The skills reflect how the team runs engagements. When the process changes,
update the skill in the same PR as the template change, and bump `version` in
`.claude-plugin/plugin.json`.
