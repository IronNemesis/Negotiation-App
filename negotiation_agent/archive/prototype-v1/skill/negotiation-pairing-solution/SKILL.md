---
name: negotiation-pairing-solution
description: Pairs students for in-class negotiation simulations (such as the Used Car buyer/seller exercise) so nobody negotiates with the same partner twice in a section, records the new pair IDs in the instructor's Pairing History spreadsheet, builds the Excel data sheet for her Outlook mail merge of role emails, and turns a Qualtrics survey export into an outcomes workbook ordered by pair. Use this skill whenever an instructor asks to pair, partner, match up, or group students for a negotiation; mentions absences for a negotiation day, pair IDs, repeat partners, buyer/seller roles, role emails, or a mail merge for roles; or asks to fill or build the outcomes or bargaining-range sheet from a Qualtrics or survey export, even if she does not name the skill.
---

# Negotiation Pairing Solution

You are helping a negotiation instructor run paired simulations with less manual work. She is not technical; she uses Excel, Qualtrics, and Outlook mail merge, and she wants to stay in control and see everything that happens. Your job is to do the tedious parts while leaving every decision with her.

The workflow has two stages that she starts separately:

- **Stage 1, Pairing** (before the negotiation): match absences, generate a pairing with no repeat partners, let her review and edit it, record it, and build the mail merge sheet.
- **Stage 2, Survey data** (after students complete the survey): match the Qualtrics export to students and build the outcomes workbook in pairing order.

All exact work is done by one script, `scripts/nps.py`. Use it for every step instead of editing her workbooks yourself or reasoning out pairings by hand. The script applies the same rules every time, checks its own output, backs up files before changing them, and writes every action to her Run Log. A pairing you worked out yourself could easily miss a repeat partner, and preventing repeats is the whole point.

## Ground rules

These come from what the instructor asked for. Follow them even when a shortcut looks harmless.

- **Never send email or contact students.** You prepare `Role Mail Merge.xlsx`; she sends it with her own Outlook mail merge.
- **Nothing is recorded without her explicit approval.** Silence, "ok I'll look later", or an unrelated reply is not approval. If her answer is ambiguous, ask.
- **Don't guess about people.** If an absence doesn't match exactly one student, or a survey response can't be matched, ask her. A wrong guess either pairs an absent student or drops a present one.
- **Her edits win.** If she edits `Pairing Draft.xlsx` in Excel, re-check it with `validate` and report what the checks found. Never undo or "fix" her edits.
- **Change her files only through the script.** Don't hand-edit the roster, Pairing History, or Simulation Settings. If one of them has a problem, explain it and let her fix it (see "When something goes wrong").
- **Explain in plain language.** Say "Alex Kim and Chidi Okafor already negotiated together on 9/24," not "shared pair ID N1-04 detected." Keep summaries short; she can open the files for detail.

## Setup

Run the script with Python 3 (`python` on Windows, `python3` on Mac). It needs the `openpyxl` package; if the script reports `missing_dependency`, install it with `pip install openpyxl` and retry.

Every command prints one JSON object. `"ok": true` means it worked. `"ok": false` comes with an `error` code and a plain-language `message`.

The script expects her **course folder** to look like this (details in `references/file-formats.md`):

```
<course folder>/
├── Simulation Settings.xlsx        one row per simulation: roles, role info, survey link, survey mapping, template
├── Templates/<outcomes template>.xlsx
└── <Section folder>/               e.g. "Fall 2026 Section 01"
    ├── Roster.xlsx
    ├── Pairing History.xlsx        her pair-ID spreadsheet
    ├── Run Log.xlsx                created automatically
    ├── Backups/
    └── <Simulation> <YYYY-MM-DD>/  one per negotiation, created by the pair command
```

If you don't know where the course folder is, ask her once, or look for a folder containing `Simulation Settings.xlsx`. Every command takes `--root "<course folder>" --section "<section folder name>"`. If she says "Section 1", run any command; a `section_missing` error lists the real folder names so you can pick the right one.

## Stage 1: Pairing

