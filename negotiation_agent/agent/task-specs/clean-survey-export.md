# Clean Survey Export Task Specification

## Basic Information

- **Task ID:** T6
- **Task name:** Clean Survey Export
- **Task type:** Reason
- **Task owner:** Negotiation Pairing Solution (`bargaining-range-sheet` skill); the Instructor is accountable.

## 1. Task Description

Students type their answers freely, so the export arrives as `13000`, `$13000`, `"12,000"`, `>8,800`, `$10,500-10,250`, or `10` meaning 10,000. Today the Instructor cleans these by hand. T6 applies her cleaning with fixed rules. Every change it makes is visible: a corrected answer is highlighted, and its original stays in a cell comment.

The rules, applied to the four price questions (initial offer, target, reservation, BATNA):

1. **Plain numbers:** remove spaces, `$`, and thousands commas. If what remains is a number, store it as a number, with no highlight. `$13,000` becomes 13000.
2. **Obvious typos:** two forms are corrected and highlighted **orange**, with the original answer in a comment:
   - a number below 100, which is multiplied by 1,000 (`10` becomes 10000, `9.4` becomes 9400);
   - a number written with `k`, which is expanded (`8.8K` becomes 8800).
3. **Unclear answers:** anything that is not a plain number after rule 1 is **kept exactly as typed** and highlighted **light red**: `>8,800`, `$10,500-10,250`, `$8,800 (sell to dealer)`. These stay hers to interpret.
4. **Out of range:** a plain number outside the simulation's usual range (set in the skill's settings; for example $1,000–$50,000 for Used Car) is kept as typed and highlighted **light red** with a comment, because it may be intentional. An example is a BATNA of 200.

Other columns:
- **Perception items** (six questions, answers `1`–`4`) and **role** (`1` or `2`) are copied as numbers.
- **Names and emails** are trimmed; emails are lowercased.
- **Rows removed:** responses with every answer blank, and preview or test responses (a `Status` other than a normal response). These are removed and counted in the summary.

## 2. Inputs

### Input 1

- **Input name:** Qualtrics export
- **Contents and format:** The CSV as downloaded, with the three header rows (codes, question text, `ImportId`) and numeric answer codes, as described in [`workbook-conventions.md`](../../docs/workbook-conventions.md).
- **Source:** The Instructor, who downloads it from Qualtrics and tells Claude where it is.

### Input 2

- **Input name:** Survey settings
- **Contents and format:** For the simulation: which column holds each field (`Q1` first name … `Q11` email), the price columns, the usual price range, and the role codes.
- **Source:** The skill's settings file.

- **If a required input is missing or invalid:** If the file is not a Qualtrics CSV, or a column named in the settings is missing (for example, the survey was edited and `Q6` no longer exists), T6 stops with status "Survey layout changed" and the case goes to H1. Nothing is built from a misread export.

## 3. Outputs

### Output 1

- **Output name:** Cleaned responses
- **Contents and format:** One record per kept response: response ID, submission time, first and last name as typed, email, role code, the four prices (as cleaned numbers or original text), the six items, and for each price a flag (clean, corrected, unclear, or out of range) with the original answer.
- **Next task or recipient:** T7: Match Survey Responses to Students.
- **Complete when:** Every row in the export is either kept and cleaned or removed with a reason, and every corrected or unclear value carries its original answer.

### Output 2

- **Output name:** Cleaning summary
- **Contents and format:** Counts of responses kept and removed, plus each corrected and each unclear answer (for example, "Alyssa W., target: `10` → 10,000"), shown in the chat.
- **Next task or recipient:** The Instructor.
- **Complete when:** Every change and every flagged value is listed.

## 4. Planned Tools

### Tool 1

- **Tool name:** `clean_survey`
- **Input:** Qualtrics export; Survey settings.
- **Output:** Cleaned responses; Cleaning summary.
- **Implementation Route:** Functions/scripts; a Python script bundled with the skill that reads the CSV (including Excel-style quoting and the three header rows) and applies the four rules. It reads only; the original export is never changed.
- **Integration approach:** Direct integration.
- **Role in this task:** Normalizes answers by fixed rules. It never invents a value: anything it can't clean with confidence stays as typed.
- **Task timeout:** 15 seconds for one task run.
- **Maximum retries:** 1
- **Retry only when:** The CSV is open in Excel and can't be read. Ask the Instructor to close it, then retry once.
- **On timeout, exhausted retries, or an error that cannot be retried:** Set status to "Failed," log the error, and tell the Instructor. T7 does not run.
