# Example Files

Fictional files in the instructor's exact formats, for building and testing the two skills. Every name, email, and answer is made up; class-list emails use `example.edu` and personal emails `example.com`, so nothing can reach a real person. Her real files are never committed to this public repo.

To regenerate everything (the contents come out the same each time):

```bash
python negotiation_agent/examples/tools/make_examples.py
```

## Files

| File | What it is | Used to test |
|---|---|---|
| `BUS 4489 F26 Roster - before Used Car.xlsx` | Her roster workbook before Used Car: class list on `Att - Fall` (39 students), an empty `Att - Spring` template, an exam tab with formulas and a comment, and `UC` and `SL` tabs prepared with headers and match numbers only | Drafting (T1–T5) and that nothing outside the `UC` draft table changes |
| `BUS 4489 F26 Roster - Used Car drafted.xlsx` | The same workbook a few days before class: the `UC` draft table is filled in, the final table is still empty | The bargaining range sheet built from the draft (before class), and the absence update (T9) |
| `BUS 4489 F26 Roster - after Used Car.xlsx` | The same workbook after Used Car: draft table and final table filled in, three absent students with `UC_0`, `SL` prepared with a `UC` column | Reading a finished tab, the absence rule (T9), repeat warnings for the next simulation |
| `BUS+4489+F26+Week+2+-+Used+Car+Bargaining+Range_October+14,+2026_14.40.csv` | A Qualtrics export in her survey's exact format (three header rows, numeric codes) | Cleaning (T6), matching (T7), and the bargaining range sheet (T8) |
| `expected/used-car.json` | The draft, absences, final matches, and per-student survey expectations | Automated checks of both skills |
| `tools/make_examples.py` | The generator for all of the above | |

## Planted Cases

**Class list and drafting.** 39 students, an odd number: the alphabetical method gives 19 Buyers and 20 Sellers, so the last Seller (Tess Zimmerman) joins match 19 as a second Seller. Two students share a last name (Daniel and Danielle Park), one name has an accent (García), one an apostrophe (O'Neill), and one a multi-word last name (Van der Berg).

**Absences in class:** Tolu Adebayo (Buyer, match 1), Rosa Castellano (Buyer, match 5), and Tess Zimmerman (the extra Seller in match 19).

| Absent | Expected result |
|---|---|
| Tolu Adebayo, match 1 | Match 1 dissolves. There is no earlier match, so Rafael Mendes joins match 2 as a second Seller. |
| Rosa Castellano, match 5 | Match 5 dissolves; Siobhan O'Neill joins match 4 as a second Seller. |
| Tess Zimmerman, match 19 | Match 19 still has a Buyer and a Seller; nothing else changes. |

**Survey export.**

| Student | Planted problem | Expected handling |
|---|---|---|
| Noor Reyes | Target `10` | Corrected to 10,000, orange, original in a comment |
| Connor Walsh | BATNA `8.8k` | Corrected to 8,800, orange |
| Kai Silva | Reservation `>8,800` | Kept as typed, light red |
| Gianna Rossi | Target `$10,500-10,250`; name typed with trailing spaces | Kept as typed, light red; matched by name |
| Jack Thornton | BATNA `$8,800 (sell to dealer)` | Read as 8,800, orange, original in a comment |
| Hiro Sato | BATNA `200` | Kept, light red (outside the usual range) |
| Lena Ortiz | Name typed in lowercase | Matched by name |
| Andy Kowalski | Typed "Andrew", personal email | Matched as a nickname |
| Katherine Nguyen | Typed "Katie", personal email | Matched as a nickname |
| Danielle Park | Typed "Dani", personal email; two students named Park | Asked about (H4), both Parks suggested |
| Jordan Evans | Last name typed "Evens", personal email | Asked about (H4), Jordan Evans suggested |
| Mateo García, Siobhan O'Neill, Elise Van der Berg | Accent missing, curly apostrophe, lowercase | Matched by name |
| Dev Shah | A Seller who chose Buyer | Assigned role kept, `ROLE` highlighted light red |
| Simone Hale | Submitted twice | Asked about (H4), "use the latest" offered |
| Owen Bennett, Mia Underwood | No response | Row kept with blank answers |
| Tolu Adebayo | Absent and no response | Left off after the absence update |
| Rosa Castellano | Absent but responded | On the sheet before class; left off after the absence update |
| (none) | One completely blank response and one "Survey Preview" response | Removed and counted in the summary |

Most other students use a mix of answer formats (`7800`, `$7800`, `7,800`, `$7,800`, a trailing space) that should all clean to plain numbers without highlights.