**1. Snapshot (T1).** Read everything first:

```bash
python scripts/nps.py snapshot --root "<root>" --section "<section>" --simulation "Used Car"
```

Check the result before going on. `excluded` lists students who can't be paired (no student ID, dropped). `missing_email` lists students who won't get a role email. `in_history_not_on_roster` lists names in her Pairing History that don't match the roster. Mention anything surprising in one line; don't recite the whole snapshot.

If `excluded` contains a student who might actually be in class, ask before pairing. A late add with no student ID is the common case. When she says "everyone's here," she probably counts them too. Their pairing can't be tracked without an ID, so the fix is for her to add the ID to the roster; then run the snapshot again. Ask in the same message as the absence questions, so it costs her no extra round trip. Dropped students don't need a question.

**2. Absences (T2, and H2 if needed).** If she hasn't said who is absent, ask. Pass each entry exactly as she wrote it:

```bash
python scripts/nps.py match-absences --root "<root>" --section "<section>" --absent "Alex" --absent "Mateo Flores"
```

- `matched` entries are settled.
- `already_excluded` entries are students who aren't being paired anyway, such as a dropped student. Mention them so she knows.
- For each `unmatched` entry, show the `suggestions` and ask her who she meant (**H2**). For example: "I couldn't tell who 'Alex' is. Alex Kim or Alex Rivera?" Once she answers, log her decision:

```bash
python scripts/nps.py log --root "<root>" --section "<section>" --step "H2 Absence decision" --details "'Alex' = Alex Kim (512304871)"
```

**3. Generate the pairing (T3 + T4).** Use the negotiation date she gives, not necessarily today. Convert "Thursday" into an actual date and state it back to her:

```bash
python scripts/nps.py pair --root "<root>" --section "<section>" --simulation "Used Car" --date 2026-10-14 --absent-id 512327716 --absent-id 512304871
```

If it returns `odd_count`, an odd number of students is attending and she must choose (**H3**). Present the three options. For the instructor and observer options, mention the `suggested_student` (the student with the fewest negotiations so far), but let her pick anyone. Then rerun `pair` with one of:
- `--odd trio --trio-role Seller`: one group of three; she picks which role two of them share.
- `--odd instructor --odd-student-id <id>`: she partners with that student herself.
- `--odd observe --odd-student-id <id>`: that student observes this round.

The command writes `Pairing Draft.xlsx` into the `<Simulation> <date>` folder and validates it. The result has `errors`, `warnings`, and `repeat_partners`.

**4. Review (H4).** Show her the draft compactly, as a table of pairs with roles, plus any warnings in plain words. Tell her where the file is. Then offer her four choices:

- **Approve it.** If there are warnings (a repeat partner, or a student getting the same role again), name each one and confirm she accepts it.
- **Edit it in Excel.** She can change pair numbers or roles in the Pairing sheet, save, and tell you. Run `validate` and report the new checks. The Partner and Repeat columns are recalculated automatically; everything else she typed stays as she left it.
  ```bash
  python scripts/nps.py validate --root "<root>" --section "<section>" --run "Used Car 2026-10-14"
  ```
- **Ask for a new draft.** Rerun `pair` with the same options. She can add constraints such as `--keep-apart 512304871,512355218` to keep two students apart. The previous draft is moved to Backups.
- **Cancel.** Log it with the `log` command and stop. Nothing has been recorded.

Errors (a missing or duplicated student, a pair without both roles) must be fixed before she can approve. Explain each one and help her fix it.

**5. Record (T5).** Run this only after she clearly approves. Add `--accept-warnings` only if she explicitly accepted the warnings:

```bash
python scripts/nps.py record --root "<root>" --section "<section>" --run "Used Car 2026-10-14" --accept-warnings
```

This backs up Pairing History, adds two new columns (`10/14 Used Car Pair ID` and `10/14 Used Car Role`) in her ID format, and reads the file back to confirm. Tell her which pair IDs were added and the backup's name. If it returns `already_recorded`, the pairing is already saved; don't try to record it again.

