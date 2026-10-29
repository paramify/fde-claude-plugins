---
name: fde-engagement
description: >
  Run a Paramify FDE client engagement in Linear with the team's templates:
  create the "<Client> - FDE Engagement" project from the "FDE/Client
  Fetcher+Validator Flow" template, add a system (a "Phase 2/3 - <System>"
  milestone plus the "FDE System Delivery" issue tree), track Build, Extend,
  Fix, Conditional and Validators issues, set issue and project statuses, and
  close out systems and engagements. Use when someone starts or sets up a
  client engagement, adds or scopes a system, creates or updates fetcher or
  validator issues in an engagement project, asks where an issue belongs or
  what status an issue or project should have, asks what a template issue
  means, or asks why a project's updates aren't reaching Slack. Use the
  fetcher-catalog skill alongside it for reuse checks and catalog updates.
---

# FDE engagements in Linear

Every client engagement is one Linear project in team **Forward Deployed
Engineers** (key `FDE`), made from the **FDE/Client Fetcher+Validator Flow**
project template, with one **FDE System Delivery** issue tree per system.

- **Worked example:** **Vastian - FDE Engagement** (`P-FDE-313`). When unsure
  how something is laid out, look at how Vastian does it.
- **For people:** the Slack canvas *FDE How-To: Client Engagements in Linear*
  (https://paramify.slack.com/docs/T039B6HQUGZ/F0C8Y5BQ56C) is the guide this
  skill follows. If the two disagree, the canvas wins; tell the user so the
  skill gets fixed.

## The templates

| Template | Type | What it makes |
|---|---|---|
| **FDE/Client Fetcher+Validator Flow** | project | The summary, a table of links (flowchart, Requirements Document, FDE Workstreams, Scope & Ownership Matrix, fetchers repo, Gap Analysis base), three milestones and 11 issues |
| **FDE System Delivery** | issue | 8 issues for one system (see [Add a system](#2-add-a-system)) |

| Milestone | Issues |
|---|---|
| Phase 1 - Preparation | Download Solution Capabilities · Provision Fetcher Repo · Paramify Workspace API Creation · Gather Requirements · Perform Gap Analysis · Designate System Scoping Documentation |
| Phase 4 - Client Production Deployment | Setup Client TUI Production Environment · Automate Deployment in Client Environment · Clients Run Orchestration |
| Phase 5 - End Active Engagement/ Continued Maintenance | Finish All Contracted Systems · Complete Fetcher/Validator Collection |

The flowchart numbers its phases differently:
- Linear's per-system "Phase 2/3" milestones hold the flowchart's phases 2–4
  (scoping, documentation and build).
- Linear's Phase 4 is the flowchart's Phase 5 (client production deployment).
- Linear's Phase 5 is the final sign-off and maintenance.

## 1. Start an engagement

1. **Check for an existing project.** Run `list_projects` with team FDE and the
   client's name. Projects from before the template (such as "<Client> -
   Fetchers") are not engagement projects. Don't build on them; move or link
   their open issues only with the lead's OK.
2. **Create the project.** Call `save_project` with:
   - `name` `<Client> - FDE Engagement`;
   - `template` `FDE/Client Fetcher+Validator Flow`;
   - `addTeams` `["Forward Deployed Engineers"]`;
   - `lead` (the FDE who owns the engagement), `startDate` and `priority`;
   - `links` for client-specific resources, such as the client's plan sheet
     (the Requirements Gathering workbook) and the client's Slack channel.

   Leave `description` out: passing one replaces the template's links table.
3. **Check what the template made.** Run `get_project` with
   `includeMilestones`, then `list_issues` for the project. You should see 3
   milestones and 11 issues, all in Backlog. Template issues can arrive a few
   seconds after the project, so list again before you add anything by hand.
4. **Things the API can't set; ask the lead to do them in the Linear app:**
   - **Members:** everyone working on the engagement.
   - **Slack:** click the bell in the project header, connect Slack, and pick
     **#fde-engagement-updates** with project updates on. Every engagement
     project posts there.

     To check it, `get_project` should show `slackChannelId`
     `C0CCMA23B98`. The channel also shows a "Notifications for <project> are
     now enabled" message.
5. **Prerequisites issue.** If some fetchers depend on the client's answers
   (licences, tools, APIs):
   - add a Phase 1 issue that lists those questions;
   - make it `blocks` every issue that relies on them.

   Vastian's is FDE-2.
6. **Project status.** Set `state` as the engagement moves (see
   [Project statuses](#project-statuses)):
   - Backlog → **Planned** when Phase 1 starts;
   - → **In Progress** at the first System Scope meeting.

**Phase 1** is the FDE's own work, done before the first System Scope meeting:

| Phase 1 issue | Done when |
|---|---|
| Download Solution Capabilities | The client's Solution Capabilities CSV is downloaded |
| Provision Fetcher Repo | The fetcher repo for this client is set up |
| Paramify Workspace API Creation | An API key exists for the client's Paramify workspace, for the TUI |
| Gather Requirements | The Requirements Gathering document is built from the client's Intake |
| Perform Gap Analysis | You know which systems need fetchers and validators, and which already have a base. Also run the fetcher-catalog skill's gap analysis, which finds fetchers that exist or that another engagement is building. |
| Designate System Scoping Documentation | The resources for each System Scope meeting are ready and reviewed by the assigned FDE |

- **Workbook steps:** the copy, the SolCap export, the Systems and Coverage
  tabs, and `fde-gaps` all run in the `fde` app from the private
  `paramify/fde-workbook` repo. Its README is the how-to.
- **Closing a step:** link what it produced on the issue, tick its End Result
  box if it has one, and move it to Done.

## 2. Add a system

Every system the gap analysis finds gets its own milestone and one System
Delivery tree. A system is one product or tool that evidence comes from: Azure
Commercial, Microsoft Entra ID, Microsoft Sentinel, or a client's own tool.

1. **Milestone.** Call `save_milestone` with `name` `Phase 2/3 - <System>`.
   - Its `description` says which resources the system covers.
   - If the system depends on a client answer, say so and link the
     prerequisites issue, as Vastian's QMS milestone does with FDE-2.
2. **Issue tree.** Call `save_issue` with `team` FDE, the `project`, `milestone`
   `Phase 2/3 - <System>` and `template` `FDE System Delivery`. Leave
   `description` out. The template makes:

   ```
   System Delivery
   ├── Collaborative Planning
   │   ├── System Scope
   │   ├── Review Coverage Tab
   │   ├── Conduct Coverage Meeting
   │   └── Review Documentation
   └── Build Phase
       └── Draft the Validator Draft Tab
   ```
3. **Check the milestone on all 8 issues.** Fix any that miss it with
   `save_issue` `milestone`.
4. **Add the system name to every title.** You get `System Delivery - Azure
   Commercial` (FDE-140), `Review Coverage Tab - Azure Commercial` and so on.
   Without the name, search shows eight identical "System Scope" issues.

## 3. Day-to-day work

All fetcher work goes under the system's **Build Phase** issue, one issue per
fetcher change, so each system's progress rolls up in one place.

**Before creating a Build issue,** run the fetcher-catalog skill's gap
analysis: reuse, extend, build, or join another engagement's open work. The
mistake to avoid is a second Build issue for a fetcher someone is already
building.

| Kind of work | Title | Label | Parent |
|---|---|---|---|
| New fetcher | `Build <fetcher_name> fetcher` | Feature | Build Phase - `<System>` |
| Change an existing fetcher | `Extend <fetcher_name>: <what changes>` | Improvement | Build Phase - `<System>` |
| Fix a fetcher | `Fix <fetcher_name>: <problem>` | Bug | Build Phase - `<System>` |
| Waits on a client answer | `[Conditional] Build <fetcher_name> fetcher` | Feature + Needs Validation | Build Phase - `<System>` |
| Validators for one evidence set | `Validators for <fetcher_name>` | Validator | Draft the Validator Draft Tab - `<System>` |

- **Fetcher names:** `<fetcher_name>` is the `name` in `fetcher.yaml`, or the
  planned name before the fetcher exists. The Fetcher Catalog matches on these
  titles, so keep to them exactly.
- **`[Conditional]` issues** stay in Backlog until the client answers the
  prerequisites issue. Then drop the prefix and the Needs Validation label,
  and plan the work. If the client doesn't need it, set it to Canceled.
- **Smaller tasks for one fetcher,** such as testing it against a real
  resource, go one level down as sub-issues of that fetcher's issue. Vastian's
  FDE-249 sits under FDE-14.
- **Every new issue needs its milestone set.** Milestones don't carry down to
  sub-issues, and without one the system's progress bar is wrong.
- **Due date:** the earliest due date of the workbook rows the issue closes.

**Descriptions** start with four lines, so anyone can see what an issue closes
in the plan sheet:

```
**Collects:** what the fetcher pulls, from which API
**Closes rows:** Coverage tab row numbers · **KSIs:** KSI-XXX-XXX
**System / access:** system name · read-only role it needs
**Testable now:** yes / no, and on what test data
```

[references/issue-formats.md](references/issue-formats.md) has the full
formats: the lines added once work starts, Fix issues, and Validators issues.

**Working an issue:**
1. Assign it (`assignee`) and move it to **In Progress**.
2. **Link the PR to its issues.** This applies to every repo, public or
   private.
   - **Branch:** the issue ID alone, lowercase: `fde-123`. Type it yourself.
     Don't use Linear's copied branch name (`gitBranchName` from `get_issue`,
     or Cmd/Ctrl + Shift + . in the app): it now carries your username and
     the issue title, and paramify-fetchers is public. Linear links the
     branch through the ID. Branches already pushed keep their names.
   - **PR description:** add one line for each issue the PR covers:
     - `Fixes FDE-123` when the PR finishes the issue;
     - `Part of FDE-123` when it's one of several PRs;
     - `Related to FDE-123` for a reference that shouldn't move the issue's
       status.

     The branch links only one issue, so this is how a PR covers several.
   - **Automations:** Linear then links the PR, and the FDE team's PR
     automations move the issue as the PR opens, is reviewed and merges.
     Check the status afterwards rather than assuming it.
   - **Nowhere else:** no issue IDs in PR titles, commit messages or code.
     Never put a client name in a branch, PR or commit; paramify-fetchers is
     public.
   - **Already-open PRs:** adding a `Fixes` line to one can move its issues
     backwards through the automations, for example from Under Client Review
     to In Progress. Ask the lead first.
3. Move it to **In Review** for FDE QA or code review, then follow the
   statuses below.
4. Add relations:
   - **Related to** for fetchers that overlap;
   - **Blocked by** for anything waiting on the client or on another issue
     (a Validators issue is `blockedBy` each fetcher issue it needs).
5. Comment at each step, in the same turn as the step: built, run on real
   data, PR opened, review fixed, merged, sent to the client, blocked. Keep
   the description's **Status** and **Remaining** lines current.

**Catalog.** Creating, renaming, splitting or canceling a fetcher issue, and a
PR merging, each trigger a Fetcher Catalog update in the same turn (see the
fetcher-catalog skill, "When to update it").

## Statuses

### Issue statuses

An issue's status always says who it is waiting on.

| Status | Use it when |
|---|---|
| Backlog | Created but not planned yet. Template issues start here, as do `[Conditional]` issues. |
| Todo | Ready for someone to pick up |
| In Progress | Someone is actively working on it |
| In Review | Waiting on FDE QA or code review (an open PR) |
| Under Client Review | Waiting on the client: approval, answers or access. A merged fetcher or delivered validators wait here for the client's approval. |
| Done | Finished and accepted. A fetcher or validator issue is Done only once the client approves it; never set Done on merge. |
| Canceled | Not doing it, for example a conditional fetcher the client doesn't need. Comment why. |
| Duplicate | Same work as another issue |

**Client approvals** happen in the plan sheet and in meetings, not in Linear:
- **While you wait:** move the issue to Under Client Review and comment with
  what you sent and when.
- **Approved:** move it to Done.
- **Changes requested:** move it back to In Progress and note what was asked.
- **Not In Progress while waiting:** use Under Client Review, so the board
  shows who the work is waiting on.

### Project statuses

Project statuses are shared with every team in the workspace. FDE uses only
these seven, and skips Discovery, Design Review, Ready for Dev and Trio Review.

| Status | Use it when |
|---|---|
| Backlog | The project exists, but Phase 1 hasn't started |
| Planned | Phase 1 is underway: our own planning, finished before client work starts |
| In Progress | Client work is active, from the first System Scope meeting through Phase 4 deployment |
| On Hold | The client has asked us to wait. Post a project update saying why and until when. Not for slow replies or missing access; use Under Client Review on the issues instead. |
| Maintenance | Active FDE work is done (Phase 5). The contract is still active, and ad hoc requests come in as new issues in the same project. |
| Completed | The contract has ended |
| Canceled | The engagement ended early or never started |

## Close-out

- **Finishing a system.** Once everything under Build Phase is Done and the
  Validator Draft Tab is filled out, close:
  - Build Phase - `<System>`;
  - Collaborative Planning - `<System>`;
  - System Delivery - `<System>`.

  The milestone then shows 100%.
- **Phase 4 - Client Production Deployment** runs once the systems are built:
  1. **Setup Client TUI Production Environment.**
  2. **Automate Deployment in Client Environment:** deploy the fetchers and
     validators where the client runs them.
  3. **Clients Run Orchestration:** the client confirms the automation works.
     If it fails, move steps 1 and 2 back to In Progress.
- **Phase 5:**
  - **Finish All Contracted Systems:** every `Phase 2/3` milestone is at 100%
    and the client has given final sign-off.
  - **Complete Fetcher/Validator Collection:** push public-repo improvements
    into the client's private repo, and bring sanitized, anonymized fetchers
    and validators back to the public repo.

  Then set the project to Maintenance, and to Completed when the contract
  ends.

## Rules

- **No client environment data in Linear.** Linear is open to the whole
  workspace. Keep out:
  - tenant, subscription, resource, user and workspace names;
  - ids;
  - real counts;
  - specific findings.

  Write "a real subscription" and describe behaviour in aggregate.
- **No client names in paramify-fetchers,** which is public. Linear IDs go
  only in the branch name (the ID alone, `fde-123`) and in PR descriptions (see
  "Working an issue").
- **Several people edit these projects.** Read an issue right before you change
  it. If an issue isn't yours, add a comment instead of rewriting its scope.
- **The client's workbook is shared with the client.** Write to it only
  through `fde-workbook` plans, or with the lead's OK.

## Common mistakes

- **A fetcher issue at the top level of the project.** It doesn't count toward
  its system. Set `parentId` to the system's Build Phase issue.
- **A new issue with no milestone.** Set the milestone whenever you create an
  issue.
- **Template titles left as they are.** Add the system name.
- **In Progress while waiting on the client.** Use Under Client Review.
- **Building a `[Conditional]` fetcher too early.** Keep it in Backlog until
  the prerequisites issue is answered.
- **A PR on a plain branch with no `Fixes FDE-n` line.** Linear can't link
  it, the automations don't run, and the issue doesn't show the work.
- **A branch from Linear's copied name, or `feat/...`.** The copied name puts
  the issue title in a public repo, and `feat/...` has no ID for Linear to
  link. Name new branches `fde-123`. The plugin's push hook stops Claude from
  pushing a new branch with any other name to a paramify repo.
- **An issue ID or client name in a PR title or commit message.** It stays in
  the public repo's history.

## Linear MCP quirks

- **A write can return `502 upstream_unavailable` without saving.** List the
  issues again before you retry. Then create a minimal issue and add the
  milestone, parent and relations in an update.
- **`patch` edits near issue mentions are unreliable.** Rewrite the whole
  `description` instead, writing mentions as plain links
  (`[FDE-155](https://linear.app/paramify/issue/FDE-155)`).
- **Echoes can be stale.** A save's echo, and a `get_issue` right after it, can
  show the old content. Confirm with a different `fields` list, or check
  `updatedAt`.
- **A template's body is replaced by any `description`.** Applying a template
  with a `description` replaces the template's body instead of merging with it.
