---
name: fde-engagement
description: >
  Run a Paramify FDE client engagement in Linear with the team's templates:
  find or create the client's initiative (led by the Forward Deployed
  Engineers team), ask which of the team's services the client wants
  (fetcher and validator, pipeline scripting, pipeline configuration), create
  each chosen service's "<Client> - <Service>" project under it, the fetcher
  and validator one from the "FDE/Client Fetcher+Validator Flow" template, add
  a system (a "Phase 2/3 - <System>" milestone plus the "FDE System Delivery"
  issue tree), track Build, Extend, Fix, Conditional and Validators issues,
  set issue, project and initiative statuses, keep each project's Effort and
  Scope labels and weekly health current, and close out systems and
  engagements. Use when someone starts or sets up a client engagement or a new
  service for a client, adds or scopes a system, creates or updates fetcher or
  validator issues in a client project, asks where an issue or project
  belongs, what status an issue, project or initiative should have, or what a
  template issue means, or asks why a project's updates aren't reaching Slack.
  Use the fetcher-catalog skill alongside it for reuse checks and catalog
  updates.
---

# FDE engagements in Linear

Every client is one Linear **initiative**, led by team **Forward Deployed
Engineers** (key `FDE`). Each service we deliver to that client is one
project under it. The fetcher and validator service is the project
**`<Client> - FDE Fetcher/Validator Service`**, made from the **FDE/Client
Fetcher+Validator Flow** project template, with one **FDE System Delivery**
issue tree per system.

- **Worked example:** Vastian's fetcher and validator project (`P-FDE-313`).
  When unsure how something is laid out, look at how Vastian does it.
