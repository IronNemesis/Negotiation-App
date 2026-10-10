# About the Agentic System

**A Negotiation Simulation Pairing and Bargaining Range Agent**
> **Problem to be solved**: A Cal Poly negotiation instructor runs in-class negotiation simulations all term, starting with the Used Car negotiation, in which every student is matched with a partner and given a role (Buyer or Seller). A few days before class she drafts the matches by hand in her course roster workbook, using a tab per simulation and a pair ID per match (such as `UC_4`) so she can see who has already negotiated together. She then emails each role its packet, BCCing all the students in that role. Before class, students complete a Qualtrics survey with their initial offer, target, reservation price, and BATNA. She cleans the messy export by hand ("$13000", "12,000", ">8,800", typos) and re-types it into a bargaining range sheet with one row per match, Buyer on the left and Seller on the right, so the class can debrief each pair's bargaining zone. In class, she finds out who is absent, moves the stranded partners into neighboring matches, and updates both files. Each simulation costs her about 30 minutes of this work outside class. She wants to keep using Excel, Qualtrics, and Outlook, to see and be able to change every step, and to have something that keeps working as her courses change.


### System Designer Name

Aidan Jones


### System Name

Negotiation Pairing Solution

### System Goal
**For** the negotiation instructor running paired simulations, starting with Used Car, **improve** how much of the matching, role-email preparation, survey cleaning, and bargaining-sheet re-typing she does by hand, **measured by** minutes of manual work outside class per simulation, **moving from** a baseline of about 30 minutes (her estimate) **to** a target of about 5 minutes, spent reviewing the draft, answering the agent's questions, and sending the role emails (proposed target, to confirm with her), **without** replacing Excel, Qualtrics, or Outlook, changing any tab of her workbook other than the current simulation's, changing a student's role after role packets are sent, sending any message on her behalf, or changing her files without a backup and a log entry.

### Who Is Better Off When This Works?

The instructor gets back most of the half hour she spends on every simulation and walks into class with the bargaining range sheet already built. Students get correctly assigned roles, partners they haven't negotiated with before, and a debrief built from accurately transferred numbers.

### Design Principles

- **Her files, her conventions.** The agent works inside her own roster workbook and produces the bargaining range sheet in her exact layout. Everything follows [`docs/workbook-conventions.md`](docs/workbook-conventions.md).
- **Her method, not a new one.** Matches are drafted with the alphabetical method she already uses, so she can check them at a glance.
- **Transparent.** Every change is backed up first and written to a plain-language log. Corrected survey answers are highlighted, with the original kept in a comment.
- **Manual edits are always allowed.** She can edit the draft in Excel; the agent re-checks it and points out problems but never reverses her edits.
- **Rules are fixed; judgment stays with her.** Drafting, absence updates, cleaning, and matching follow fixed rules carried out by scripts. Anything uncertain (who a survey response belongs to, where a stranded student should go) is her decision.
- **Future-proof.** The workflow is plain-language task specifications plus small scripts. Simulation details live in one settings file per skill, so adding a simulation later means adding an entry, not a new system.

### Two Skills

The workflow is delivered as two Claude Skills, because the instructor uses them at different moments and for different requests:

| Skill | When she uses it | What it does |
|---|---|---|
| `negotiation-pairing` | A few days before class, then again in class | Drafts the matches into the simulation tab, builds a BCC list per role, and applies absences to write the final matches |
| `bargaining-range-sheet` | After the survey closes, then again after absences | Cleans the Qualtrics export, matches responses to students, and builds the bargaining range sheet |

Both run in the Claude desktop app on her Windows computer, with access to the folder holding her roster workbook. Neither sends email. See [`agent/workflow-of-tasks.md`](agent/workflow-of-tasks.md) for the full workflow and [`docs/open-questions.md`](docs/open-questions.md) for what is still to be confirmed.

The first prototype (a single skill built before the instructor's files were available) is kept in [`archive/prototype-v1/`](archive/prototype-v1/).
