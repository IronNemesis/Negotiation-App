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
4. With an odd count, the extra Seller joins the last match as a second Seller.
5. Apply her swaps (`--swap`). Each swapped student takes the other's role and match.

**Writing:** names go into the draft table's numbered rows, starting at the first. A second same-role student goes on the next row with no match number. Unused numbered rows are cleared.

## Absences (her rule)

1. Absent students leave their match and get `<code>_0`.
2. A match that still has at least one student in each role stays as it is.
3. Otherwise its remaining students are stranded. Each one joins the nearest earlier match still in use, in the same role. If there is no earlier match, they join the next one.
4. If joining would give that match more than three students, or repeat a partner from an earlier simulation, the script doesn't choose: she places the student with `--place`.
5. Match numbers are never renumbered.

**Writing the final table:**
- Rows start under the final header: match number, then each role's name, email, earlier pair IDs, and `<code>_<match>`.
- Extra same-role students go on the row under their match.
- One blank row, then absent students with `<code>_0`.
- Unused prefilled match numbers above the draft table are cleared.
- Columns she fills herself (Gender, Intervention) are never written.

## Checks (before anything is written)

**Errors** block writing:
- a student appears twice;
- an absent student is in a match;
- a match lacks a role;
- a match has more than three students;
- a name isn't on the class list, or is only "likely";
- in the final matches, a role differs from the draft, or a class-list student is in no match and not reported absent.

**Warnings** need her OK:
- repeat partners from earlier simulations;
- in a draft, a class-list student not in any match.

## Safety on Every Write

1. The workbook is backed up to `Backups/<name> <date> <time> before <code> draft|final.xlsx`.
2. After saving, every cell of every tab is compared with the backup. If anything other than the intended cells changed, or an intended cell is wrong, the backup is restored and the command fails with `write_verification_failed`.
3. Each action is logged in `Negotiation Log.xlsx` next to the workbook.
