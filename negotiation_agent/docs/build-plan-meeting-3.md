# Build Plan: Meeting 3 Changes

**Status:** Approved. Phases 1–5 are built and pushed; Phase 6 (the guide) and experimental dimensions remain.

This plan turns the Meeting 3 decisions into changes to the two skills, their task specifications, and their tests. Items that depend on an open question say which assumption they build on; see [`open-questions.md`](open-questions.md). Each phase ends at a review checkpoint with a pushed commit, and every change is tested against the fictional examples only.

## Order and Checkpoints

| Phase | What | Blocked by an open question? | Checkpoint |
|---|---|---|---|
| 1 | Absence and drop rules in `negotiation-pairing` | Partly ("moving forward" exception is left as is) | Push after tests pass |
| 2 | Bargaining range sheet: absent students, non-respondent list, day-of path | No | Push after tests pass |
| 3 | Qualtrics name dropdown | No (format assumed `Last, First`) | Push after tests pass |
| 4 | The 1v2 rule | Yes (who counts as "the 1") | Ask first, then build |
| 5 | Salary negotiation draft method | Yes (what the shift is applied to) | Ask first, then build |
| 6 | Step-by-step guide for the instructor | No, but best written last | Push for review |
| Later | Experimental dimensions | Yes (she hasn't said what she wants) | Not scheduled |

Phases 1–3 can be built now. Phases 4 and 5 should wait for her answers, since a wrong guess there changes who negotiates with whom.

## Phase 1: Absence and Drop Rules (`negotiation-pairing`)

**Dropped students.** Today T3 reports a drafted student who has left the class as an error. Change it to her rule:

- In the week they drop, a drafted student no longer on the class list is treated as absent: listed with `_0` under their own role's columns, and their partner is moved like any other stranded student. The chat summary says they appear to have dropped, so she can correct it if it was a name mismatch instead.
- On later simulations they are simply not on the class list, so they are left off. Their earlier pair IDs stay on earlier tabs and still count for repeat-partner checks.
- Name-mismatch protection stays: a drafted name that is "likely" a class-list student (same last name, different first name) is still asked about, not treated as dropped.

**Confirmed rules.** `UC_0` under the student's own role, and stranded students joining the previous match, are already built; move them from "assumption" to "confirmed" in the specs and `workbook-conventions.md`.

**Files:** `agent/task-specs/check-matches.md`, `apply-absences-and-write-final-matches.md`, `docs/workbook-conventions.md`, `skills/negotiation-pairing/references/pairing-rules.md`, `scripts/pairing.py`, `tests/test_negotiation_pairing.py`, plus a fictional example with a dropped student.

## Phase 2: Bargaining Range Sheet (`bargaining-range-sheet`)

**2a. Absent students stay on the sheet.** After the last match row, leave a blank row, then an "Absent" block: one row per absent student on their own role's side, with their survey answers if they submitted any, and `ACTUAL IO`/`OUTCOME` blank. They are excluded from row shading and from anything that treats rows as matches. The summary lists them instead of saying they were left off.

**2b. Survey non-respondent list (new task T10).** She asks "who hasn't done the survey?" and gets the students in the current matches with no matched response, as names plus a BCC-ready email list in the same format as the role lists. Responses that couldn't be matched to anyone are listed separately, since one of them may belong to a "missing" student. Nothing is sent.

**2c. Day-of path.** Add a documented option to skip the before-class build and build the sheet once in class from the final matches. This is mostly workflow and skill-instruction work, since T8 can already build from the final table: the skill should pick the final table when it has names, and say which table it used. The workflow diagram gets the alternate branch.

**Files:** `agent/task-specs/build-bargaining-range-sheet.md`, `match-survey-responses-to-students.md`, a new `agent/task-specs/list-survey-non-respondents.md`, `agent/workflow-of-tasks.md`, `skills/bargaining-range-sheet/SKILL.md`, `references/sheet-layout.md`, `scripts/brs.py`, `tests/test_bargaining_range_sheet.py`, expected results in `examples/expected/`.

## Phase 3: Qualtrics Name Dropdown

- A small command that prints the class list as `Last, First`, one per line, ready to paste into a Qualtrics dropdown question's choices.
- T6 and T7 learn a "name chosen from list" column in the settings file. When it's there, a response is matched by exact name first; the current first/last/email matching stays as the fallback, so older exports and free-typed surveys still work.
- Qualtrics exports dropdown answers as numeric codes by default, so the command also tells her to export "choice text" (or the skill maps codes back using the order it generated). To confirm on a real export before relying on it.

**Files:** `simulations.json` in both skills, `scripts/brs.py`, `match-survey-responses-to-students.md`, `clean-survey-export.md`, `workbook-conventions.md` (survey section), tests with a fictional dropdown export.

## Phase 4: The 1v2 Rule (after her answer)

Built on the assumption that "the 1" is the student alone on their side of a three-person match:

- T1 reads each student's history of being "the 1" from earlier tabs (a pair ID shared by three students, two of them in the other role).
- T2: with an odd count, choose the last match so its single student hasn't been "the 1" before (shift the extra student's match up one at a time until it fits).
- T9: when a stranded student would join a match whose single student has already been "the 1", ask her where they should go, as is done today for repeat partners.
- T3 warns about any repeat.

## Phase 5: Salary Negotiation Draft Method (after her answer)

Add `"draft_method": "rotate-second-half"` to `SL` in `simulations.json`: keep the left column's order, move each right-column student down one, and move the last one to the top. T3's repeat-partner and 1v2 checks run as usual, and any repeat is shown to her in review rather than fixed silently. Also needs her prepared `SL` template layout (UC and SL pair-ID history columns) checked against the fictional examples.

## Phase 6: Step-by-Step Guide

A plain-language guide for her, separate from the developer docs: installing the two skills in the Claude desktop app, then what to say to Claude at each stage (draft, role emails, survey, non-respondents, absences, day-of sheet), what she'll see, and what to do when Claude stops and asks. Written last so it matches what was built. Delivered as a document she can print.

## Not Changing

- No email is sent by the agent; non-respondent lists are for her own emails.
- `Gender` and `Intervention` stay hers. Experimental dimensions wait until she says what she wants.
- Her real files stay out of the repo. The local changes in `archive/prototype-v1/examples/` (test outputs from earlier runs) are not part of this plan and won't be committed.
