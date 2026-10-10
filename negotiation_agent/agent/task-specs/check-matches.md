# Check Matches Task Specification

## Basic Information

- **Task ID:** T3
- **Task name:** Check Matches
- **Task type:** Verify
- **Task owner:** Negotiation Pairing Solution (`negotiation-pairing` skill); the Instructor is accountable.

## 1. Task Description

T3 checks a set of matches against fixed rules before anything is written. It runs on:
- every draft from T2;
- every draft the Instructor edits in Excel during H2 (read back from the tab's draft table);
- the final matches proposed by T9.

The rules are:
1. Every student on the class list appears exactly once, unless absent.
2. No absent student appears in a match.
3. Every match has at least one Buyer and one Seller. At most one role in a match has a second student.
4. No student appears who is not on the class list.
5. In the absence update only, no student's role differs from their role in the draft, because role packets have already been sent.
6. Two students in the same match who already share a pair ID other than `_0` from an earlier simulation are flagged as a repeat.

Rules 1–5 are errors that block approval. Rule 6 is a warning the Instructor may accept. For Used Car, the first simulation of the term, rule 6 normally finds nothing, but it runs anyway, so it is already tested when later simulations are added. T3 reports problems but never changes the matches or undoes her edits.

## 2. Inputs

### Input 1

- **Input name:** Matches to check
- **Contents and format:** Draft matches from T2, her edited draft table read back from the tab, or final matches from T9.
- **Source:** T2, H2, or T9.

### Input 2

- **Input name:** Class snapshot and pair history
- **Contents and format:** Class list and absent students from T1/T2/H5; earlier pair IDs from T1; draft roles when checking an absence update.
- **Source:** T1, T2, and H5.

- **If a required input is missing or invalid:** If her edited draft table can't be read (for example, a header was changed), T3 names the cell area and asks her to restore it; it does not guess what an edited cell means.

## 3. Outputs

### Output 1

- **Output name:** Check report
- **Contents and format:** A list of errors and warnings in plain language (for example, "Ana Lopez appears twice: matches 3 and 9"; "Ben Novak and Lena Ortiz were already partners in UC_2"), with a one-line summary.
- **Next task or recipient:** H2: Review Draft Matches, or H6: Confirm Final Matches.
- **Complete when:** All six rules have been checked and every finding is listed.

## 4. Planned Tools

### Tool 1

- **Tool name:** `check_matches`
- **Input:** Matches to check; Class snapshot and pair history.
- **Output:** Check report.
- **Implementation Route:** Functions/scripts; a Python script bundled with the skill that applies the six rules. It logs the summary line.
- **Integration approach:** Direct integration.
- **Role in this task:** Checks and reports. It cannot approve or change matches.
- **Task timeout:** 15 seconds for one task run.
- **Maximum retries:** 1
- **Retry only when:** Reading her edited draft back from the workbook fails because the file is open in Excel. Ask her to save and close it, then retry once.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Check failed," log the error, and tell the Instructor. Matches that have not passed T3 cannot be approved or written.
