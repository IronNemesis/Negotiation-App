# Draft Matches Task Specification

## Basic Information

- **Task ID:** T2
- **Task name:** Draft Matches
- **Task type:** Reason
- **Task owner:** Negotiation Pairing Solution (`negotiation-pairing` skill); the Instructor is accountable.

## 1. Task Description

T2 drafts the matches using the Instructor's own method, so the result looks like what she would have made and she can check it at a glance. For Used Car, the first simulation of the term:

1. Sort the class list alphabetically by last name, then first name, leaving out any student she has already said will be absent.
2. Split it in half. The first half are Buyers and the second half are Sellers. With an odd count, the second half has one extra student.
3. Match in order: the first Buyer with the first Seller, and so on, numbering matches from 1.
4. With an odd count, the extra Seller joins the last match as a second Seller, on a row with no match number.

Students she named as absent in advance are left out of the draft and kept for T9, which records them as `_0`.

For later simulations, she keeps the alphabetical halves and shifts the second half to avoid former partners. That rule will be specified when later simulations are added. Until then, T2 drafts only simulations whose settings say "first simulation" (Used Car). T3 still checks every draft for repeats, so the check is ready for later simulations.

T2 makes no other choices. If she asks for changes in H2 ("swap these two", "move Ana to Seller"), T2 applies exactly those changes to the current draft rather than re-drafting.

## 2. Inputs

### Input 1

- **Input name:** Class snapshot
- **Contents and format:** Alphabetically sortable class list (name, email).
- **Source:** T1: Read Class List and Simulation Tab.

### Input 2

- **Input name:** Known absences
- **Contents and format:** Students the Instructor already knows will be absent, matched to the class list. An entry that matches no one, or more than one student, is asked about, not guessed.
- **Source:** The Instructor's run request.

### Input 3

- **Input name:** Requested changes
- **Contents and format:** Specific swaps or moves the Instructor asks for during review.
- **Source:** H2: Review Draft Matches, only when she asks for changes in the chat.

- **If a required input is missing or invalid:** If fewer than two students remain, T2 stops and tells the Instructor there is nobody to match. A requested change that names a student not on the class list is shown back to her with the closest names.

## 3. Outputs

### Output 1

- **Output name:** Draft matches
- **Contents and format:** Structured record: one entry per match (match number, Buyer, Seller), plus any second same-role student with the match they belong to; the known-absent students; and a note of every change she requested.
- **Next task or recipient:** T3: Check Matches.
- **Complete when:** Every student on the class list who is not known to be absent appears exactly once, with exactly one role.

## 4. Planned Tools

### Tool 1

- **Tool name:** `draft_matches`
- **Input:** Class snapshot; Known absences; Requested changes.
- **Output:** Draft matches.
- **Implementation Route:** Functions/scripts; a Python script bundled with the skill that applies the alphabetical method and the requested changes. It logs the method used and every requested change.
- **Integration approach:** Direct integration.
- **Role in this task:** Produces the draft in memory and as a preview. It cannot write to the workbook; T4 does that after approval.
- **Task timeout:** 15 seconds for one task run.
- **Maximum retries:** 0
- **Retry only when:** Not applicable; the method gives the same result for the same class list every time.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Failed," log the error, and tell the Instructor in the chat. No partial draft is passed to T3.
