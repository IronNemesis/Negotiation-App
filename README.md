# Negotiation Pairing Solution

An agentic workflow that takes the repetitive work out of running in-class negotiation simulations, starting with the Used Car negotiation. It drafts student matches in the instructor's own roster workbook using her own method and conventions, prepares the BCC lists for her role emails, updates the matches for absences in class, and turns the messy Qualtrics survey export into her bargaining range sheet for the debrief. It works with the tools she already uses (Excel, Qualtrics, Outlook) and leaves every decision with her.

- [`negotiation_agent/README.md`](negotiation_agent/README.md): the problem, system goal, design principles, and the two skills
- [`negotiation_agent/agent/workflow-of-tasks.md`](negotiation_agent/agent/workflow-of-tasks.md): the full workflow, diagram, and task index
- [`negotiation_agent/agent/task-specs/`](negotiation_agent/agent/task-specs/): one specification per task
- [`negotiation_agent/docs/workbook-conventions.md`](negotiation_agent/docs/workbook-conventions.md): the instructor's workbook, survey, and sheet conventions the skills follow
- [`negotiation_agent/docs/open-questions.md`](negotiation_agent/docs/open-questions.md): assumptions still to be confirmed with the instructor
- [`negotiation_agent/archive/prototype-v1/`](negotiation_agent/archive/prototype-v1/): the first prototype, kept for reference

- [`negotiation_agent/skills/bargaining-range-sheet/`](negotiation_agent/skills/bargaining-range-sheet/): the skill that cleans the Qualtrics export and builds the bargaining range sheet
- [`negotiation_agent/examples/`](negotiation_agent/examples/): fictional files in the instructor's formats, with expected results
- [`negotiation_agent/tests/`](negotiation_agent/tests/): automated tests against the example files

The `negotiation-pairing` skill is next.
