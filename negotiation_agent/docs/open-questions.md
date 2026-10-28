# Open Questions

The workflow is built from four meetings and her files: her roster workbook, Used Car and Salary Qualtrics exports, her finished Used Car bargaining range sheet, her Salary outcomes sheet and in-class Google Form export, and a Week 1 baseline survey export with its codebook. Each item below is an assumption in the current design that still needs her confirmation. The **Affects** column shows which task specifications change if her answer differs.

## To Ask the Instructor

| Question | Current assumption | Affects |
|---|---|---|
| When does she fill in the final (top) table on a simulation tab: at drafting time, or only after absences? | The draft goes in the bottom `MATCH` table; the top table is written at the in-class absence step, even when nobody is absent. | T4, T9 |
| Found while building: with the Salary rotation (right column down one), the "join the match before" rule always puts a stranded Subordinate back with their Used Car partner, because the match before holds exactly that partner. Today the skill then asks her where the student goes. Is this the "once we start moving forward" exception, and what should happen instead (for example, the match after, or pairing two stranded students)? | She is asked to place the student each time. | T9 |
| Meeting 3 confirmed that a stranded student joins the previous match, "except once we start moving forward." What does that exception mean: once negotiations have started in class, in later simulations, or something else? And when it applies, should two stranded students in opposite roles be paired with each other? | Each stranded student joins the previous match in the same role, in every simulation. | T9 |
| Salary: what is the base salary used to turn a raise into a total salary? | $60,000 (most Form answers). Some say $63,000 or $63,500; one mentions keeping a $3,500 bonus. | Salary sheet |
| Salary: how do we tell a raise from a total salary in what students type? | A number under $40,000 is a raise and gets the base added; $40,000 or more is already a total. The original answer stays in a cell comment. | Salary sheet |
| Salary: targets come from both the Qualtrics survey and the in-class Form. Which wins? | Qualtrics (the white columns); the Form's targets stay on the `Form` tab. | Salary sheet |
| Salary: duplicate Form rows (both partners submitted) and duplicate Qualtrics responses. | The latest submission is used and the summary says so. | Salary sheet |
| Conditions: balance I/C within each role, or across the whole class? | Within each role, as far as the method allows. | UC drafting |
| Conditions: how do "first half / second half," gender balance, and same-condition matching fit together? | Within each gender, alphabetically, the first half is I and the second half C. Within each condition, her usual method: first half Buyers, second half Sellers. | UC drafting |
| Conditions: where should each match's I/C go at drafting time, before the final table exists? | A `CONDITION` column next to the draft table. | UC drafting |
| Conditions: when two stranded students who both declined consent have the same role, should Claude swap one's role and pair them (allowed in Meeting 4), or place them as usual? | Placed as usual; the role swap isn't built yet. | T9 |
| Conditions: which condition do students who declined consent get? | They are paired with each other first and take whichever condition keeps the groups even. | UC drafting |
| Is attendance in `Att - Fall` filled in after class? Could it ever be the source for absences? | Filled in after class; absences come from her in the chat. | H5 |
| Meeting 3: she brings a running list of questions to class for students to answer. Is that how she fills in answers for students who missed the survey, and should she be able to type those answers into the chat for the sheet? | Students not in the export get a blank row with a "No survey response" comment; she fills them in by hand. | T7, T8 |
| Does she ever change a student's survey answer by hand (her Week 2 sheet has one initial offer that differs from Qualtrics), and from what source? | The skill copies the export exactly, apart from the documented cleaning rules. | T6 |
| The list of students who haven't filled out the survey: when does she want it (the night before, the morning of class), and should it be a BCC-ready email list like the role lists? | A BCC-ready list with names, built from the export and the current matches whenever she asks. | New task (T10) |
| The day-of path (building the whole bargaining range sheet in class from the final matches): does it replace the before-class build, or is it an option alongside it? | An option: she can still build from the draft before class, or skip that and build once from the final matches in class. | T8, workflow Stage 2 and 3 |
| Absent students on the bargaining range sheet: should their rows include their survey answers if they submitted them, and should they carry `UC_0` or a label like "Absent"? | Listed in a separate block below the matches, labeled "Absent", with their survey answers if they gave them. | T8 |
| The Qualtrics name dropdown: will it list names as `Last, First` (as on her class list)? Does she still want the email question in the survey? | `Last, First`, generated by the skill from the class list for her to paste into Qualtrics; email stays optional. | T6, T7, H4 |
| Late adds: her UC draft placed two students who joined late at the end instead of in alphabetical order. Should late adds always go at the end? | Strictly alphabetical, as decided; she can swap students in review. | T2 |
| Her UC draft lists a student by one first name and the final table and class list by another (a legal vs. preferred name). Which name should the skills write on new tabs? | The class-list name is written; other variants are linked when confident and otherwise reported for her to confirm. | T1, T4, T9 |
| Are the proposed time target (about 5 minutes per simulation) and highlight colors (orange for corrected typos, light red for unclear answers) acceptable to her? | Yes. | README, T6, T8 |

## For Aidan

