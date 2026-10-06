# Open Questions

The workflow is drafted from one requirements interview. Each item below is an assumption in the current draft that should be confirmed with the instructor. The **Affects** column shows which task specifications change if the answer differs.

## Files to Request

| Item | Why it matters | Affects |
|---|---|---|
| A copy of her current pair-ID spreadsheet (names can be removed) | T1 must read it and T5 must write to it in her exact layout and pair-ID format. | T1, T5 |
| The role information, bargaining range, and used car outcomes sheets | T9 fills her outcomes template exactly; T6 needs the role information. | T6, T9 |
| A sample Qualtrics export (answers can be removed) | Sets the survey column mapping and the student ID column. | T7, T8 |
| Her Word mail merge document for role emails, if one exists | T6's fixed column names should match her merge fields. | T6, H5 |
| A sample roster export | Confirms the roster columns T1 expects. | T1 |

## Pairing (Stage 1)

| Question | Current assumption | Affects |
|---|---|---|
| Should roles be balanced across negotiations (for example, each student is a buyer once and a seller once)? | Role balancing is a per-simulation setting, on when past roles are recorded. | T3, T4 |
| Does her spreadsheet record which role each student played, or only pair IDs? | Roles are recorded only if her spreadsheet already does. | T1, T5 |
| Do all her simulations use pairs, or do some use larger groups (for example, a 5-person coalition)? | Pairs with two roles only. Larger groups would need a group version of the "no shared ID" rule. | T1, T3, T4 |
| Do other simulations use the same pairing rules as Used Car? | Yes; each simulation is one row in Simulation Settings. | T1, T3 |
| How many sections, students per section, and negotiations per term? | About 100 students (50 buyers, 50 sellers) across her sections; pairing history is kept per section. | T3 (search time) |
| When does pairing happen relative to class (days before, the morning of, during class)? | Before class, early enough for students to read their role email. | Trigger |
| How does she learn about absences? | She lists them in her request to the agent. | T2 |
| Should the role email tell students who their partner is? | No; partners are not included in the mail merge. | T6 |
| Is the survey link the same for all students, or does each role have its own survey? | One link per simulation. | T6, T7 |

## Role Emails

| Question | Current assumption | Affects |
|---|---|---|
| How is role information delivered today: in the email body, as an attachment, or as a link? | Text or a link. Word/Outlook mail merge cannot attach a different file to each email, so attachments would need a different approach. | T6, H5 |
| Who should the emails come from, and should replies go to a different address? | Her own Outlook account. | H5 |

## Survey Data (Stage 2)

| Question | Current assumption | Affects |
|---|---|---|
| Is the survey taken before the negotiation (planning numbers) or after? | Does not change the workflow; Stage 2 runs once the survey closes. | Trigger |
| What order does she want in the outcomes sheet (one row per student)? | Partners on adjacent rows, in pair order. | T9 |
| What does she do with the finished outcomes sheet: an in-class debrief, grading, or research? | In-class debrief. If it feeds grading or research, add a check that outcomes are complete. | T9 |
| What goes wrong today when she re-enters survey data? | Typos, students without a response, and duplicates. | T8, H6 |
| Does she want the agent to summarize the outcomes after class (for example, a chart of deals against bargaining ranges)? | Out of scope for now. | New task |

## Deployment

| Question | Current assumption | Affects |
|---|---|---|
| Can the Claude desktop app be installed and used on her computer? | Yes, with access to one course folder. | Where It Runs |
| Where should the course folder live: OneDrive or a local folder? | OneDrive, so backups survive a computer change. Files open in Excel can be locked while syncing. | All file tasks |
| How much time does pairing and re-entry take her per simulation today? | Unknown; this sets the baseline in the system goal. | README |
