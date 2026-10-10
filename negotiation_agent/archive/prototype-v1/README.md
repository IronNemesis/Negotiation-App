# About the Agentic System

**A Negotiation Simulation Pairing and Survey Data Agent**
> **Problem to be solved**: A Cal Poly negotiation instructor runs in-class negotiation simulations, such as the Used Car negotiation, in which every student is paired with a partner and given a role (for example, buyer or seller). Her goal is to mix students as much as possible, so nobody negotiates with the same partner twice in a section. She tracks this by hand in a spreadsheet: each time two students negotiate, both receive a shared pair ID next to their names, and two students who already share an ID should never be paired again. After pairing, she emails each student their role information. Students then complete a short Qualtrics survey (4–5 questions about their bargaining range, such as worst acceptable price, ideal price, and opening offer). The survey export has one row per student in no useful order, so she manually re-enters the data in pairing order into an outcomes spreadsheet, and then fills in the outcome column by hand during class. Each step is repetitive, error-prone, and repeated for every simulation in every section. She tried automating similar work with Power Automate and found it hard to change and hard to see into. She wants to keep using the tools she already knows (Excel, Qualtrics, and Outlook mail merge), stay in control of every decision, and have a solution that keeps working as her courses change.


### System Designer Name

Aidan Jones


### System Name

Negotiation Pairing Solution

### System Goal
**For** the negotiation instructor running paired simulations across her course sections, **improve** how much of the pairing, role-email preparation, and survey re-entry work she must do by hand, **measured by** hours of manual data entry per term, **moving from** a baseline of fully manual pairing, history tracking, and survey re-entry for every simulation in every section (exact hours to be measured with the instructor) **to** a target where her remaining manual work is entering absences, reviewing and approving each pairing, sending the Outlook mail merge, and filling in outcomes during class, **without** replacing her existing tools (Excel, Qualtrics, Outlook mail merge), sending any message to students on her behalf, pairing students who have already negotiated together unless she approves it, or changing any of her files without a backup and a visible log entry.

### Who Is Better Off When This Works?

The instructor gets back the hours she spends pairing students, tracking pair history, and re-typing survey data, and she can see and edit every result in the Excel files she already uses. Students are better off because they negotiate with a new partner every time, receive the correct role, and get a debrief built from accurately transferred survey data.

### Design Principles

These follow directly from what the instructor asked for.

- **Her tools, not a new app.** Every input and output is an Excel workbook, a Qualtrics CSV export, or an Outlook mail merge she runs herself. She can open, read, and edit any file the system touches.
- **Transparent.** Every action the agent takes is written to a Run Log workbook in plain language. Every pairing is shown to her as a draft before anything is recorded.
- **Manual edits are always allowed.** She can edit any draft directly in Excel. The agent re-checks her edits and points out problems, but it never reverses them.
- **Rules are fixed; judgment stays with her.** Pairing, history tracking, and survey matching follow fixed rules carried out by scripts, so the same inputs always give the same checks. Anything ambiguous (an absence that doesn't match a name, an odd number of students, a duplicate survey response) goes to her to decide.
- **Future-proof.** The workflow is written as plain-language task specifications that a general-purpose agent follows, plus a small set of scripts. Simulation details (roles, survey questions, templates) live in a settings workbook she can edit, so adding a new simulation does not require changing the system.

### Where It Runs

The workflow is designed to run in the Claude desktop app on the instructor's Windows computer, with access to one course folder of Excel files. She starts each stage by asking in plain language (for example, "Pair Section 01 for Used Car. Maria Lopez and Dev Shah are absent."). The agent reads and writes files only inside that folder, and it never sends email; she sends role emails through her own Outlook mail merge. See [`agent/workflow-of-tasks.md`](agent/workflow-of-tasks.md) for the full workflow and [`docs/open-questions.md`](docs/open-questions.md) for details still to be confirmed with the instructor.