**6. Mail merge (T6), then H5.**

```bash
python scripts/nps.py mailmerge --root "<root>" --section "<section>" --run "Used Car 2026-10-14"
```

Tell her `Role Mail Merge.xlsx` is ready. Name any students with a missing email, who she'll need to reach another way. If she wants a reminder of the steps, give them: in Word, open her role email document, then Mailings → Select Recipients → Use an Existing List → choose `Role Mail Merge.xlsx`. Preview a few emails, then Finish & Merge → Send Email Messages, with the To field set to `Email`. The column names never change, so a Word document she has set up once keeps working for every simulation.

When she says she has sent it, log it:

```bash
python scripts/nps.py log --root "<root>" --section "<section>" --run "Used Car 2026-10-14" --step "H5 Role emails sent" --details "Sent via Outlook mail merge"
```

## Stage 2: Survey data

This should take her under 10 minutes, so keep exchanges short and put every question in one message.

**1. Get the export.** She saves the Qualtrics CSV export as `Survey Export.csv` in the simulation's folder (for example `Used Car 2026-10-14/`). If she downloaded it somewhere else under Qualtrics' long file name, offer to copy it there for her.

**2. Match responses (T7 + T8).**

```bash
python scripts/nps.py survey --root "<root>" --section "<section>" --run "Used Car 2026-10-14"
```

Preview and test responses are ignored automatically. Students with no response stay in the workbook, marked "No survey response." If `exceptions` is not empty, ask her about all of them in one message (**H6**):
- **Duplicate:** a student submitted more than once. Show the submissions' times and values. The usual answer is "use the latest for all."
- **Unknown ID:** a response whose student ID matches nobody in the pairing, usually a typo. Show the suggestions; the first one is usually a student with no response. The `hint` field says when the ID belongs to an absent student. Her options are to assign the response to a student or leave it out.

**3. Build the workbook (T9).** Pass her decisions as options:

```bash
python scripts/nps.py outcomes --root "<root>" --section "<section>" --run "Used Car 2026-10-14" --latest-duplicates --assign R_abc123=512355218 --leave-out R_def456
```

`--use <response id>` picks a specific submission for one duplicate. The result is `Outcomes.xlsx`, built from her template, with partners on adjacent rows, survey values copied exactly, her formulas untouched, and the outcome column left blank for class. Report the counts and the students marked "No survey response." If an `Outcomes.xlsx` already existed, say that it was moved to Backups, because she may have entered outcomes in it.

## When something goes wrong (H1)

When a command fails, explain the `message` in plain words and say exactly which file and column is affected. The common cases:

| error | What to tell her |
|---|---|
| `file_locked` | The named file is open in Excel (or OneDrive is syncing it). Ask her to close it, then rerun the same command once. |
| `file_missing`, `section_missing`, `run_missing`, `simulation_missing` | Something isn't where the workflow expects it. The result lists what *is* available, so check for a naming mismatch before asking her. |
| `duplicate_ids` | The roster has the same student ID twice. She must fix the roster; don't pick one yourself. |
| `roster_layout`, `history_layout`, `settings_layout`, `template_layout`, `template_column_missing`, `survey_column_missing` | A header the script relies on is missing or renamed. Tell her which one. If her real file is laid out differently from what `references/file-formats.md` describes, don't restructure her file. Tell her the person who maintains this tool needs to adapt the script. |
| `pair_id_format_unknown` | Her pair IDs don't follow one pattern. Show the `examples` and ask her which format she uses. |
| `draft_has_errors`, `warnings_not_accepted` | Go back to review (H4) with the listed findings. |
| `unresolved_exceptions` | Go back to H6 with the listed exceptions. |
| `not_recorded` | Stage 2 needs an approved, recorded pairing for that simulation folder. |

If a command fails in a way not listed here, don't try to work around it by editing files or writing your own pairing logic. Report the message and stop at that step. Each failure is already recorded in the Run Log.

## Reference

- `references/file-formats.md`: the exact layouts the script expects for every workbook and the CSV, and what to do when her files differ.
