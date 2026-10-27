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

## Changing it

The skills reflect how the team runs engagements. When the process changes,
update the skill in the same PR as the template change, and bump `version` in
`.claude-plugin/plugin.json`.
