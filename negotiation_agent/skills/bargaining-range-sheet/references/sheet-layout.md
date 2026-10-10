# Sheet Layout and Cleaning Rules

## The Export

The script reads the Qualtrics CSV with its three header rows (question codes, question text, `ImportId`) and numeric answer codes. Columns come from `scripts/simulations.json`. For Used Car:

| Code | Field |
|---|---|
| `Q1`, `Q2` | First and last name, as typed by the student |
| `Q3` | Role: `1` Buyer, `2` Seller |
| `Q4`–`Q7` | Initial offer, target, reservation price, BATNA |
| `Q12_1`–`Q12_6` | Six "after this negotiation, my partner will…" items (`1`–`4`); their headers on the sheet are the question text from the export |
| `Q11` | Email, often a personal address |

Rows are removed (and counted) when every answer is blank, or when `Status` isn't a normal response (a survey preview or test).

## Cleaning a Price

| Typed | Result | Highlight |
|---|---|---|
| `7800`, `$7800`, `7,800`, `$7,800 ` | 7800 | none |
| `10`, `9.4` (below 100) | ×1,000: 10000, 9400 | orange, original in comment |
| `8.8k`, `8.8K` | 8800 | orange, original in comment |
| `$8,800 (sell to dealer)` | 8800 | orange, original (with the note) in comment |
| `>8,800`, `$10,500-10,250`, `about 9000`, anything else | kept exactly as typed | light red |
| a plain number outside the usual range (Used Car: $1,000–$50,000), such as `200` | kept as the number | light red, with a comment |
| blank | blank | none |

## Matching a Response to a Student

Candidates are the students in the current matches: the final table if it has names, otherwise the draft table.

1. **Exact name**, ignoring case, accents, extra spaces, and apostrophes; or **class-list email**.
2. **Nickname**: same last name (no other student shares it) and a known nickname or shortened first name ("Andrew"/"Andy", "Katie"/"Katherine", "Dan"/"Daniel").
3. Otherwise the response is **unresolved** and the instructor decides. This covers a unique last name with a different first name, two possible students, no match, or a name and email that point to different students.

Further rules:
- **Absent students:** a response from a student marked absent (`_0`) is left off the sheet and listed.
- **Not in the matches:** so is a response from a class-list student who isn't in the current matches.
- **Duplicates:** two responses for one student are a duplicate for her to resolve.
- **Role conflicts:** if the survey role differs from the assigned role, the assigned role is used and the `ROLE` cell is highlighted light red.

## The Sheet

One row per match, mirrored around `OUTCOME`:

```
MATCH | FIRST LAST ROLE ACTUAL IO INITIAL TARGET RESERVATION BATNA items×6 | OUTCOME | BATNA RESERVATION TARGET INITIAL ACTUAL IO FIRST LAST ROLE items×6
        ── Buyer (role 1) ──────────────────────────────────────           ── Seller (role 2), mirrored ──────────────────────────────────
```

- **Extra same-role students:** a second student in the same role sits on the next row, with `MATCH` and the other side blank.
- **Names:** come from her tab, not as typed in the survey.
- **ROLE:** the Qualtrics code.
- **In-class columns:** `ACTUAL IO` (yellow headers) and `OUTCOME` stay blank.
- **Shading:** alternate matches are shaded.
- **Legend:** a legend under the table explains yellow, orange, and light red.
- **No response:** a student without a response keeps their row, with a "No survey response" comment on their first name.

Other tabs: `Roles` (`MATCH | BUYER | SELLER`) and `Raw` (the export exactly as downloaded).

The file is written to a temporary location, every value is read back and compared, and only then is it copied next to the export. An existing sheet is moved to `Backups` first, unless it has entries in ACTUAL IO or OUTCOME; then the script stops and asks.
