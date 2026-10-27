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
| `BUS 4489 F26 Roster - Salary in class.xlsx` | After Used Car, with `SL` drafted by her rotation and the final matches after one absence (Priya Chen); Siobhan O'Neill was placed in match 7 by hand, since the match before would repeat her Used Car partner | The Salary outcomes sheet (T11) |
| `BUS+4489+F26+Week+3+-+Salary+Bargaining+Range+SUPERVISOR_….csv`, `…SUBORDINATE_….csv` | The two Salary Qualtrics exports in her exact format, answered as raises or totals, with notes, a range, `NA`, a typo (`7`), a nickname, a duplicate, and two students with no response | T11 cleaning and matching |
| `BUS 4489 F26 Salary Negotiation (Responses) - Form Responses 1.csv` | The in-class Google Form export: a pair that submitted twice (one with `66000` as the match number), a total typo (`6550`), `No Deal`, a three-person match typed as `7 + Siobhan O'Neill`, `35 minutes`, `None`, a raise typed where a total was asked, and one match with no row | T11 Form matching and cleaning |
| `BUS+4489+F26+Week+1+-+Negotiation+Baseline+Survey_September+30,+2026_09.44.csv` | The Week 1 baseline survey in her format (number codes): two students decline consent, one chooses Other for gender, a nickname, lowercase names, a misspelled last name (asked), a student who took it twice and changed their consent, two who didn't take it, and a survey preview | Gender and consent (T12) |
| `expected/baseline.json`, `tools/make_baseline_example.py` | What T12 should record for each student, and the generator | |
| `expected/salary.json`, `tools/make_salary_examples.py` | The planted Salary cases, and their generator (run after `make_examples.py`; it uses the pairing skill itself to make the `SL` tab) | |

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
| Tolu Adebayo | Absent and no response | In the absent block after the absence update, with blank answers; on the non-respondent list before class |
| Rosa Castellano | Absent but responded | On the sheet before class; in the absent block, with her answers, after the absence update |
| (none) | One completely blank response and one "Survey Preview" response | Removed and counted in the summary |

Most other students use a mix of answer formats (`7800`, `$7800`, `7,800`, `$7,800`, a trailing space) that should all clean to plain numbers without highlights.
