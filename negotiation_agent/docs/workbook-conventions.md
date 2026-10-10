# Workbook Conventions

These are the instructor's own conventions, learned from her Fall 2026 roster workbook, a Qualtrics export, and a finished Used Car bargaining range sheet. Both skills must follow them exactly, so that what Claude writes looks like what she would have written by hand. All names below are fictional.

Items marked **(assumption)** have not been confirmed with the instructor yet; see [`open-questions.md`](open-questions.md).

## The Roster Workbook

One Excel workbook per course and term (for example `BUS 4489 F26 Roster.xlsx`). It also holds exams, grades, and attendance, so the skills change only the simulation tab they are working on and never touch any other tab.

| Tab | Contents | Used by |
|---|---|---|
| `Att - Fall` (or `Att - Spring`) | Class list and attendance: `No.`, `Student Name` (`Last, First`), `Email` (Cal Poly), then one column per class date | Both skills read the class list. Attendance is filled in by the instructor after class **(assumption)** and is not read yet. |
| `UC`, `SL`, `ES`, `JO`, `VA`, … | One tab per simulation, named with the simulation's two-letter code | `negotiation-pairing` writes the current simulation's tab. Both skills read pairings from it. |
| Exams, grades, other tabs | Not related to pairing | Never read or changed |

Students are identified by **name** (`Last, First`, as on the class list) and **Cal Poly email**. There are no student ID numbers.

## Simulation Codes and Pair IDs

Each simulation has a two-letter code: `UC` is Used Car, `SL` is the salary negotiation, and so on. Every match gets a pair ID made of the code and the match number:

- `UC_4`: the student was in match 4 of Used Car. Everyone in the same match shares the same ID.
- `UC_0`: the student was **absent** for Used Car.

Two students have negotiated together before if they share any pair ID other than `_0`. Pair IDs are never reused within a simulation, and match numbers are never renumbered: when a match dissolves because of an absence, its number simply disappears from the final table.

## A Simulation Tab

Each simulation tab holds two tables. The instructor prepares the tab in advance with headers and match numbers already filled in; the skill fills in the names.

### Final table (top)

The matches as they actually happened in class, written after absences are known **(assumption: written at the in-class absence step, even when nobody is absent)**.

Used Car layout (row 1 is the header):

| A | B | C | D | E | F | G | H | I | J |
|---|---|---|---|---|---|---|---|---|---|
| *(match)* | `BUYER` | `Email` | *(pair ID)* | `Gender` | `SELLER` | `Email` | *(pair ID)* | `Gender` | `Intervention` |
| 1 | Alvarez, Maya | malvarez@calpoly.edu | UC_1 | | Novak, Ben | bnovak@calpoly.edu | UC_1 | | |
| 2 | Brooks, Tyler | tbrooks@calpoly.edu | UC_2 | | Ortiz, Lena | lortiz@calpoly.edu | UC_2 | | |
| 3 | Chen, Priya | pchen@calpoly.edu | UC_3 | | Park, Owen | opark@calpoly.edu | UC_3 | | |
| | | | | | Quinn, Ava | aquinn@calpoly.edu | UC_3 | | |
| 5 | Diaz, Sam | sdiaz@calpoly.edu | UC_5 | | Reyes, Noor | nreyes@calpoly.edu | UC_5 | | |
| | | | | | Silva, Kai | ksilva@calpoly.edu | UC_5 | | |

This is the final version of the draft shown further down, after Evans, Jo was absent.

