# Retrieve Survey Export and Approved Pairs Task Specification

## Basic Information

- **Task ID:** T7
- **Task name:** Retrieve Survey Export and Approved Pairs
- **Task type:** Retrieve
- **Task owner:** Negotiation Pairing Solution; the Instructor is accountable.

## 1. Task Description

T7 starts every Stage 2 run. It reads the Qualtrics survey export the Instructor saved into the simulation folder, the approved pairing for the same section and simulation, and the simulation's survey column mapping. The mapping in Simulation Settings tells T7 which Qualtrics column holds the student ID and which hold each bargaining number (for example, worst acceptable price, ideal price, opening offer). That way, a change to the survey only requires editing one settings row. T7 skips Qualtrics' extra header rows and preview or test responses, and passes along only real responses. It does not change any file.

## 2. Inputs

### Input 1

- **Input name:** Survey export
- **Contents and format:** `Survey Export.csv`, the Qualtrics CSV export, with one row per response, including a student ID column and the bargaining-range questions.
- **Source:** The Instructor, who downloads the export from Qualtrics and saves it into the simulation folder.

### Input 2

- **Input name:** Approved pairing
- **Contents and format:** The approved `Pairing Draft.xlsx` for this section and simulation, with T5's recording confirmed in the Run Log.
- **Source:** Stage 1 of this workflow.

### Input 3

- **Input name:** Survey column mapping and outcomes template
- **Contents and format:** From the simulation's Simulation Settings row: the student ID column, each survey column and the outcomes column it maps to, and the outcomes template file name.
- **Source:** The Instructor, who maintains Simulation Settings.

- **If a required input is missing or invalid:** If the export is missing or unreadable, a mapped column is not in the export, no recorded Stage 1 pairing exists for this simulation, or the outcomes template file is missing, T7 stops with status "Retrieval failed" and the case goes to H1: Resolve Section Data Issue. If the export contains a column the mapping does not mention, T7 ignores it and notes it in the Run Log.

## 3. Outputs

### Output 1

- **Output name:** Survey snapshot
- **Contents and format:** Structured record: run ID, export file name and time, response rows (student ID as entered, mapped bargaining values, submission time), and the count of removed preview, test, or header rows.
- **Next task or recipient:** T8: Match Survey Responses to Students.
- **Complete when:** Every row in the export has been classified as a response or a removed row with a reason.

### Output 2

- **Output name:** Pairing and template record
- **Contents and format:** The approved pairs in pair order, with roles, and the outcomes template location.
- **Next task or recipient:** T8: Match Survey Responses to Students; T9: Build Outcomes Workbook in Pairing Order.
- **Complete when:** The pairing matches the recorded Pairing History entries for this simulation.

### Output 3

- **Output name:** Retrieval failure report
- **Contents and format:** Run Log entry produced only on failure: run ID, the file or column that failed, failure category, attempts, and time.
- **Next task or recipient:** H1: Resolve Section Data Issue (Instructor).
- **Complete when:** The report names the exact file or column that failed and is explained in the chat.

## 4. Planned Tools

### Tool 1

- **Tool name:** `read_survey_export`
- **Input:** Survey export; Approved pairing; Survey column mapping and outcomes template.
- **Output:** Survey snapshot; Pairing and template record; Retrieval failure report.
- **Implementation Route:** Functions/scripts; a local Python script bundled with the agent's skill that reads the CSV and workbooks read-only and applies the column mapping and row-removal rules. The only write is the Run Log entry.
- **Integration approach:** Direct integration.
- **Role in this task:** Reads and cleans the survey data. It cannot edit the export, the pairing, or Simulation Settings.
- **Task timeout:** 30 seconds for one task run, including retries.
- **Maximum retries:** 1
- **Retry only when:** A file is locked because it is open in Excel. Ask the Instructor to close it, then retry once.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Retrieval failed," write the failure report, and hand the case to H1. Do not build an outcomes workbook from a partial export.
