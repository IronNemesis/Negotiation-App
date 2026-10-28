# Pairing Rules

## Reading the Workbook

- **Class list:** the attendance tab with `Student Name` (`Last, First`) and `Email` headers and names under them (`Att - Fall` or `Att - Spring`). If two attendance tabs both have names, the script asks which one is current.
- **Simulation tab** (for example `UC`), found by its two header rows:
  - **Final table (top):** the row holding both role names and `Email`. Each role is followed by its email column (sometimes unlabeled), the codes of earlier simulations (for later simulations), and this simulation's pair-ID column (blank header or the code).
  - **Draft table (below):** the row holding `MATCH` and both role names.
- **Names on her tabs** are linked to the class list by exact name, email, or a known nickname with a unique last name. A unique last name with a different first name is only "likely": she confirms it with `--same-person`.
- **Pair history:** every `XX_n` ID on every tab, attached to the student name to its left on the same row. Two students sharing an ID other than `_0` have negotiated together.

## Drafting (Used Car)

1. Take the class list, minus students she named as absent.
2. Sort by last name, then first name, ignoring case, accents, and apostrophes.
3. The first half (rounded down) are Buyers and the rest are Sellers. Match them in order and number the matches from 1.
4. With an odd count, the extra Seller joins the last match as a second Seller, unless that would make the last match's Buyer the "1" in a 1v2 for a second time, or repeat a partner. Then the extra student joins the nearest earlier match where neither happens (reported in `placement_notes`).
5. Apply her swaps (`--swap`). Each swapped student takes the other's role and match.

## Experimental Conditions (Used Car, once gender and consent are recorded)

These are assumptions from Meeting 4, to confirm with her.

1. Students whose Consent isn't `Yes` (`No`, `No (no survey)`, `Excluded`) are matched only with each other, by her alphabetical method. A lone one joins the smaller condition.
2. Everyone else is split by gender. Within each gender, alphabetically, the first half is `I` and the second half `C`. An odd one out goes to `I` for the first gender and to `C` for the next, so the totals stay even.
3. Within each condition, her method applies: first half Buyers, second half Sellers, matched in order. The extra student is placed as in step 4 above.
4. Matches are numbered with all `I` matches first, then `C`. Each match of students without consent takes the condition with fewer students.
5. **Writing:**
   - The condition goes in a `CONDITION` column added next to the draft table.
   - At the absence step, a stranded student joins the nearest earlier match **in the same condition** (or the next one). If there's none, she places them. Placing across conditions is a warning.
   - The final table then gets each student's `Gender` (from the class list) and the `Intervention` column (their condition, for absent students too).
6. **BCC lists:** four of them, Buyer-I, Buyer-C, Seller-I, Seller-C.

Not built yet: swapping roles between two stranded students who both declined consent, which Meeting 4 allows.

## Drafting (Salary negotiation and later rotations)

1. Take the class list, minus students she named as absent.
2. Each student keeps their side (first or second role) from the earlier simulation's draft table (`rotate_from` in the settings; `UC` for `SL`). Sort each side alphabetically.
3. Students who weren't in that draft go on the smaller side. If the sides end up more than one apart (after drops), the alphabetically last students of the bigger side move to the other side.
4. The right column moves down one, and the bottom student goes to the top. Match in order.
5. An extra student is placed as in Used Car step 4. Apply her swaps.

Every placement decision is in `placement_notes`. Repeats the rotation can't avoid are warnings for her review.

**Writing:** names go into the draft table's numbered rows, starting at the first. A second same-role student goes on the next row with no match number. Unused numbered rows are cleared.

## Absences (her rule)

1. Absent students leave their match and get `<code>_0`. A drafted student who is no longer on the class list dropped the class: they are treated as absent this week, even if she doesn't name them, and simply aren't on the class list for later simulations. Their earlier pair IDs still count as history.
2. A match that still has at least one student in each role stays as it is.
3. Otherwise its remaining students are stranded. Each one joins the nearest earlier match still in use, in the same role. If there is no earlier match, they join the next one.
4. If joining would give that match more than three students, repeat a partner from an earlier simulation, or make someone the "1" in a 1v2 for a second time, the script doesn't choose: she places the student with `--place`.
5. Match numbers are never renumbered.

**Writing the final table:**
- Rows start under the final header: match number, then each role's name, email, earlier pair IDs, and `<code>_<match>`.
- Extra same-role students go on the row under their match.
- One blank row, then absent students with `<code>_0`, each under their own role's columns (students absent from the draft go under the first role).
- Unused prefilled match numbers above the draft table are cleared.
- Columns she fills herself (Gender, Intervention) are never written.

## Checks (before anything is written)

**Errors** block writing:
- a student appears twice;
- an absent student is in a match;
- a match lacks a role;
- a match has more than three students;
- a name is only "likely" a class-list student;
- in the final matches, a name isn't on the class list (dropped students are listed as absent instead);
- in the final matches, a role differs from the draft, or a class-list student is in no match and not reported absent.

**Warnings** need her OK:
- repeat partners from earlier simulations;
- a student who is the "1" in a 1v2 (alone on their side of a three-person match) and already was on an earlier simulation's final table;
- in a draft, a class-list student not in any match;
- in a draft, a name that isn't on the class list (she may have dropped the class; she'll be listed as absent in class).

## Safety on Every Write

1. The workbook is backed up to `Backups/<name> <date> <time> before <code> draft|final.xlsx`.
2. After saving, every cell of every tab is compared with the backup. If anything other than the intended cells changed, or an intended cell is wrong, the backup is restored and the command fails with `write_verification_failed`.
3. Each action is logged in `Negotiation Log.xlsx` next to the workbook.

## Gender and Consent (baseline survey)

- **Read from** the Week 1 baseline export (number codes). The columns are `Q1` consent (1 agree, 2 decline), `Q11` first name, `Q14` last name, and `Q15` gender (1 Male, 2 Female, any other code Other, with `Q15_4_TEXT`). Survey previews are skipped.
- **Matching:** responses are matched to the class list by name (exact, then a known nickname with a unique last name). Anything else is her decision (`--assign`, `--leave-out`). If someone took it twice, the latest response is used.
- **Values written:**
  - Gender: `M`, `F` or `Other`.
  - Consent: `Yes` or `No`.
  - A student who chose Other gets Consent `Excluded`: they're excluded from the research.
  - A student with no response gets Consent `No (no survey)` and a blank Gender.
- **Where:** two columns headed `Gender` and `Consent`, just after `Email` on the class list.
- **Inserting the columns:** if they aren't there yet, they're inserted and everything to the right moves over by two. That only happens if nothing on the tab would break: no formulas, merged cells to the right of Email, conditional formatting, data validation, tables, or formulas or names elsewhere pointing at the tab. Otherwise she inserts the two blank columns herself and the script fills them.
- **Checking the write:** after saving, every other cell is checked to be exactly where it was, or two columns to the right. Otherwise the backup is restored.
