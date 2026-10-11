---
name: negotiation-pairing
description: Drafts student matches for an in-class negotiation simulation (currently the Used Car buyer/seller negotiation) in the instructor's own roster workbook, using her alphabetical method and her UC_1-style pair IDs; builds the BCC email lists for sending each role its packet; and on class day applies absences (UC_0, stranded partners join the previous match) and writes the final matches. Warns about repeat partners from earlier simulations. Use this skill whenever the instructor asks to pair, partner, match, or set up students for a negotiation, draft the matches, prepare role emails or BCC lists, says who is absent on a negotiation day, or asks to update or check the matches on a simulation tab, even if she doesn't name the skill.
---

# Negotiation Pairing

The instructor runs paired negotiation simulations. A few days before each one, she drafts the matches in her roster workbook, then emails each role its packet. On class day, she adjusts the matches for absent students. This skill does that work with her own method and conventions, so the result looks like what she would have written by hand.

## Ground rules

- **Use the script for every change.** `scripts/pairing.py` drafts, checks, and writes by fixed rules. It backs up the workbook first, then proves that only the intended cells changed. Don't edit her workbook by hand or work out matches yourself.
- **Nothing is written without her clear approval.** Show the draft or the final matches and wait for a clear yes. Silence, or "I'll look later", is not approval.
- **Never send email.** You prepare BCC lists; she sends the role emails with the packets attached.
- **Roles are locked once role emails go out.** Students already have their packets. Absences can move a student to another match, never change their role.
- **Never guess about people.** If an absent name or a name on her tab could be more than one student, ask.
- **Her edits win.** If she edits the draft in Excel, re-check it and report; don't undo her changes.
- **Plain language, short messages.** She is not technical, and on class day she's in front of the class.

## Setup

Run the script with Python 3 (`python` on Windows, `python3` on Mac). It needs `openpyxl`; if the script reports `missing_dependency`, install it with `pip install openpyxl` and retry. Every command prints one JSON object: `"ok": true` on success, or `"ok": false` with an `error` code and a plain `message`. All commands take `--roster "<her roster workbook>.xlsx"` and `--simulation UC` (the default).

If you don't know where her roster workbook is, ask once, or look in the folder she gave you for an `.xlsx` with "Roster" in its name. The workbook needs the class list on the attendance tab (`Att - Fall` or `Att - Spring`), and a tab for the simulation (`UC`) that she has prepared with headers and match numbers. Start with:

```bash
python scripts/pairing.py snapshot --roster "<roster>.xlsx"
```

This shows the class size, missing emails, whether the draft and final tables are filled in, and whether roles are already locked. Mention anything surprising in one line.

## Stage 1: Draft (a few days before class)

**1. Preview (T2 + T3).** If she mentioned students who will be absent, pass them as she said them:

```bash
python scripts/pairing.py draft --roster "<roster>.xlsx" [--absent "Name"]
```

The draft uses her method: the class sorted alphabetically, the first half as Buyers and the second half as Sellers, matched in order. With an odd count, the extra student is a second Seller in the last match.

One effect to explain if it comes up: leaving out a student known to be absent shifts the halves, so the pairs after that point in the alphabet change. That is how her method works, not a mistake.

**2. Review (H2).** Show the draft as a compact table (match, Buyer, Seller) and any `warnings` (repeat partners from earlier simulations) or `errors`. She can:
- **Approve** it.
- **Ask for swaps.** Re-run `draft` with `--swap "Last, First;Last, First"` (two names from the class list, separated by `;`). Each keeps the other's role and match.
- **Cancel.** Log it and stop.

Errors must be fixed before writing. Warnings need her explicit OK.

**3. Write (T4)** after a clear approval, with the same options she approved:

```bash
python scripts/pairing.py write-draft --roster "<roster>.xlsx" [same --absent/--swap options] [--accept-warnings]
```

- **Draft table already has names (`draft_exists`):** show her what's there and ask before using `--replace`.
- **She edits the draft in Excel afterwards:** run `check` and report the findings; her edits stay.

  ```bash
  python scripts/pairing.py check --roster "<roster>.xlsx"
  ```