- **For people:** the Slack canvas *FDE How-To: Client Engagements in Linear*
  (https://paramify.slack.com/docs/T039B6HQUGZ/F0C8Y5BQ56C) is the guide this
  skill follows. If the two disagree, the canvas wins; tell the user so the
  skill gets fixed.

## Clients, services and projects

| In Linear | Holds | Named |
|---|---|---|
| Initiative | One client | `<Client>` |
| Project | One service for that client | `<Client> - <Service>`, such as `<Client> - FDE Fetcher/Validator Service` |

- **Lead team:** every client initiative has Forward Deployed Engineers as
  its lead team. FDE is a private team, so only its members see these
  initiatives. An initiative without a lead team is visible to the whole
  workspace.
- **Owner:** the FDE who leads the client.
- **Project names keep the client prefix.** Projects also show in team lists,
  outside their initiative, where the prefix is the only thing that tells them
  apart.
- **Other services** get their own project under the same initiative, once
  they're in the [Services](#services) table. Work for the client that isn't
  fetchers or validators goes there, not in the fetcher and validator project.
  A project owned by another team keeps its team's visibility, but that team
  can't see the private client initiative.
- **Work for every client** stays outside client initiatives: Fetcher Catalog,
  Fetcher Coverage, Validator Library, Comparator Fetchers and Fetchers -
  Maintenance.

## Services

The services this skill can set up for a client. Ask which ones the client
wants when you start an engagement ([step 2](#1-start-an-engagement)).

| Service | Project | Templates | Set up with |
|---|---|---|---|
| FDE Fetcher/Validator Service | `<Client> - FDE Fetcher/Validator Service` | FDE/Client Fetcher+Validator Flow (project), FDE System Delivery (issue, one per system) | [Start an engagement](#1-start-an-engagement) steps 3–8, then [Add a system](#2-add-a-system) for each system |
| FDE Pipeline Scripting Service | `<Client> - FDE Pipeline Scripting Service` | Being set up | [Services without a template](#services-without-a-template) |
| FDE Pipeline Configuration Service | `<Client> - FDE Pipeline Configuration Service` | Being set up | [Services without a template](#services-without-a-template) |

When the team adds a service, add its row here and bump the plugin version.
A row can come before its template: until the template exists, the service is
set up with [Services without a template](#services-without-a-template). When
the template is made, name it in the row and give the service its own setup
steps in the same change. Until a service has a row, this skill doesn't set
it up.

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

1. **Find or create the client's initiative.** Run `list_initiatives` with the
   client's name as `query`. If there is none, call `save_initiative` with:
   - `name` `<Client>`;
   - `leadTeam` `Forward Deployed Engineers`;
   - `owner` (the FDE who leads the client) and `status` `Planned`;
   - `targetDate`, the contract's end date, if you know it.

   Check with `get_initiative` that the lead team is FDE before you add
   anything to it.
2. **Ask which services the client wants.** Use `AskUserQuestion` with
   `multiSelect: true` and one option per row of the [Services](#services)
   table: the service name as the label and its project as the description.
   Add "None yet: initiative only" as the last option. The tool takes at most
   4 options per question, so once the table has more than 3 rows, split the
   services across two questions in the same call.
   - Set up each chosen service from its row. Steps 3–8 below are the fetcher
     and validator service's; the pipeline services follow [Services without a
     template](#services-without-a-template).
   - **A service typed under Other that isn't in the table:** don't invent a
     project name or template for it. Tell the user it isn't in the plugin
     yet and gets added to the Services table once the team creates it. The
     initiative can still be made.
   - **No way to ask** (a subagent, or a run with no user): don't guess. Send
     the question back to whoever asked.
3. **Check for an existing project.** Run `list_projects` with team FDE and the
   client's name.
   - **Named `<Client> - FDE Engagement`, or not under the initiative:** it
     was made before client initiatives. With the lead's OK, rename it to
     `<Client> - FDE Fetcher/Validator Service` and add it to the initiative
     (`save_project` with `name` and `addInitiatives`), then use it.
   - **From before the template,** such as "<Client> - Fetchers": add it to
     the initiative so the client's work is in one place, but don't build on
     it. Move or link its open issues only with the lead's OK.
4. **Create the project.** Call `save_project` with:
   - `name` `<Client> - FDE Fetcher/Validator Service`;
   - `template` `FDE/Client Fetcher+Validator Flow`;
   - `addTeams` `["Forward Deployed Engineers"]`;
   - `addInitiatives` `["<Client>"]`;
   - `lead` (the FDE who owns the engagement), `startDate` and `priority`;
   - `labels` `["<Effort>", "Unscoped"]`, with a provisional Effort from the
     contracted systems (see [Effort and Scope labels](#effort-and-scope-labels)).
     Ask the lead if the contract doesn't tell you;
   - `links` for client-specific resources, such as the client's plan sheet
     (the Requirements Gathering workbook) and the client's Slack channel.

   Leave `description` out: passing one replaces the template's links table.
5. **Check what the template made.** Run `get_project` with
   `includeMilestones`, then `list_issues` for the project. You should see 3
   milestones and 11 issues, all in Backlog. Template issues can arrive a few
   seconds after the project, so list again before you add anything by hand.
   Check the project shows the client's initiative too.
6. **Things the API can't set; ask the lead to do them in the Linear app:**
   - **Members:** everyone working on the engagement.
   - **Slack:** click the bell in the project header, connect Slack, and pick
     **#fde-engagement-updates** with project updates on. Every client
     project posts there. Projects in a private team don't post to the
     workspace's default channel, so this step is needed for every project.

     To check it, `get_project` should show `slackChannelId`
     `C0CCMA23B98`. The channel also shows a "Notifications for <project> are
     now enabled" message.
   - **Initiative updates** are optional: post them only once a client has
     more than one service project. If you do, set the initiative's Slack
     channel from its own bell menu as well.
7. **Prerequisites issue.** If some fetchers depend on the client's answers
   (licences, tools, APIs):
   - add a Phase 1 issue that lists those questions;
   - make it `blocks` every issue that relies on them.

   Vastian's is FDE-2.
8. **Project and initiative status.** Set `state` as the engagement moves (see
   [Statuses](#statuses)):
   - Backlog → **Planned** when Phase 1 starts;
   - → **In Progress** at the first System Scope meeting, and the initiative
     → **Active** at the same time.

   Once every contracted system has had its Coverage Meeting, confirm Effort
   and set Scope to **Scoped**.

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

### Services without a template

The pipeline scripting and pipeline configuration services have no project
template yet. Set one up like this:

1. **Check for an existing project.** Run `list_projects` with team FDE and
   the client's name. Use a `<Client> - <Service>` project that's already
   there, and add it to the initiative if it isn't under it.
2. **Create the project.** Call `save_project` with:
   - `name` from the service's row;
   - `addTeams` `["Forward Deployed Engineers"]`;
   - `addInitiatives` `["<Client>"]`;
   - `lead`, `startDate` and `priority`;
   - `labels` `["<Effort>", "Unscoped"]`. The Effort criteria were written for
     fetcher work, so judge Effort by the FDE time, and ask the lead.
3. **Issues.** There's no template, so the project starts empty. Ask the lead
   which issues to add. Don't copy the fetcher and validator template's phases
   or issues into it.
4. **Members and Slack:** as in step 6. Every client project posts to
   #fde-engagement-updates.
5. **Statuses:** as in step 8. Planned while we plan, In Progress once client
   work starts, and the initiative goes Active with it.

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

### Initiative statuses

A client initiative's status follows its projects. FDE doesn't use Proposed.

| Status | Use it when |
|---|---|
| Planned | The client has signed, and none of its projects is In Progress yet |
| Active | Any of its projects is In Progress, On Hold or Maintenance |
| Completed | Every project is Completed or Canceled: the contract has ended |
| Canceled | The client ended before any work started |

## Effort and Scope labels

Every client project carries one label from each of two single-select
project label groups of the FDE team. Risk isn't a label: the health on the
weekly project update carries it.

- **If the groups don't exist** (`list_project_labels` with team FDE shows no
  Effort or Scope group), don't create them. Ask the lead to add them in the
  team's label settings.
- **`save_project`'s `labels` replaces the whole set.** Read the project's
  labels with `get_project` first, and send them all with the one value
  changed.

**Effort** is how much work the project was scoped to be. Set it provisionally
when the project is made, confirm it at the Coverage Meetings, and then leave
it alone, even at close-out.

| Effort | Criteria |
|---|---|
| Light | Existing fetchers cover nearly everything. Mostly validators and deployment, at most 2 fetcher extensions, no new fetchers. Under a quarter of one FDE's time. |
| Moderate | New fetchers or extensions on platforms we support. Up to one FDE's time. |
| Heavy | More than one FDE's time, or two FDEs. Also a new platform or a custom system. |

**Scope** says whether scoping is done.

| Scope | Criteria |
|---|---|
| Unscoped | New projects start here. Some contracted system hasn't had its Coverage Meeting, so its fetchers and validators aren't agreed and Effort is still provisional. |
| Scoped | Every contracted system's fetchers and validators are agreed, each with an issue and a due date, and access is granted. |

**Health** goes on each weekly project update (`save_status_update` with
`type` `project` and `health`). It changes only when someone posts an update,
so the update that changes it names the trigger and says whose turn it is,
ours or the client's.

| Health | When |
|---|---|
| On track | No trigger has fired. Before the Coverage Meetings, health covers only the Phase 1 work. |
| At risk | One trigger has fired. |
| Off track | Two triggers at once, or one trigger through two weekly updates. The project is taking capacity from other work: a resource drain. |

Triggers:
- scope added after the Coverage Meeting without the dates moving;
- blocked on the client (access, answers or reviews) for over a week;
- Fix issues or rework after delivery;
- more FDE time than planned;
- due dates missed two weeks in a row;
- crowding out another engagement's due dates.

Linear doesn't record most of these, so the update has to say so: being
blocked, extra FDE time and crowding out show only there.

| Labels and health | Reads as |
|---|---|
| Light · Scoped, On track | A light project |
| Moderate · Scoped, On track | A well scoped build |
| Heavy · Scoped, On track | Big, but planned that way: not a drain |
| Any · Scoped, Off track | A resource drain; Heavy is the worst case |
| Any · Unscoped | Waiting for its Coverage Meetings |

**At close-out,** Effort keeps its planned value. The close-out update says
which Effort level the project really took, backed by counts of its finished
Build, Extend, Fix and Validators issues and the weeks from start to finish.
Comparing the two across clients shows which kinds of client we
under-estimate.

**Initiatives get no Effort or Scope labels for now.** An initiative's Active
projects column already rolls up its projects' health. If initiative labels
are added later, Effort adds up (Light 1, Moderate 2, Heavy 4; a total of 1–2
is Light, 3–4 Moderate, 5 or more Heavy), and Scope is Unscoped while any
project is.

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

  Post the close-out update (see [Effort and Scope
  labels](#effort-and-scope-labels)). Then set the project to Maintenance, and
  to Completed when the contract ends. When every project under the client's initiative is Completed or
  Canceled, set the initiative to Completed.

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

- **A client project with no initiative,** or an initiative with no lead team.
  The project drops out of the client's view, and an initiative without FDE as
  its lead team is visible to the whole workspace.
- **Another service's work in the fetcher and validator project.** Give the
  service its own `<Client> - <Service>` project under the initiative.
- **Changing Effort after the Coverage Meetings.** Effort is the plan. A
  project that grew shows it in its health and its close-out update.
- **Health with no reason.** An update that moves health names the trigger,
  so the history explains it.
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