| Item | Status |
|---|---|
| Open a copy of her workbook that has been saved by openpyxl in desktop Excel (ideally Windows) and confirm it opens without a repair prompt. `shared/tools/roundtrip_check.py` confirmed nothing in the content is lost; only Excel itself can confirm the file opens cleanly. | To do before the skills write to her real workbook |
| Write a step-by-step guide for her on using Claude and this workflow (requested in Meeting 3). | Planned; see the build plan |
| Confirm on a real Qualtrics export with a name dropdown that answers come out as positions in the pasted list (1, 2, …), and note the dropdown's question code for `name_choice` in `simulations.json`. Tested so far only on a fictional export. | To do when she adds the dropdown |

## Decided

| Decision | Source |
|---|---|
| Draft matches with her alphabetical method (first half Buyers, second half Sellers, matched in order). | Aidan, after reviewing her UC and SL tabs |
| Sort the class list strictly alphabetically. | Aidan |
| The skill fills in the simulation tab she prepares; it does not create tabs. She prefers a prepared template, with headers and match numbers, for every simulation. | Aidan; confirmed in Meeting 3 |
| Write both draft and final tables into her actual roster workbook, with a backup before every write. | Aidan |
| Role emails go out as BCC emails per role with the packet attached; the agent only prepares the address lists. | Interview 2 |
| Students learn their partners in class, not by email. | Interview 2 |
| The bargaining range sheet is built from the draft before class and quickly re-run after absences. | Aidan |
| Obvious typos are fixed and highlighted; unclear answers stay as typed and are highlighted. | Aidan |
| Warn about repeat partners from earlier simulations now, so the logic is ready for later simulations. | Aidan |
| Focus on Used Car first; look at her other simulation templates afterwards. | Interview 2 and Aidan |
| Used Car is always the first simulation of the term, then Salary. | Meeting 4 |
| Salary outcomes sheet: built in class from the downloaded Google Form CSV plus the two Qualtrics exports (Supervisor, Subordinate), with the matches from her roster's `SL` tab. Saved as an Excel file like the Used Car sheet. | Meeting 4 |
| Salary sheet layout is her template: yellow columns come from the in-class Form, white columns from the Qualtrics survey before class. Each side has both an INITIAL OFFER (planned, Qualtrics) and an ACTUAL INITIAL (spoken in class, Form). | Meeting 4 |
| Salary sheet: every money value shown as a total salary, formatted with $ and commas for a cleaner look. | Meeting 4 |
| Used Car doesn't use the Google Form: she fills ACTUAL IO and OUTCOME by hand during the same-day debrief. | Meeting 4 |
| Experimental conditions (I/C) are assigned per student for Used Car only, about half of the women and half of the men in each. Students in the same condition are matched together; intervention students get different role packets, so there are four BCC lists (Buyer-I, Buyer-C, Seller-I, Seller-C). | Meeting 4 |
| I/C is kept in mind after absences: a stranded student joins the nearest earlier match in the same condition, or she is asked. | Meeting 4 |
| Students who declined consent are paired together where possible; their roles may be swapped to make that work. | Meeting 4 |
| The baseline survey (Week 1, number codes) is read once to record Gender and Consent on the class list, in two columns just after Email. A student who didn't take it counts as declined; a student who chose "Other" for gender is excluded from the research. Only gender and consent for now; the full codebook dataset and Prolific come later. | Meeting 4 |
| Two skills: `negotiation-pairing` and `bargaining-range-sheet`. | Aidan |
| Her real files are used for local testing only and never committed to the public repo. | Aidan |
| A stranded student joins the previous match in the same role (with an exception still to be clarified, above). | Meeting 3 |
| Absent students are listed with `UC_0` on the simulation tab, under their own role's columns. | Meeting 3 |
| A student who drops the class keeps their history from earlier simulations. They are treated as absent (`_0`) for the simulation in the week they drop, and left off the tabs of later simulations. | Meeting 3 |
| Only the Used Car simulation has an experimental condition (the `Intervention` column). | Meeting 3 |
| No student should be the "1" in a 1v2 match more than once: the student alone on their side of a three-person match, counted across all simulations of the term. Drafting and absence updates avoid giving them that spot again; if it can't be avoided, she is warned or asked. | Meeting 3; scope confirmed by Aidan |
| Absent students stay on the bargaining range sheet for later research, in separate rows at the bottom. | Meeting 3 |
| She emails students who haven't submitted the survey; Claude gives her the list of who hasn't. | Meeting 3 |
| She wants an alternate path that builds the whole bargaining range sheet in class on the day, from the final matches, so there is no separate absence update of the sheet. | Meeting 3 |
| The Qualtrics survey can use a dropdown of student names instead of free-typed names. | Meeting 3 |
| Salary negotiation pairing: each student keeps their Used Car side (Buyers on the left as Supervisors, Sellers on the right as Subordinates), sorted alphabetically; the right column moves down one and the bottom student goes to the top. Students who missed Used Car keep the side of their Used Car role. Repeats are shown to her in review, not fixed silently. | Meeting 3; details confirmed by Aidan |
| She wants a step-by-step guide for using Claude and this workflow. | Meeting 3 |
