# Build Plan: Meeting 5 Changes

**Status:** Approved by Aidan ("propose a build order and get to work"). Items built on an assumption are listed in [`open-questions.md`](open-questions.md).

Interview notes from Meeting 5 changed the Used Car conditions, settled the Salary question, and introduced the next simulation, Equity Splits. Her real process points sheet (Week 4) was used only locally, to copy its format. Everything committed uses fictional students.

## Order and Checkpoints

| Phase | What | Why this order | Checkpoint |
|---|---|---|---|
| 1 | Used Car conditions: Sellers only, three BCC lists | Corrects something already built and demoed | Push after tests pass |
| 2 | Salary: totals are the default, the raise conversion stays as a fallback | Documentation only; the code already does this | With phase 1 |
| 3 | Equity Splits drafting: trios, gender, repeats, two four-person teams, absences | The next simulation in class | Push after tests pass |
| 4 | Equity Splits process points sheet from the in-class Google Form | Built in class, like the Salary sheet | Push after tests pass |
| 5 | Demo Kit: an Equity Splits step | So there's something to show her today | With phase 4 |

Waiting on her: the Equity Splits tangible-outcomes sheet (its layout) and where she wants the yellow highlight for students who didn't fill out the form.

## Phase 1: Used Car Conditions, Sellers Only (`negotiation-pairing`)

Meeting 5: there are no intervention Buyers. Only Sellers get a condition, so there are three role packets and three BCC lists: `BUYER`, `SELLER-I`, `SELLER-C`.

1. Students who declined consent (or are excluded, or didn't take the baseline) are matched with each other first, by her alphabetical method. They get no condition, even as Sellers.
2. Everyone else: within each gender, alphabetically, the first half are Buyers and the second half Sellers. This keeps both roles balanced by gender; Meeting 5 said Buyer balance matters less, but to keep it anyway.
3. Sellers: within each gender, alphabetically, the first half get `I` and the second half `C`.
4. Buyers and Sellers are each sorted alphabetically and matched in order. A Buyer can face an I or a C Seller.
5. The draft table's `CONDITION` column holds the Seller's condition on that row. The final table's `Intervention` column gets each Seller's condition.
6. **BCC lists:** `BUYER`, `SELLER-I`, `SELLER-C`. Sellers without consent go on the `SELLER-C` list (the standard packet) and are named in a note. *(Assumption.)*
7. **Absences:** conditions no longer decide anything. A stranded student joins the match just before in the same role, as in every simulation, but stays with students in the same group (with consent or without) where possible. *(Assumption, as she asked.)*

## Phase 2: Salary (`bargaining-range-sheet`)

From next term, students always type a total salary, in the Qualtrics surveys and the Form. The sheet already treats any number of $40,000 or more as a total, so nothing changes for those answers. The raise conversion (under $40,000 gets the $60,000 base added) stays as a fallback. When she updates the surveys, run the new export through the skill once to check the question wording.

## Phase 3: Equity Splits Drafting (`negotiation-pairing`, tab `ES`)

Three cofounders: **Michael, Phuc, Georg** (the role names on her process points sheet). The tab follows her usual layout with three roles: the final table on top (each role with Email, `UC`, `SL`, `ES`), and the draft table below (`MATCH`, `MICHAEL`, `PHUC`, `GEORG`). She prepares it, as with the other tabs.

**Drafting.** There is no base method for this simulation, so the script searches for the best trios against her goals, in this order:
1. Nobody is with someone they've already negotiated with (any earlier tab). Best effort: a repeat it can't avoid is a warning.
2. Each role gets about the same number of men and women.
3. Each trio is mixed (at least one man and one woman), where possible.
4. With a class size not divisible by 3, the one or two extra students each join a different trio, as a second student in a role. So with 2 left over there are two four-person teams. The extra students take different roles, Michael first, then Phuc. *(Assumption.)*
5. Nobody is in an odd spot twice in the term (all simulations): the "1" in a 1v2, or an extra in a four-person team. Extras are chosen from students who haven't had an odd spot yet.

The search is deterministic: the same class gives the same draft every time, so she can re-run it and get the same answer. Swaps work as for Used Car.

**BCC lists:** three, `MICHAEL`, `PHUC`, `GEORG`.

**Absences:**
1. Absent students get `ES_0`.
2. A team that still has all three roles stays as it is (a four-person team that loses its extra is simply a trio again).
3. A team missing a role first gets an extra from a four-person team who has that role (the nearest one). That team is then a trio.
4. If there are more absences than extras, the trio left with two people is merged: with another incomplete team if together they have every role, otherwise into the team just before it (her usual rule). Nobody's role changes.
5. Anything that would repeat a partner, give someone a second odd spot, or make a team of more than five: she decides with `--place`.

## Phase 4: Equity Splits Process Points Sheet (`bargaining-range-sheet`)

**What she does in class:** after the negotiation, each student fills in the Google Form once for each teammate. She downloads the responses as a CSV and asks Claude for the process points sheet. Claude reads the CSV and the `ES` tab (final table, otherwise the draft).

**The sheet** follows her Week 4 sheet:
- **Main tab:** `TRIO`, the observer's first and last name and role, the partner's first and last name and role (bold), the five scores (Trust, Respect, Fairness, Interests, Future), and `TOTAL` as an Excel `SUM`. Rows are sorted by trio, then by the person assessed; alternate trios are shaded, as in hers; the header row is frozen.
- **Names and roles come from her roster**, not as typed. The trio number is checked against the names. A corrected value (trio `#1` to 1, a misspelled name, a wrong role) is highlighted orange with the typed value in a comment. A score that isn't 0–5 stays as typed, in light red.
- **`By Student` tab** *(new, an assumption)*: one row per student: trio, role, ratings given out of those expected, and the average and total points they received. A student who hasn't rated every teammate is highlighted yellow, so she knows whom to chase. Where she wants the yellow is still to be confirmed.
- **`Raw` tab:** the Form export, untouched, as in hers.

**Problems handled:** duplicate ratings (the latest is used, listed in the summary), a rating of someone outside the observer's trio, a self-rating, names that match nobody (she's asked), absent students (not expected to rate).

## Not Changing

- Students learn their partners in class; no email is sent.
- Her workbook is only written with a backup and a check that nothing else changed.
- The tangible-outcomes sheet for Equity Splits waits for her layout.
