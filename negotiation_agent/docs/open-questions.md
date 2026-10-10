# Open Questions

The workflow is built from two interviews and three of the instructor's files: her roster workbook, a Used Car Qualtrics export, and her finished bargaining range sheet. Each item below is an assumption in the current design that still needs her confirmation. The **Affects** column shows which task specifications change if her answer differs.

## To Ask the Instructor

| Question | Current assumption | Affects |
|---|---|---|
| When does she fill in the final (top) table on a simulation tab: at drafting time, or only after absences? | The draft goes in the bottom `MATCH` table; the top table is written at the in-class absence step, even when nobody is absent. | T4, T9 |
| When a student is absent, does their partner always join the match just before theirs? If a Buyer and a Seller from different matches are both stranded, should they be paired with each other instead? | Each stranded student joins the previous match in the same role. | T9 |
| On her UC tab, the absent student is listed below the table without an ID; her later tabs show `UC_0`. Which does she want on the current simulation's tab? | The absent student is listed with `UC_0`. | T9 |
| How does she show absent students on the bargaining range sheet? | They are left off the re-run sheet and named in the summary. | T7, T8 |
| What is the `Intervention` column (`I`/`C`) on the UC tab, how is it assigned, and should the agent fill it in? | Left blank for her; not used. | T9 |
| What is the `Gender` column used for, and should it play any role in pairing? | Left blank for her; not used. | T2, T9 |
| Who are the second list of students (with gender and intervention) lower on her UC tab? | Ignored. | T1 |
| Is attendance in `Att - Fall` filled in after class? Could it ever be the source for absences? | Filled in after class; absences come from her in the chat. | H5 |
| Would she require students to enter their Cal Poly email in the Qualtrics survey (or pick their name from a list)? | Not required; matching uses names and whatever email they give. | T7, H4 |
| Does she prepare the UC tab in advance the same way as the VA tab (headers and match numbers filled in)? | Yes; the skill fills in her prepared tab and stops if it is missing or too short. | T1, T4, T9 |
| Should students switch roles across simulations? | Ignored for now. Her method keeps the same alphabetical halves. | T2 |
| Her UC draft lists a student by one first name and the final table and class list by another (a legal vs. preferred name). Which name should the skills write on new tabs? | The class-list name is written; other variants are linked when confident and otherwise reported for her to confirm. | T1, T4, T9 |
| A student in her UC draft no longer appears on the class list (dropped before class). Should the skills warn when a drafted student has since left the class? | Yes: T3 reports it as an error before the final matches are written. | T3, T9 |
| In her Week 2 sheet, one student has survey answers that aren't in the Qualtrics export. How does she collect answers from students who miss the survey, and should the skill accept them (for example, typed into the chat)? | Students not in the export get a blank row with a "No survey response" comment. | T7, T8 |
| In her Week 2 sheet, one initial offer differs from what the student entered in Qualtrics. Does she sometimes correct survey answers by hand, and from what source? | The skill copies the export exactly, apart from the documented cleaning rules. | T6 |
| Are the proposed time target (about 5 minutes per simulation) and highlight colors (orange for corrected typos, light red for unclear answers) acceptable to her? | Yes. | README, T6, T8 |

## For Aidan

| Item | Status |
|---|---|
| Open a copy of her workbook that has been saved by openpyxl in desktop Excel (ideally Windows) and confirm it opens without a repair prompt. `shared/tools/roundtrip_check.py` confirmed nothing in the content is lost; only Excel itself can confirm the file opens cleanly. | To do before the skills write to her real workbook |

## Decided

| Decision | Source |
|---|---|
| Draft matches with her alphabetical method (first half Buyers, second half Sellers, matched in order). | Aidan, after reviewing her UC and SL tabs |
| Sort the class list strictly alphabetically. | Aidan |
| The skill fills in the simulation tab she prepares; it does not create tabs. | Aidan |
| Write both draft and final tables into her actual roster workbook, with a backup before every write. | Aidan |
| Role emails go out as BCC emails per role with the packet attached; the agent only prepares the address lists. | Interview 2 |
| Students learn their partners in class, not by email. | Interview 2 |
| The bargaining range sheet is built from the draft before class and quickly re-run after absences. | Aidan |
| Obvious typos are fixed and highlighted; unclear answers stay as typed and are highlighted. | Aidan |
| Warn about repeat partners from earlier simulations now, so the logic is ready for later simulations. | Aidan |
| Focus on Used Car first; look at her other simulation templates afterwards. | Interview 2 and Aidan |
| Two skills: `negotiation-pairing` and `bargaining-range-sheet`. | Aidan |
| Her real files are used for local testing only and never committed to the public repo. | Aidan |
