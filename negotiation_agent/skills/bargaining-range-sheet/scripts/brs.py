"""Bargaining range sheet: clean a Qualtrics export and build the instructor's debrief sheet.

Commands (task IDs refer to negotiation_agent/agent/task-specs):
  prepare  T6 + T7  clean the export and match responses to the current matches; writes nothing
  build    T6-T8    the same, then write the bargaining range workbook next to the export

Both print one JSON object. "ok": false comes with an "error" code and a plain-language "message".
Decisions from the instructor (H4) are passed to both commands with --assign, --use, --leave-out,
and --latest-duplicates.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sys
import tempfile
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nps_shared as ns  # noqa: E402
from openpyxl import Workbook, load_workbook  # noqa: E402
from openpyxl.comments import Comment  # noqa: E402
from openpyxl.styles import Alignment, Font, PatternFill  # noqa: E402

SETTINGS = json.loads((HERE / "simulations.json").read_text(encoding="utf-8"))
ORANGE, LIGHT_RED, YELLOW, BAND = "F8CBAD", "FFC7CE", "FFFF00", "E2EFDA"
PRICE_ORDER = ["INITIAL", "TARGET", "RESERVATION", "BATNA"]
AUTHOR = "Claude (bargaining-range-sheet)"


# ---------------------------------------------------------------- T6: clean the export

@dataclass
class Answer:
    value: object          # a number, the text as typed, or None
    flag: str = ""         # "", "corrected", "unclear", "out_of_range"
    typed: str = ""


@dataclass
class Response:
    rid: str
    time: str
    first: str
    last: str
    email: str
    role_code: str
    prices: dict[str, Answer]
    items: list
    match_how: str = ""


def clean_price(text: str, low: float, high: float) -> Answer:
    typed = ns.clean(text)
    if not typed:
        return Answer(None, "", "")
    # A plain number followed by a note in parentheses, e.g. "$8,800 (sell to dealer)": the number is clear.
    note = re.fullmatch(r"(.*?\d)\s*\(([^()]*)\)", typed)
    compact = (note.group(1) if note else typed).replace("$", "").replace(",", "").replace(" ", "")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([kK])?", compact)
    if not m:
        return Answer(typed, "unclear", typed)
    number = float(m.group(1))
    scaled = bool(m.group(2)) or 0 < number < 100   # "8.8K", or "10" meaning 10,000
    if scaled:
        number *= 1000
    corrected = scaled or bool(note)
    number = int(number) if float(number).is_integer() else round(number, 2)
    if corrected:
        return Answer(number, "corrected", typed)
    if not low <= number <= high:
        return Answer(number, "out_of_range", typed)
    return Answer(number, "", typed)


def read_export(path: Path, sim: dict) -> tuple[list[list[str]], list[str], list[Response], list[dict]]:
    if not path.exists():
        raise ns.SkillError("file_missing", f"Could not find the survey export {path.name} in {path.parent}.")
    try:
        with path.open(newline="", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f))
    except PermissionError:
        raise ns.SkillError("file_locked", f"{path.name} is open in Excel. Close it and try again.")
    if len(rows) < 2:
        raise ns.SkillError("survey_empty", f"{path.name} has no responses.")
    codes = [c.strip() for c in rows[0]]
    skip = 2 if len(rows) > 2 and rows[2] and rows[2][0].startswith('{"ImportId') else (
        1 if rows[1] and rows[1][0].startswith('{"ImportId') else 0)
    questions = [c.strip() for c in rows[1]] if skip == 2 else codes

    def col(code: str) -> int:
        if code not in codes:
            raise ns.SkillError("survey_layout", f"The export has no '{code}' column. The survey may have been "
                                                 "edited; the skill's settings need updating.", {"columns": codes})
        return codes.index(code)

    s = sim["survey"]
    c_first, c_last, c_role, c_email = col(s["first_name"]), col(s["last_name"]), col(s["role"]), col(s["email"])
    c_prices = {name: col(code) for name, code in s["prices"].items()}
    c_items = [col(code) for code in s["items"]]
    c_status = codes.index("Status") if "Status" in codes else None
    c_rid = codes.index("ResponseId") if "ResponseId" in codes else None
    c_time = codes.index("RecordedDate") if "RecordedDate" in codes else None
    low, high = sim["price_range"]
    item_headers = [questions[c] for c in c_items]

    responses, removed = [], []
    for n, row in enumerate(rows[1 + skip:], start=1):
        row = row + [""] * (len(codes) - len(row))
        rid = row[c_rid] if c_rid is not None and row[c_rid] else f"row {n}"
        answer_cols = [c_first, c_last, c_role, c_email, *c_prices.values(), *c_items]
        if not any(ns.clean(row[c]) for c in answer_cols):
            removed.append({"response": rid, "reason": "every answer is blank"})
            continue
        status = ns.clean(row[c_status]) if c_status is not None else ""
        if status not in ("", "0", "IP Address"):
            removed.append({"response": rid, "reason": f"not a real response (status {status}, e.g. a survey preview)"})
            continue
        items = [int(v) if ns.clean(v).isdigit() else (ns.clean(v) or None) for v in (row[c] for c in c_items)]
        responses.append(Response(
            rid=rid, time=row[c_time] if c_time is not None else "", first=ns.clean(row[c_first]),
            last=ns.clean(row[c_last]), email=ns.clean(row[c_email]).lower(), role_code=ns.clean(row[c_role]),
            prices={name: clean_price(row[c], low, high) for name, c in c_prices.items()}, items=items))
    return rows, item_headers, responses, removed


# ---------------------------------------------------------------- current matches

@dataclass
class Participant:
    name: str          # as on the simulation tab, "Last, First"
    first: str
    last: str
    role: str
    match: int
    email: str
    response: Response | None = None
    role_conflict: str = ""


def load_matches(roster: Path, code: str, sim: dict):
    wb = ns.open_workbook(roster)
    _, students, class_warnings = ns.read_class_list(wb)
    tab = ns.read_sim_tab(wb, code, sim["roles"])
    if tab.final_members:
        stage, members = "final", tab.final_members
    elif tab.draft_members:
        stage, members = "draft", tab.draft_members
    else:
        raise ns.SkillError("no_matches", f"The '{code}' tab has no matches yet. Draft the matches first "
                                          "(negotiation-pairing skill).")
    warnings = list(class_warnings)

    def participant(m: ns.Member, match: int) -> Participant:
        res = ns.resolve_class_name(m.name, students, m.email)
        first, last = ns.split_class_name(m.name)
        if not res.confident:
            hint = f" (maybe {res.student.name})" if res.student else ""
            warnings.append(f"'{m.name}' on the {code} tab is not on the class list{hint}; "
                            "matching their survey response by name only.")
        email = res.student.email if res.confident else m.email
        return Participant(m.name, first, last, m.role, match, email)

    groups = {match: [participant(m, match) for m in ms] for match, ms in tab.groups(members).items()}
    absent = [participant(m, 0) for m in tab.absent] if stage == "final" else []
    return students, stage, groups, absent, warnings


# ---------------------------------------------------------------- T7: match responses

def pool_students(people: list[Participant]) -> list[ns.Student]:
    return [ns.Student(p.name, p.first, p.last, p.email, 0) for p in people]


def match_responses(responses, groups, absent, students, args):
    present = [p for g in groups.values() for p in g]
    by_name = {p.name: p for p in present}
    absent_names = {p.name for p in absent}
    present_pool, absent_pool = pool_students(present), pool_students(absent)
    by_rid = {r.rid: r for r in responses}
    decisions, unresolved, left_off = [], [], []

    for spec in args.assign:
        rid, _, name = spec.partition("=")
        if rid not in by_rid or name.strip() not in by_name:
            raise ns.SkillError("bad_decision", f"--assign {spec}: the response or the student "
                                                "('Last, First' as on the tab) was not found.")
    for rid in args.leave_out + args.use:
        if rid not in by_rid:
            raise ns.SkillError("bad_decision", f"There is no response {rid} in the export.")

    claims: dict[str, list[Response]] = defaultdict(list)
    assigned = {rid: name.strip() for rid, _, name in (s.partition("=") for s in args.assign)}
    for r in responses:
        if r.rid in args.leave_out:
            decisions.append(f"Left out response {r.rid} ({r.first} {r.last})")
            continue
        if r.rid in assigned:
            r.match_how = "instructor"
            claims[assigned[r.rid]].append(r)
            decisions.append(f"Response {r.rid} ({r.first} {r.last}) assigned to {assigned[r.rid]}")
            continue
        res = ns.resolve_student(r.first, r.last, present_pool, r.email)
        by_email = [s for s in present_pool if s.email and s.email == r.email]
        if res.confident and by_email and by_email[0].name != res.student.name:
            unresolved.append(unresolved_entry(r, "the name and the email point to different students",
                                               [res.student, by_email[0]]))
            continue
        if res.confident:
            r.match_how = res.how
            claims[res.student.name].append(r)
            continue
        res_absent = ns.resolve_student(r.first, r.last, absent_pool, r.email)
        if res_absent.confident:
            left_off.append(f"{res_absent.student.name} (absent; response {r.rid})")
            continue
        res_class = ns.resolve_student(r.first, r.last, students, r.email)
        if res_class.confident:
            left_off.append(f"{res_class.student.name} (on the class list but not in the current matches; "
                            f"response {r.rid})")
            continue
        reason = ("the last name matches but the first name doesn't" if res.how == "likely"
                  else "more than one student could match" if len(res.candidates) > 1
                  else "no student matches this name or email")
        unresolved.append(unresolved_entry(r, reason, res.candidates or ([res.student] if res.student else [])))

    for name, rs in claims.items():
        p = by_name[name]
        if len(rs) == 1:
            p.response = rs[0]
            continue
        rs = sorted(rs, key=lambda r: r.time)
        chosen = [r for r in rs if r.rid in args.use]
        if len(chosen) == 1:
            p.response = chosen[0]
            decisions.append(f"{name}: used response {chosen[0].rid} of {len(rs)} submissions")
        elif args.latest_duplicates:
            p.response = rs[-1]
            decisions.append(f"{name}: used the latest of {len(rs)} submissions")
        else:
            unresolved.append({"type": "duplicate", "student": name,
                               "submissions": [{"response": r.rid, "time": r.time, "typed_name": f"{r.first} {r.last}",
                                                **{k: a.typed for k, a in r.prices.items()}} for r in rs],
                               "reason": f"{name} submitted {len(rs)} times"})

    codes = SETTINGS_SIM["role_codes"]
    for p in present:
        if p.response and p.response.role_code and p.response.role_code != str(codes[p.role]):
            chose = next((role for role, c in codes.items() if str(c) == p.response.role_code), p.response.role_code)
            p.role_conflict = f"Chose {chose.title()} in the survey; assigned {p.role.title()}."
    return decisions, unresolved, left_off


def unresolved_entry(r: Response, reason: str, candidates) -> dict:
    return {"type": "unmatched", "response": r.rid, "typed_name": f"{r.first} {r.last}".strip(), "email": r.email,
            "time": r.time, "reason": reason, "suggestions": [c.name for c in candidates if c][:3]}


# ---------------------------------------------------------------- summary

def summarize(stage, groups, absent, removed, responses, decisions, unresolved, left_off, warnings):
    present = [p for g in groups.values() for p in g]
    cleaning = {"corrected": [], "unclear": [], "out_of_range": []}
    owner = {p.response.rid: p.name for p in present if p.response}
    for r in responses:
        who = owner.get(r.rid, f"{r.first} {r.last} (unmatched)")
        for q, a in r.prices.items():
            if a.flag:
                item = {"student": who, "question": q, "typed": a.typed}
                if a.flag == "corrected":
                    item["now"] = a.value
                cleaning[a.flag].append(item)
    matched_how = Counter(p.response.match_how for p in present if p.response)
    return {
        "matches_from": f"{stage} table",
        "matches": len(groups),
        "students": len(present),
        "responses_in_export": len(responses) + len(removed),
        "responses_removed": removed,
        "matched": dict(matched_how),
        "no_response": [p.name for p in present if not p.response
                        and not any(u.get("student") == p.name for u in unresolved)],
        "role_conflicts": [f"{p.name}: {p.role_conflict}" for p in present if p.role_conflict],
        "cleaning": cleaning,
        "left_off_sheet": left_off,
        "absent": [p.name for p in absent],
        "decisions_applied": decisions,
        "tab_warnings": warnings,
        "unresolved": unresolved,
        "ready_to_build": not unresolved,
    }


# ---------------------------------------------------------------- T8: build the sheet

def sheet_headers(roles, item_headers):
    left = ["MATCH", "FIRST", "LAST", "ROLE", "ACTUAL IO", "INITIAL", "TARGET", "RESERVATION", "BATNA", *item_headers]
    right = ["BATNA", "RESERVATION", "TARGET", "INITIAL", "ACTUAL IO", "FIRST", "LAST", "ROLE", *item_headers]
    return left + ["OUTCOME"] + right


def side_columns(left: bool, n_items: int) -> dict:
    """1-based column numbers for one side of the mirrored layout."""
    if left:
        cols = {"FIRST": 2, "LAST": 3, "ROLE": 4, "ACTUAL IO": 5, "INITIAL": 6, "TARGET": 7, "RESERVATION": 8, "BATNA": 9}
        cols["ITEMS"] = list(range(10, 10 + n_items))
        return cols
    start = 10 + n_items + 1  # one past OUTCOME
    cols = {"BATNA": start, "RESERVATION": start + 1, "TARGET": start + 2, "INITIAL": start + 3,
            "ACTUAL IO": start + 4, "FIRST": start + 5, "LAST": start + 6, "ROLE": start + 7}
    cols["ITEMS"] = list(range(start + 8, start + 8 + n_items))
    return cols


def fill(color):
    return PatternFill("solid", fgColor=color)


def write_sheet(wb, title, roles, groups, item_headers, codes):
    ws = wb.active
    ws.title = title
    headers = sheet_headers(roles, item_headers)
    ws.append(headers)
    n_items = len(item_headers)
    outcome_col = 10 + n_items
    sides = {roles[0]: side_columns(True, n_items), roles[1]: side_columns(False, n_items)}
    for c in ws[1]:
        c.font = Font(bold=True)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if c.value == "ACTUAL IO":
            c.fill = fill(YELLOW)
    expected = {}
    row = 2
    for index, (match, people) in enumerate(sorted(groups.items())):
        by_role = {role: [p for p in people if p.role == role] for role in roles}
        height = max(len(v) for v in by_role.values())
        for k in range(height):
            if index % 2 == 0:
                for col in range(1, len(headers) + 1):
                    ws.cell(row, col).fill = fill(BAND)
            if k == 0:
                ws.cell(row, 1, match)
                expected[(row, 1)] = match
            for role in roles:
                if k >= len(by_role[role]):
                    continue
                p, cols = by_role[role][k], sides[role]
                values = {"FIRST": p.first, "LAST": p.last, "ROLE": codes[role]}
                r = p.response
                if r:
                    values.update({q: r.prices[q].value for q in PRICE_ORDER})
                for key, value in values.items():
                    ws.cell(row, cols[key], value)
                    expected[(row, cols[key])] = value
                if r:
                    for col, value in zip(cols["ITEMS"], r.items):
                        ws.cell(row, col, value)
                        expected[(row, col)] = value
                    for q in PRICE_ORDER:
                        a = r.prices[q]
                        cell = ws.cell(row, cols[q])
                        if a.flag == "corrected":
                            cell.fill = fill(ORANGE)
                            cell.comment = Comment(f"Typed: {a.typed}\nRead as {a.value:,}.", AUTHOR)
                        elif a.flag == "unclear":
                            cell.fill = fill(LIGHT_RED)
                            cell.comment = Comment(f"Kept exactly as typed: {a.typed}", AUTHOR)
                        elif a.flag == "out_of_range":
                            cell.fill = fill(LIGHT_RED)
                            cell.comment = Comment(f"Typed: {a.typed}. Outside the usual range; check it.", AUTHOR)
                else:
                    ws.cell(row, cols["FIRST"]).comment = Comment("No survey response.", AUTHOR)
                if p.role_conflict:
                    ws.cell(row, cols["ROLE"]).fill = fill(LIGHT_RED)
                    ws.cell(row, cols["ROLE"]).comment = Comment(p.role_conflict, AUTHOR)
            row += 1
    legend = row + 1
    for offset, (color, text) in enumerate([
            (YELLOW, "Fill in during class"),
            (ORANGE, "Typo corrected by Claude; the original answer is in the cell comment"),
            (LIGHT_RED, "Unclear or unusual answer kept as typed, or a role chosen in the survey that differs from the assigned role")]):
        ws.cell(legend + offset, 1).fill = fill(color)
        ws.cell(legend + offset, 2, text)
    widths = {"A": 7, "B": 11, "C": 14, "D": 6, "E": 10, "F": 10, "G": 10, "H": 13, "I": 9}
    for letter, width in widths.items():
        ws.column_dimensions[letter].width = width
    ws.column_dimensions[ws.cell(1, outcome_col).column_letter].width = 12
    for col in range(outcome_col + 1, outcome_col + 9):
        ws.column_dimensions[ws.cell(1, col).column_letter].width = 11
    ws.row_dimensions[1].height = 60
    ws.freeze_panes = "B2"
    return expected


def write_roles_tab(wb, roles, groups):
    ws = wb.create_sheet("Roles")
    ws.append(["MATCH", *roles])
    for c in ws[1]:
        c.font = Font(bold=True)
    for match, people in sorted(groups.items()):
        by_role = {role: [p.name for p in people if p.role == role] for role in roles}
        for k in range(max(len(v) for v in by_role.values())):
            ws.append([match if k == 0 else None, *[(by_role[r][k] if k < len(by_role[r]) else None) for r in roles]])
    for letter in "BC":
        ws.column_dimensions[letter].width = 26


def write_raw_tab(wb, rows):
    ws = wb.create_sheet("Raw")
    for r in rows:
        ws.append(r)


def existing_in_class_entries(path: Path) -> list[str]:
    wb = ns.open_workbook(path)
    ws = wb.worksheets[0]
    cols = [c.column for c in ws[1] if ns.clean(c.value) in ("ACTUAL IO", "OUTCOME")]
    found = []
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if c.column in cols and ns.clean(c.value):
                found.append(c.coordinate)
    return found


def course_from_roster(roster: Path) -> str | None:
    m = re.match(r"^(.*?)\s+Roster\b", roster.stem)
    return m.group(1).strip() if m else None


def safe_title(text: str) -> str:
    return re.sub(r"[\[\]:*?/\\]", "", text)[:31] or "Bargaining Range"


# ---------------------------------------------------------------- commands

SETTINGS_SIM: dict = {}


def run(args, build: bool):
    started = time.time()
    if args.simulation not in SETTINGS:
        raise ns.SkillError("simulation_unknown", f"No settings for simulation '{args.simulation}'.",
                            {"known": sorted(SETTINGS)})
    sim = SETTINGS[args.simulation]
    SETTINGS_SIM.clear()
    SETTINGS_SIM.update(sim)
    roster, export = Path(args.roster).expanduser().resolve(), Path(args.csv).expanduser().resolve()
    raw_rows, item_headers, responses, removed = read_export(export, sim)
    students, stage, groups, absent, warnings = load_matches(roster, args.simulation, sim)
    decisions, unresolved, left_off = match_responses(responses, groups, absent, students, args)
    result = {"ok": True, **summarize(stage, groups, absent, removed, responses, decisions, unresolved, left_off,
                                      warnings)}
    if not build:
        ns.write_log(roster.parent, "T6-T7 Prepare bargaining sheet",
                     f"{export.name}: {result['students']} students, {len(responses)} responses kept, "
                     f"{len(unresolved)} unresolved, matches from the {stage} table.")
        ns.emit(result)
        return
    if unresolved:
        raise ns.SkillError("unresolved_responses", "Some survey responses need the instructor's decision first.",
                            {"unresolved": unresolved})
    course = args.course or course_from_roster(roster)
    if not course:
        raise ns.SkillError("course_unknown", "Could not tell the course and term from the roster file name. "
                                              "Pass --course, e.g. 'BUS 4489 F26'.")
    out = export.parent / f"{course} Week {args.week} - {sim['name']} Bargaining Range.xlsx"
    previous = None
    if out.exists():
        filled = existing_in_class_entries(out)
        if filled and not args.replace_in_class_entries:
            raise ns.SkillError("in_class_entries_present",
                                f"{out.name} already has entries in ACTUAL IO or OUTCOME ({', '.join(filled[:6])}"
                                f"{'…' if len(filled) > 6 else ''}). Replacing it would lose them.",
                                {"cells": filled})
        previous = ns.backup(out, "replaced")

    wb = Workbook()
    expected = write_sheet(wb, safe_title(export.stem), sim["roles"], groups, item_headers, sim["role_codes"])
    write_roles_tab(wb, sim["roles"], groups)
    write_raw_tab(wb, raw_rows)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / out.name
        wb.save(tmp_path)
        check = load_workbook(tmp_path).worksheets[0]
        mismatched = [check.cell(r, c).coordinate for (r, c), v in expected.items() if check.cell(r, c).value != v]
        if mismatched:
            raise ns.SkillError("readback_mismatch", "Some values did not save correctly; the sheet was not created.",
                                {"cells": mismatched})
        try:
            shutil.copyfile(tmp_path, out)
        except PermissionError:
            raise ns.SkillError("file_locked", f"{out.name} is open in Excel. Close it and try again.")
    result.update({"workbook": str(out), "previous_version_backup": str(previous) if previous else None,
                   "seconds": round(time.time() - started, 1)})
    warning = ns.write_log(roster.parent, "T8 Build bargaining sheet",
                           f"{out.name} from the {stage} table: {result['students']} students, "
                           f"{len(result['no_response'])} without a response, decisions: {decisions or 'none'}. "
                           f"Previous version: {previous.name if previous else 'none'}.")
    if warning:
        result["log_warning"] = warning
    ns.emit(result)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)
    for name in ("prepare", "build"):
        sp = sub.add_parser(name)
        sp.add_argument("--roster", required=True, help="The instructor's roster workbook (.xlsx)")
        sp.add_argument("--csv", required=True, help="The Qualtrics export (.csv)")
        sp.add_argument("--simulation", default="UC", help="Simulation code (default UC)")
        sp.add_argument("--assign", action="append", default=[], help="RESPONSE_ID=Last, First (her decision)")
        sp.add_argument("--use", action="append", default=[], help="Response ID to use for a duplicate")
        sp.add_argument("--leave-out", action="append", default=[], help="Response ID to leave off the sheet")
        sp.add_argument("--latest-duplicates", action="store_true", help="Use the latest of duplicate submissions")
        if name == "build":
            sp.add_argument("--week", required=True, help="Week of the term, for the file name")
            sp.add_argument("--course", help="Course and term for the file name (default: from the roster name)")
            sp.add_argument("--replace-in-class-entries", action="store_true",
                            help="Replace an existing sheet even though ACTUAL IO or OUTCOME has entries")
    args = p.parse_args()
    run(args, build=args.command == "build")


if __name__ == "__main__":
    ns.run_cli(main)
