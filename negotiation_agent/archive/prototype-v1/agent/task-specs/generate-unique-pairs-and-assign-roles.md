# Generate Unique Pairs and Assign Roles Task Specification

## Basic Information

- **Task ID:** T3
- **Task name:** Generate Unique Pairs and Assign Roles
- **Task type:** Reason
- **Task owner:** Negotiation Pairing Solution; the Instructor is accountable.

## 1. Task Description

T3 creates the pairing for this negotiation. It follows the Instructor's own rule: two students may be paired only if they do not already share a pair ID in this section's Pairing History. T3 searches for a pairing in which every attending student has exactly one partner and no pair repeats. If no such pairing exists, which becomes possible late in the term with a small section, T3 returns the pairing with the fewest repeated partners and flags each repeat for the Instructor; it never hides a repeat. Within each pair, one student receives each of the simulation's two roles. When role balancing is on and past roles are recorded, the student who has played a role fewer times receives it; otherwise roles are assigned at random. If the Instructor chose an arrangement for an odd student count in H3, T3 applies it. The random seed is recorded so the same draft can be reproduced. T3 decides nothing the Instructor has not delegated; it proposes a draft for T4 and H4.

## 2. Inputs

### Input 1

- **Input name:** Attendance list
- **Contents and format:** Attending students and attending count from T2.
- **Source:** T2: Build Attendance List from Absences.

### Input 2

- **Input name:** Pair history
- **Contents and format:** Each attending student's existing pair IDs, and past roles if recorded, from the section snapshot.
- **Source:** T1: Retrieve Section Roster and Pairing History.

### Input 3

- **Input name:** Simulation configuration
- **Contents and format:** The simulation's two roles and whether role balancing is on.
- **Source:** T1: Retrieve Section Roster and Pairing History.

### Input 4

- **Input name:** Odd-count arrangement
- **Contents and format:** The Instructor's choice from H3: one group of three (with the role given to the third member), the Instructor partners with one named student, or one named student observes this round.
- **Source:** H3: Decide Arrangement for Odd Student Count, only when the attending count is odd.

### Input 5

- **Input name:** New draft request
- **Contents and format:** The Instructor's request from H4 for a different draft, optionally with constraints such as "keep these two apart."
- **Source:** H4: Review and Approve Pairing Draft, only when she asks for a new draft.

- **If a required input is missing or invalid:** If the attending count is odd and no H3 arrangement exists, T3 does not run; the case goes to H3. If fewer than two students are attending, T3 stops and tells the Instructor there is nobody to pair.

## 3. Outputs

### Output 1

- **Output name:** Pairing draft
- **Contents and format:** Structured record: run ID, seed, and one row per student with draft pair number, student ID, name, role, partner name, and a "repeat partner" flag; plus the count of repeated pairs.
- **Next task or recipient:** T4: Validate Pairing Draft.
- **Complete when:** Every attending student appears exactly once, every pair has one student in each role (or matches the H3 arrangement), and the number of repeated pairs is the lowest the search found.

## 4. Planned Tools

### Tool 1

- **Tool name:** `generate_pairs`
- **Input:** Attendance list; Pair history; Simulation configuration; Odd-count arrangement; New draft request.
- **Output:** Pairing draft.
- **Implementation Route:** Functions/scripts; a local Python script bundled with the agent's skill that searches for a pairing with no shared pair IDs (repeated randomized attempts with a repair step) and assigns roles by the balancing rule. Writes a Run Log entry with the seed and the repeat count.
- **Integration approach:** Direct integration.
- **Role in this task:** Produces the draft. It cannot write to Pairing History; nothing is recorded until H4 approval and T5.
- **Task timeout:** 60 seconds for one task run.
- **Maximum retries:** 0
- **Retry only when:** Not applicable; a new draft is requested through H4, not retried automatically.
- **On timeout, exhausted retries, or an error that cannot be retried:** If the search reaches the time limit, return the best pairing found so far with its repeats flagged and note in the Run Log that the search was cut short. If the script fails, set status to "Failed," record the error, and tell the Instructor in the chat. No partial pairing is passed to T4.
