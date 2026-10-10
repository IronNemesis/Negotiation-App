---
name: bargaining-range-sheet
description: Cleans a Qualtrics survey export for an in-class negotiation simulation (currently the Used Car buyer/seller negotiation) and builds the instructor's bargaining range sheet for the debrief, with one row per match, the Buyer on the left, OUTCOME in the middle, and the Seller mirrored on the right, using the matches from her roster workbook. Fixes obvious typos in prices and highlights them, keeps unclear answers as typed, matches responses to students by name and email, and leaves ACTUAL IO and OUTCOME blank for class. Use this skill whenever the instructor mentions a Qualtrics or survey export or CSV for a negotiation, the bargaining range sheet, bargaining zones, reservation prices or BATNAs from the survey, cleaning the survey data, or rebuilding the sheet after absences, even if she doesn't name the skill.
---

# Bargaining Range Sheet

The instructor runs paired negotiation simulations. Before each one, students complete a Qualtrics survey with their initial offer, target, reservation price, and BATNA. Today she cleans the export by hand and re-types it into a sheet with one row per match, so the class can debrief each pair's bargaining zone. This skill does that work for her.

Her conventions are fixed and come from her own files; the script follows them exactly. You talk with her, show her what happened, and ask her about anything the script couldn't decide.

## Ground rules

- **Use the script for all data work.** `scripts/brs.py` cleans, matches, and builds by fixed rules, then checks its own output. Don't edit her CSV, her roster workbook, or the finished sheet by hand, and don't work out numbers yourself. A wrong number in the debrief misleads the class.
- **Never attach a response to a student on a guess.** Anything the script lists as unresolved is her decision.
- **Her roster workbook is read only.** This skill never writes to it. The pairing skill (`negotiation-pairing`) owns the matches.
- **Leave ACTUAL IO and OUTCOME to her.** She fills them in during class.
- **Plain language, short messages.** She is not technical. Say "Alyssa typed 10 for her target, so I read it as $10,000," not "corrected flag on Q5."

## Setup

Run the script with Python 3 (`python` on Windows, `python3` on Mac). It needs `openpyxl`; if the script reports `missing_dependency`, install it with `pip install openpyxl` and retry. Every command prints one JSON object: `"ok": true` on success, or `"ok": false` with an `error` code and a plain `message`.

You need two files from her:
- **Her roster workbook** (for example `BUS 4489 F26 Roster.xlsx`): the class list and the simulation tab (`UC`) with the matches.
- **The Qualtrics export** (a `.csv` she downloaded, often with a long name like `BUS+4489+F26+Week+2+-+Used+Car+Bargaining+Range_….csv`).

If she doesn't say where they are, ask once, or look in the folder she gave you for a `.csv` with "Bargaining Range" in its name and a workbook with "Roster" in its name. Confirm the files with her before building.

## Steps

**1. Prepare (T6 + T7).** This writes nothing:

```bash
python scripts/brs.py prepare --roster "<roster workbook>" --csv "<export>.csv"
```

Read the result. `matches_from` says whether the current matches are the **draft** (before class) or the **final** table (after absences). Tell her which, in passing.

**2. Show her what was found, in one message.** Keep it short:
- How many students and matches, and who has no response (`no_response`).
- What was cleaned (`cleaning`):
  - `corrected`: obvious fixes, shown in orange on the sheet. Examples: `10` read as 10,000, `8.8K` as 8,800, `$8,800 (sell to dealer)` as 8,800.
  - `unclear`: answers kept exactly as typed and shown in light red, for example `>8,800` or a range.
  - `out_of_range`: numbers kept but outside the usual range, also light red, for example a BATNA of 200.
- Role conflicts (`role_conflicts`): a student who picked the other role in the survey. Their assigned role is used and the cell is highlighted.
- Anyone left off the sheet (`left_off_sheet`), such as an absent student who answered anyway.
- `tab_warnings`, if any: names on her tab that aren't on the class list.

**3. Resolve anything unresolved (H4).** If `unresolved` isn't empty, put every item in that same message so she can answer at once:
- `unmatched`: show the typed name, email, the reason, and the `suggestions`. Ask whose response it is, or whether to leave it out.
- `duplicate`: show the submissions with their times and prices, and offer "use the latest" as the easy answer.

Turn her answers into options, using the response IDs from the result and names exactly as on her tab (`Last, First`):
- `--assign "R_abc123=Evans, Jordan"` gives a response to a student.
- `--leave-out R_abc123` leaves a response off.
- `--latest-duplicates` uses the latest submission for every duplicate; `--use R_abc123` picks one specific submission.

You can run `prepare` again with these options to confirm everything is resolved.

**4. Build (T8).** Ask for the week of the term if you don't know it. The export's file name may suggest it, but confirm, because her survey names aren't always right.

```bash
python scripts/brs.py build --roster "<roster workbook>" --csv "<export>.csv" --week 2 [her decisions]
```

The sheet is saved next to the export as `<course and term> Week <N> - Used Car Bargaining Range.xlsx`, with a `Roles` tab and a `Raw` tab holding the untouched export. Tell her where it is, the counts, and that the colors are explained in a legend under the table.

**5. Re-run after absences.** On class day, once the pairing skill has written the final matches with absences, run `build` again with the same options. The result will say `matches_from: final table`. The previous sheet goes to the `Backups` folder next to it. Absent students are left off and listed in `left_off_sheet`; tell her who.

If the existing sheet already has anything typed in ACTUAL IO or OUTCOME, `build` stops with `in_class_entries_present` and lists the cells. Tell her and ask before doing anything. Only if she confirms she wants it replaced, add `--replace-in-class-entries`; the old file is still kept in `Backups`.

## When something goes wrong (H1)

Explain the `message` plainly and say exactly which file is affected.

| error | What to tell her |
|---|---|
| `file_locked` | The named file is open in Excel or syncing in OneDrive. Ask her to close it, then run the same command once more. |
| `file_missing` | The file isn't where expected. Check the name and folder with her. |
| `survey_layout` | A question in the export is missing or renamed, so the survey was probably edited. Don't try to work around it; the skill's settings (`scripts/simulations.json`) need updating by whoever maintains the skill. |
| `sim_tab_missing`, `sim_tab_layout`, `class_list_missing`, `class_tab_ambiguous` | Her roster workbook isn't laid out as expected. Name the tab, and don't change her workbook. |
| `no_matches` | The matches haven't been drafted yet. That's the pairing skill's job, so do that first. |
| `unresolved_responses` | Go back to step 3 with the listed items. |
| `in_class_entries_present` | See step 5. |
| `course_unknown` | Ask her for the course and term (for example "BUS 4489 F26") and pass `--course`. |

Each run is recorded in `Negotiation Log.xlsx` next to her roster workbook. If an error isn't listed here, report the message and stop; don't improvise around it.

## Reference

`references/sheet-layout.md` describes the export columns, the cleaning rules, and the sheet layout in detail. Read it if she asks how a value was handled, or if something on the sheet looks wrong.
