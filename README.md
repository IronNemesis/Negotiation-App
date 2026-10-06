# Negotiation Pairing Solution

An agentic workflow that takes the repetitive work out of running in-class negotiation simulations. It pairs students so nobody negotiates with the same partner twice in a section, prepares each student's role email for an Outlook mail merge, and turns the Qualtrics survey export into an outcomes workbook in pairing order. It works with the tools the instructor already uses (Excel, Qualtrics, and Outlook mail merge) and leaves every decision with her.

- [`negotiation_agent/README.md`](negotiation_agent/README.md): the problem, system goal, and design principles
- [`negotiation_agent/agent/workflow-of-tasks.md`](negotiation_agent/agent/workflow-of-tasks.md): the full workflow, diagram, and task index
- [`negotiation_agent/agent/task-specs/`](negotiation_agent/agent/task-specs/): one specification per task
- [`negotiation_agent/docs/open-questions.md`](negotiation_agent/docs/open-questions.md): assumptions still to be confirmed with the instructor
- [`negotiation_agent/skill/negotiation-pairing-solution/`](negotiation_agent/skill/negotiation-pairing-solution/): the Claude Skill that runs the workflow (instructions plus the `nps.py` script)
- [`negotiation_agent/examples/`](negotiation_agent/examples/): fictional course files, test tools, and a testing guide
