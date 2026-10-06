# File Formats

What `scripts/nps.py` expects in each file. Column headers are matched case-insensitively, by the words shown, and may appear anywhere in the first 15 rows (so a title row above the header is fine). Extra columns are ignored.

## Simulation Settings.xlsx (course folder)

One row per simulation, header in the first rows.

| Header contains | Meaning | Example |
|---|---|---|
| `Simulation` | Name used in requests and folder names | `Used Car` |
| `Role 1`, `Role 2` | The two roles in each pair | `Buyer`, `Seller` |
| `Role 1 Information`, `Role 2 Information` | Text or a link inserted into each student's role email | a link to the role PDF |
| `Survey Link` | Qualtrics link included in role emails | |
| `Survey Student ID Column` | Export column holding the student ID (code like `Q1`, or the question text) | `Q1` |
| `Survey Column Mapping` | `export column=outcomes column`, separated by `;` | `Q3=Worst Acceptable Price; Q4=Ideal Price; Q5=Opening Offer` |
| `Outcomes Template` | File name in `Templates/` | `Used Car Outcomes Template.xlsx` |
| `Role Balancing` | `Yes` to prefer giving students the role they've had less often | `Yes` |

Only two-role simulations (pairs) are supported. Multi-party groups are not.

## Roster.xlsx (section folder)

The first sheet. It needs a `Student ID` (or `Emplid`) header, plus either `Name` (as `Last,First` or `First Last`) or separate `First Name` / `Last Name` columns.

- **Optional columns:** `Email`, `Status` (only `Enrolled` students are paired), `Status Note(s)`. Notes such as "Goes by Katie" help absence matching.
- **Student IDs:** compared ignoring spaces and leading zeros, but always written back exactly as they appear in the roster.

## Pairing History.xlsx (section folder)

The instructor's own tracking sheet, read from the first sheet. It needs a `Student ID` header and usually `Student Name`.

- **Past negotiations:** every column whose header contains `Pair` (for example `9/24 Warm-Up Pair ID`) is one past negotiation. If the next column's header contains `Role`, it holds that negotiation's roles.
- **The pairing rule:** two students who share a value in any Pair column have already negotiated together.
- **Pair-ID formats** recognized for continuing the sequence: `N3-07` style (a letter prefix, the negotiation number, a separator, then the pair number), or a single running counter such as `14` or `P14`. Anything else stops with `pair_id_format_unknown`.
- **What `record` writes:** new columns after the last used column, `<M/D> <Simulation> Pair ID` and, when roles are tracked, `<M/D> <Simulation> Role`, with the header styled like the existing header. Students missing from the sheet are added as new rows. Existing cells are never changed. A backup is saved in `Backups/` first.

**If her real spreadsheet is laid out differently** (for example, all pair IDs in one cell per student, or one sheet per negotiation), the script will stop with a layout error or misread the history. Don't restructure her file to fit. Tell her, and leave the script change to the tool's maintainer.

## Pairing Draft.xlsx (simulation folder, created by `pair`)

| Sheet | Contents |
|---|---|
| `Pairing` | `Pair #`, `Student ID`, `Student Name`, `Role`, `Partner`, `Repeat Partner?`. She may edit `Pair #` and `Role`. `Partner` and `Repeat Partner?` are recalculated on every check. An observer has role `Observer` and no pair number. A student partnered with the instructor is alone in a pair. |
| `Checks` | Every error and warning from the last validation, with a summary line. |
| `Info` | Settings for this run: section, simulation, date, absent IDs, odd-count arrangement, keep-apart pairs, seed, status (`Draft` or `Recorded <time>`), pair IDs issued. |

## Role Mail Merge.xlsx (simulation folder, created by `mailmerge`)

Fixed columns: `First Name`, `Last Name`, `Email`, `Simulation`, `Role`, `Role Information`, `Survey Link`, `Status` (`Ready` or `Missing email`). Observers are not included. Partner names are not included, because the instructor hasn't yet confirmed whether students should learn their partner by email.

Outlook mail merge cannot attach a different file to each email, which is why role information is text or a link.

## Survey Export.csv (simulation folder, saved by the instructor)

A Qualtrics CSV export, either the standard three header rows (codes, question text, ImportId) or a plain single header.

- **Columns are found** by code (`Q1`) or by exact question text.
- **Rows ignored:** those whose `Status` contains Preview, Test, or Spam.
- **Duplicate submissions** are ordered by `RecordedDate` (or `EndDate`).
- **Response IDs** come from `ResponseId`; without that column they are `row<n>`.
- **Number formatting:** `$` and `,` are stripped from numbers.

## Outcomes.xlsx (simulation folder, created by `outcomes`)

A copy of the template in `Templates/`. The header row must contain `Role`. The script fills in the columns whose headers contain `Pair`, `Name`, `Student ID`, `Role`, and `Note`, plus every mapped outcomes column (matched by exact header text).

All other cells, including formulas and the outcome column she fills in during class, are left untouched. Rows go in pair order, with partners on adjacent rows and Role 1 first. An existing `Outcomes.xlsx` is moved to `Backups/` before a new one is written.
