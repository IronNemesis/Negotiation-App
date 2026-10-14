# Agent Test Runs

Besides the automated tests in this folder, each skill was tested end to end by a fresh Claude agent given only the skill folder, a copy of the fictional example files, and a realistic request. The instructor's answers to the agent's questions were supplied up front, because she isn't available during a test. A script then compared what each agent produced against a reference result made directly by the skill's script from untouched copies of the same files.

## October 2026: 22 of 22 checks passed

| Test | Request | Her supplied answers | Checks |
|---|---|---|---|
| 1. Draft and role emails | "Set up the partners for Used Car on Thursday? Owen Bennett emailed me that he'll be out. Then give me the email lists." | Approves the draft; later says the role emails were sent | 7/7: draft matches her method without Owen Bennett; final table untouched; other tabs unchanged; BCC lists for 19 Buyers and 19 Sellers; roles recorded as sent; backup made; draft shown before writing |
| 2. Absences in class | "Adebayo, Rosa Castellano and Tess aren't here. Update the Used Car partners." | Confirms the final matches | 5/5: final matches identical to the expected result; absent students with `UC_0`; draft and other tabs unchanged; moves explained |
| 3. Bargaining range sheet | "The survey closed and I put the Qualtrics download in the folder. Can you make my bargaining range sheet?" | Week 2; "Dani Park" is Danielle; "Jordan Evens" is Jordan Evans; use the latest of duplicate submissions | 5/5: sheet identical cell for cell to the reference build; roster unchanged; all three questions asked in one message; corrections reported |
| 4. Hard absences | "Mahoney and Park are missing today, can you fix the partners?" | Daniel Park; put a student who doesn't fit in match 17 | 5/5: asked which Park; Daniel's partner moved to match 6; the stranded Seller who didn't fit placed in match 17 as she chose; final table passes every check |

Gaps the agents reported, and what changed:

- **Roles not recorded as sent on class day.** The pairing skill now asks once whether the role emails went out, and records it. Recording only writes to the log.
- **Absent Sellers listed under the Buyer columns.** Absent students are now listed under their own role. This is added to the open questions for her.
- **Bargaining sheet tab name.** The main tab was named with Excel's 31-character cut of the export's file name. It is now `Week <N> <Simulation>`.
- **Redundant logging instruction.** The pairing skill no longer asks to log decisions that the script already logs.

To repeat these runs, give an agent the skill folder path, a copy of the matching example workbook (and the CSV for test 3), the request, and the supplied answers above. Ask it to write every message it would have shown the instructor to a `summary.md`.
