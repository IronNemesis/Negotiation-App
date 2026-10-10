# Archived: Prototype v1

This folder holds the first version of the Negotiation Pairing Solution: workflow, task specs, a single Claude Skill, fictional example files, and evals. It was built from the first interview, before the instructor shared her real files.

It was replaced because her files showed that several of its assumptions were wrong:

- Pairing history lives in her roster workbook as one tab per simulation with `UC_4`-style pair IDs, not in a separate Pairing History workbook.
- Students are identified by name and Cal Poly email; there are no student ID numbers.
- Matches are drafted days ahead and roles are locked once packets are sent; absences are handled by moving the stranded partner into the previous match, not by re-pairing.
- The bargaining range sheet has one row per match, mirrored Buyer | Outcome | Seller, not one row per student.
- Role emails go out as BCC emails per role, not a mail merge.

The current design is in [`../../README.md`](../../README.md). Nothing in this folder is maintained.