**4. BCC lists (T5).**

```bash
python scripts/pairing.py bcc --roster "<roster>.xlsx"
```

Give her each role's list, ready to paste into Outlook's BCC field, and say where the text file is saved. Name anyone missing an email, so she can reach them another way.

**5. Role emails sent (H3).** When she says the role emails went out, record it. This locks roles for the simulation:

```bash
python scripts/pairing.py roles-sent --roster "<roster>.xlsx"
```

If she later asks for a change that alters a student's role, the script refuses with `roles_locked`. Tell her the students affected already have the other packet. Only if she confirms she'll re-send, add `--confirm-role-change`.

## Stage 3: Absences (start of class)

**6. Report absences (H5).** Ask who is absent if she hasn't said. "Nobody" is a valid answer. Pass names as she said them (a last name, a full name, or an email):

```bash
python scripts/pairing.py absences --roster "<roster>.xlsx" --absent "Evans" --absent "ksilva@example.edu"
```

This writes nothing. It applies her rule:
- Absent students get `UC_0`.
- A partner left without anyone in the other role joins the match just before theirs, in the same role.
- Match numbers keep their gaps; nobody's role changes.

Results that need her answer:
- **`absence_unclear`:** a name fits more than one student or no one. Ask with the suggestions.
- **`needs_placement`:** a stranded student can't join the previous match, because it would have more than three students or repeat a partner. Ask where they should go, then pass `--place "Last, First=MATCH"`.
- **An error that a tab name "may be" a class-list student:** her draft uses a different first name (for example a legal name). Ask her to confirm, then pass `--same-person "Tab Name=Class Name"`.
- **Class-list students who aren't in the draft:** usually absent students she already knew about. Confirm, then include them with `--absent`.

**7. Confirm (H6).** Show the final matches compactly, plus each move in one line, as listed in `moves`. On her clear yes, write the final table with the same options:

```bash
python scripts/pairing.py write-final --roster "<roster>.xlsx" --absent "…" [--place …] [--same-person …] [--accept-warnings]
```

- **Final table already has entries (`final_area_not_empty`):** ask before adding `--replace`.
- **A `note` about Gender or Intervention:** pass it on. Those columns are hers and are never changed, so she should check they still line up.

Then tell her to re-run the bargaining range sheet (`bargaining-range-sheet` skill), which will now use the final matches.

## Logging her decisions

Record decisions the script doesn't see, such as a cancellation or a confirmed placement:

```bash
python scripts/pairing.py log --roster "<roster>.xlsx" --step "H2 Draft review" --details "Canceled by the instructor"
```

Every command also logs itself in `Negotiation Log.xlsx` next to her workbook.

## When something goes wrong (H1)

Explain the `message` plainly and say exactly which file and tab is affected.

| error | What to tell her |
|---|---|
| `file_locked` | The workbook is open in Excel or syncing in OneDrive. Ask her to close it, then run the same command once more. |
| `sim_tab_missing`, `sim_tab_layout`, `tab_too_short` | The simulation tab isn't prepared as expected (missing, a header renamed, or too few numbered rows). Name what's missing; she fixes the tab. Don't change it yourself. |
| `class_list_missing`, `class_tab_ambiguous`, `duplicate_student` | The class list can't be read reliably. Name the tab and the problem. |
| `draft_method_unknown` | Drafting this simulation isn't set up yet (only Used Car is). `check` and the absence steps still work on a draft she makes herself. |
| `draft_has_errors`, `final_has_errors`, `warnings_not_accepted` | Go back to her review with the listed findings. |
| `write_verification_failed` | Saving didn't produce exactly the intended change, so the backup was restored and nothing changed. Report it and stop. |
| `unknown_student`, `bad_option` | A name or option didn't match; check the spelling against the class list. |

If an error isn't listed here, report the message and stop; don't work around it.

## Reference

`references/pairing-rules.md` has the exact drafting, absence, and checking rules, and what is written where on the tab. Read it if she asks why a student ended up where they did.
