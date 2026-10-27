# Issue description formats

Vastian's issues are the models. Build and Extend issues follow FDE-331, and
Validators issues follow FDE-383. "The workbook" is the client's copy of the
FDE KSI Fetcher Plan, the Requirements Gathering Document.

## Build, Extend and Fix

```
**Collects:** <what the fetcher reads and which API calls it makes, in one or two sentences. For Extend: what it adds to the existing calls.>

**Closes rows:** <Coverage-tab rows, each with its due date> · **KSI:** <KSI ids>
**System / access:** <system> · <roles or permissions it needs>
**Testable now:** <Yes or No: what real data and access exist, and what's needed from the client>

**Sheet items:** <R9-E1, R51-V3, …> (Coverage tab of the <Client> workbook: E = internal notes bullet, V = Suggested Evidence Validation bullet)

**Adds to the sheet:** <one sentence on what the workbook's fetcher column will say>
```

Once work starts, add these lines:

```
**Status:** <built / real-data run passed / in PR #n / merged in PR #n>
**Remaining:** <what's left, or "nothing">
**Path:** `fetchers/<platform>/<name>/` on <branch or main>
```

For **Fix** issues, open with what's wrong and how to see it, then the same
lines.

Find rows by their content, not their number. Workbooks get re-sorted, and an
old comment's row numbers can point at different rows today.

## Validators for `<fetcher>`

```
**Validates:** evidence from `<fetcher_name>` (<on main / planned in FDE-n>).

**Checks from the sheet's Suggested Evidence Validation column** (rows <n, n>):

| Row | KSI | Due | Check | State |
| -- | -- | -- | -- | -- |
| <row> | <KSI> | <due> | <the check, in plain words> | <Ready / Delivered / Shared check; needs FDE-n> |

**Ready now:** <x> of <y> checks. **Blocked by:** <FDE-n, …>

**How:** a validator reads only this fetcher's evidence file, so a check that spans several fetchers is covered here only for this fetcher's part. Draft each validator in the workbook's Validator Draft tab (anchor field, statement, what it does not prove, regex), prove it on real evidence, and move it to Validator Config after client review.
```

When validators are delivered, comment with what was added (validator names,
and what each one checks) and move the issue to Under Client Review.

## Template step issues

The template's own issues use the text they came with: a sentence, sometimes a
checklist, and an **End Result** checkbox. When the step is done:

- link what it produced, such as the workbook, gap analysis or meeting notes;
- tick the checkbox;
- move the issue to Done.

Don't rewrite the template text.