- **A second student in the same role** (because of an odd count or an absence) gets their own row directly under the match, with the match number and the other role's cells left blank, and shares the match's pair ID (`UC_3` above).
- **Absent students** are listed a few rows below the table with their name, email, and `UC_0` **(assumption: the instructor's UC tab lists the absent student without an ID; her later tabs show `UC_0`)**.
- `Gender` and `Intervention` are filled in by the instructor. The skills leave them blank and never change them.
- **Later simulations carry history forward:** each student's earlier pair IDs appear in columns headed with the earlier simulations' codes, before the current one. For example, the `SL` tab has `Email | UC | SL` for each role. Used Car is the first simulation of the term, so its tab has only the `UC` column.

### Draft table (bottom)

The matches drafted a few days before class, under a header row reading `MATCH | BUYER | SELLER` (the role names change with the simulation):

| A | B | C |
|---|---|---|
| `MATCH` | `BUYER` | `SELLER` |
| 1 | Alvarez, Maya | Novak, Ben |
| 2 | Brooks, Tyler | Ortiz, Lena |
| 3 | Chen, Priya | Park, Owen |
| 4 | Evans, Jo | Quinn, Ava |
| 5 | Diaz, Sam | Reyes, Noor |
| | | Silva, Kai |

An extra student in an odd-numbered class appears as the last row with no match number, in the role that has one more student.

## How the Instructor Pairs Students

- **Used Car (first simulation of the term):** sort the class list alphabetically by last name, then first name. The first half are Buyers and the second half are Sellers, and they are matched in order: the first Buyer with the first Seller, and so on. With an odd count, the extra student becomes a second Seller in the last match.
- **Later simulations:** she keeps the alphabetical halves and shifts the second half so nobody meets a former partner. The exact rule will be written down when later simulations are in scope.
- **Roles are locked once role emails go out,** because each student already has the role packet for their role. Absence updates may move a student to another match, but never change their role.

## Absences in Class

When a student is absent, they get `_0`, and their partner joins the **match just before theirs** as a second student in the same role **(assumption: rule seen twice in her UC tab, not yet confirmed)**. Example from the draft above: if Evans, Jo (match 4) is absent, Quinn, Ava joins match 3 as a second Seller; match 4 disappears; Evans, Jo is listed below the table with `UC_0`.

If the match just before would create a repeat partner (possible in later simulations), the skill warns and asks the instructor where the student should go.

## The Qualtrics Export (Used Car)

The instructor downloads a CSV with three header rows: column codes (`Q1`, `Q2`, …), question text, and `ImportId` JSON. Answers are exported as numeric codes (Role `1` = Buyer, `2` = Seller; perception items `1`–`4`).

| Code | Question | Used for |
|---|---|---|
| `Q1`, `Q2` | First name, last name | Matching to the class list |
| `Q3` | Role (1 Buyer, 2 Seller) | Checked against the assigned role |
| `Q4` | Initial offer | `INITIAL` |
| `Q5` | Ideal price | `TARGET` |
| `Q6` | Highest/lowest acceptable price | `RESERVATION` |
| `Q7` | Cost of best alternative | `BATNA` |
| `Q12_1`–`Q12_6` | Six "after this negotiation, my partner will…" items | Copied as-is |
| `Q11` | Email address (often a personal Gmail) | Matching to the class list |

Answers are typed freely, so they arrive as `13000`, `$13000`, `"12,000"`, `>8,800`, `$10,500-10,250`, `$8,800 (sell to dealer)`, or occasionally a typo such as `10` for 10,000. Names arrive with stray spaces, lowercase, or nicknames (`Andrew` for `Andy`). Some responses are completely blank.

## The Bargaining Range Sheet (Used Car)

The instructor's finished sheet, named like `BUS 4489 F26 Week 2 - Used Car Bargaining Range.xlsx`, has one row **per match**, mirrored around the outcome:

| A | B | C | D | E | F | G | H | I | J–O | P | Q | R | S | T | U | V | W | X | Y–AD |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `MATCH` | `FIRST` | `LAST` | `ROLE` | `ACTUAL IO` | `INITIAL` | `TARGET` | `RESERVATION` | `BATNA` | six items | `OUTCOME` | `BATNA` | `RESERVATION` | `TARGET` | `INITIAL` | `ACTUAL IO` | `FIRST` | `LAST` | `ROLE` | six items |

- The **Buyer** fills columns A–O and the **Seller** fills Q–AD, in reverse order, so the two bargaining ranges meet at `OUTCOME`.
- `ACTUAL IO` (yellow headers) and `OUTCOME` are filled in **by hand during class**. The skill leaves them blank.
- A second student in the same role gets their own row under the match, with the other side blank.
- `ROLE` holds the Qualtrics code (`1` or `2`). Every other match row is shaded for readability.
- Other tabs: `Roles` (`MATCH | BUYER | SELLER`) and `Raw` (the untouched export).
- Clean numbers are stored as numbers without `$` or commas. Unclear answers stay exactly as typed.

### Highlights added by the skill

| Color | Meaning |
|---|---|
| Yellow | The instructor's in-class columns (`ACTUAL IO`), as in her own sheets |
| Orange | An obvious typo the skill corrected; the original answer is in a cell comment |
| Light red | An unclear answer kept exactly as typed, for her to read |

A short legend on the sheet explains the colors.
