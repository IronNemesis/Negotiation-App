"""Negotiation pairing: draft matches, role BCC lists, and the in-class absence update.

Commands (task IDs refer to negotiation_agent/agent/task-specs):
  snapshot     T1       what the workbook holds for this simulation; writes nothing
  draft        T2 + T3  preview the draft with her alphabetical method, with checks; writes nothing
  write-draft  T4       write the approved draft into the simulation tab's draft table
  check        T3       re-check the draft table as it stands (after she edits it in Excel)
  bcc          T5       one BCC email list per role, in the output and in a text file
  roles-sent   H3       record that role emails went out (roles are locked from then on)
  absences     T9       propose the final matches for the absent students; writes nothing
  write-final  T9       write the confirmed final matches into the final table
  log                   record one of her decisions in the log

Every command prints one JSON object. "ok": false comes with an "error" code and a plain-language "message".
Names are given as on her class list ("Last, First"); absences may be given however she said them.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nps_shared as ns  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

SETTINGS = json.loads((HERE / "simulations.json").read_text(encoding="utf-8"))
MAX_GROUP = 3


# ---------------------------------------------------------------- loading

@dataclass
class Person:
    name: str                 # the name to write: class-list name when linked, otherwise as on the tab
    tab_name: str             # as on the simulation tab ("" for drafts computed from the class list)
    role: str
    student: ns.Student | None
    link: str                 # "exact", "email", "nickname", "confirmed", "likely", "none"

    @property
    def key(self) -> str:
        return self.student.key if self.student else ns.class_name_key(self.name)

    @property
    def email(self) -> str:
        return self.student.email if self.student else ""


class Context:
    def __init__(self, args):
        self.roster = Path(args.roster).expanduser().resolve()
        self.code = args.simulation
        if self.code not in SETTINGS:
            raise ns.SkillError("simulation_unknown", f"No settings for simulation '{self.code}'.",
                                {"known": sorted(SETTINGS)})
        self.sim = SETTINGS[self.code]
        self.roles = self.sim["roles"]
        self.wb = ns.open_workbook(self.roster)
        self.class_tab, self.students, self.class_warnings = ns.read_class_list(self.wb)
        self.tab = ns.read_sim_tab(self.wb, self.code, self.roles)
        self.history, self.unlinked_history = ns.read_pair_history(self.wb, exclude_code=self.code).linked_to_class(
            self.students)
        self.same_person = {}
        for spec in getattr(args, "same_person", []) or []:
            tab_name, _, class_name = spec.partition("=")
            student = next((s for s in self.students if s.name == class_name.strip()), None)
            if not student:
                raise ns.SkillError("bad_option", f"--same-person {spec}: '{class_name.strip()}' is not on the class list.")
            self.same_person[ns.class_name_key(tab_name)] = student

    def by_name(self, name: str) -> ns.Student:
        res = ns.resolve_class_name(name, self.students)
        if res.confident:
            return res.student
        raise ns.SkillError("unknown_student", f"'{name}' doesn't match exactly one student on the class list.",
                            {"suggestions": [s.name for s in res.candidates] or ([res.student.name] if res.student else [])})

    def person_from_tab(self, m: ns.Member) -> Person:
        if ns.class_name_key(m.name) in self.same_person:
            s = self.same_person[ns.class_name_key(m.name)]
            return Person(s.name, m.name, m.role, s, "confirmed")
        res = ns.resolve_class_name(m.name, self.students, m.email)
        if res.confident:
            return Person(res.student.name, m.name, m.role, res.student, res.how)
        return Person(m.name, m.name, m.role, res.student if res.how == "likely" else None, res.how)

    def tab_groups(self, members: list[ns.Member]) -> dict[int, list[Person]]:
        return {match: [self.person_from_tab(m) for m in ms] for match, ms in self.tab.groups(members).items()}

    def log(self, step: str, details: str) -> str | None:
        return ns.write_log(self.roster.parent, f"{step} ({self.code})", details)


def table_preview(groups: dict[int, list[Person]], roles: list[str]) -> list[dict]:
    return [{"match": m, **{r: [p.name for p in people if p.role == r] for r in roles}}
            for m, people in sorted(groups.items())]


# ---------------------------------------------------------------- T3: checks

def check_groups(ctx: Context, groups: dict[int, list[Person]], absent: list[Person], stage: str,
                 draft_roles: dict[str, str] | None = None) -> dict:
    errors, warnings = [], []
    seen: dict[str, int] = {}
    absent_keys = {p.key for p in absent}
    for match, people in sorted(groups.items()):
        roles = [p.role for p in people]
        for role in ctx.roles:
            if role not in roles:
                errors.append(f"Match {match} has no {role.title()}.")
        if len(people) > MAX_GROUP:
            errors.append(f"Match {match} has {len(people)} students; the most is {MAX_GROUP}.")
        for p in people:
            if p.key in seen:
                errors.append(f"{p.name} appears twice: matches {seen[p.key]} and {match}.")
            seen[p.key] = match
            if p.key in absent_keys:
                errors.append(f"{p.name} is marked absent but is in match {match}.")
            if p.link == "likely":
                errors.append(f"'{p.tab_name}' on the {ctx.code} tab isn't on the class list; it may be "
                              f"{p.student.name}. Confirm it's the same person.")
            elif p.link == "none":
                errors.append(f"'{p.tab_name or p.name}' is in match {match} but isn't on the class list "
                              "(dropped the class, or a different spelling?).")
            if draft_roles is not None and p.key in draft_roles and draft_roles[p.key] != p.role:
                errors.append(f"{p.name} was a {draft_roles[p.key].title()} in the draft and can't become a "
                              f"{p.role.title()}: role packets have already gone out.")
        for a, b in combinations(people, 2):
            shared = ctx.history.shared_ids(a.key, b.key)
            if shared:
                warnings.append(f"Repeat partners in match {match}: {a.name} and {b.name} were already together "
                                f"({', '.join(shared)}).")
    for s in ctx.students:
        if s.key not in seen and s.key not in absent_keys:
            message = f"{s.name} is on the class list but not in any match."
            (errors if stage == "final" else warnings).append(
                message + (" Report them as absent if they aren't in class." if stage == "final"
                           else " Were they already known to be absent?"))
    return {"errors": errors, "warnings": warnings,
            "summary": f"{len(errors)} errors, {len(warnings)} warnings"}


# ---------------------------------------------------------------- T2: drafting

def match_entry(entry: str, people: list[Person]) -> tuple[Person | None, list[Person], str]:
    """Match how she named an absent student to one person: email, full name, then a unique last or first name."""
    e = ns.normalize(entry.replace(",", " ")).replace(",", "")
    words = e.split()
    rules = [
        ("email", lambda p: p.email and p.email == entry.strip().lower()),
        ("full name", lambda p: sorted(ns.normalize(p.name.replace(",", " ")).split()) == sorted(words)),
        ("last name", lambda p: ns.normalize(ns.split_class_name(p.name)[1]) == e),
        ("first name", lambda p: ns.normalize(ns.split_class_name(p.name)[0]) == e),
    ]
    for rule, test in rules:
        hits = [p for p in people if test(p)]
        if len(hits) == 1:
            return hits[0], [], rule
        if len(hits) > 1:
            return None, hits, rule
    loose = [p for p in people if any(w in ns.normalize(p.name.replace(",", " ")).split() for w in words)]
    return None, loose[:4], "none"


def resolve_entries(entries: list[str], people: list[Person]) -> tuple[list[Person], list[dict]]:
    found, problems = [], []
    for entry in entries:
        if not entry.strip():
            continue
        person, candidates, rule = match_entry(entry, people)
        if person:
            found.append(person)
        else:
            problems.append({"entry": entry, "reason": "more than one student fits" if candidates and rule != "none"
                             else "no student fits", "suggestions": [p.name for p in candidates]})
    return found, problems


def compute_draft(ctx: Context, args) -> tuple[dict[int, list[Person]], list[Person]]:
    if ctx.sim.get("draft_method") != "alphabetical-halves":
        raise ns.SkillError("draft_method_unknown", f"Drafting {ctx.sim['name']} isn't supported yet; only "
                                                    "simulations with a confirmed drafting method can be drafted.")
    everyone = [Person(s.name, "", "", s, "exact") for s in ctx.students]
    absent, problems = resolve_entries(args.absent, everyone)
    if problems:
        raise ns.SkillError("absence_unclear", "Some absent students couldn't be matched to one student.",
                            {"unclear": problems})
    absent_keys = {p.key for p in absent}
    ordered = sorted((s for s in ctx.students if s.key not in absent_keys), key=lambda s: s.key)
    if len(ordered) < 2:
        raise ns.SkillError("too_few_students", "Fewer than two students are left to match.")
    half = len(ordered) // 2
    first_role, second_role = ctx.roles
    groups = {i + 1: [Person(a.name, "", first_role, a, "exact"), Person(b.name, "", second_role, b, "exact")]
              for i, (a, b) in enumerate(zip(ordered[:half], ordered[half:]))}
    if len(ordered) % 2:
        extra = ordered[-1]
        groups[half].append(Person(extra.name, "", second_role, extra, "exact"))
    for spec in args.swap:
        names = [n.strip() for n in spec.split(";")]
        if len(names) != 2:
            raise ns.SkillError("bad_option", f"--swap '{spec}' needs two names separated by ';'.")
        a, b = (ctx.by_name(n) for n in names)
        pa = next((m, p) for m, ps in groups.items() for p in ps if p.key == a.key)
        pb = next((m, p) for m, ps in groups.items() for p in ps if p.key == b.key)
        (ma, person_a), (mb, person_b) = pa, pb
        ia, ib = groups[ma].index(person_a), groups[mb].index(person_b)
        groups[ma][ia] = Person(b.name, "", person_a.role, b, "exact")
        groups[mb][ib] = Person(a.name, "", person_b.role, a, "exact")
    return groups, [Person(p.name, "", "", p.student, "exact") for p in absent]


def draft_rows(groups: dict[int, list[Person]], roles: list[str]) -> list[tuple[int | None, dict[str, Person | None]]]:
    rows = []
    for match, people in sorted(groups.items()):
        by_role = {r: [p for p in people if p.role == r] for r in roles}
        for k in range(max(len(v) for v in by_role.values())):
            rows.append((match if k == 0 else None, {r: (by_role[r][k] if k < len(by_role[r]) else None) for r in roles}))
    return rows


# ---------------------------------------------------------------- writing safely

def snapshot_values(wb) -> dict:
    return {(ws.title, c.coordinate): c.value for ws in wb.worksheets for row in ws.iter_rows() for c in row
            if c.value is not None}


def save_and_verify(ctx: Context, written: dict[tuple[str, str], object], label: str) -> Path:
    """Back up, save, and prove that only the intended cells changed."""
    before = snapshot_values(load_workbook(ctx.roster))
    backup = ns.backup(ctx.roster, label)
    ns.save_workbook(ctx.wb, ctx.roster)
    after = snapshot_values(load_workbook(ctx.roster))
    unexpected = [f"'{t}'!{c}" for (t, c) in set(before) | set(after)
                  if (t, c) not in written and before.get((t, c)) != after.get((t, c))]
    wrong = [f"'{t}'!{c}" for (t, c), v in written.items() if after.get((t, c)) != (v if v != "" else None)]
    if unexpected or wrong:
        import shutil
        shutil.copy2(backup, ctx.roster)
        raise ns.SkillError("write_verification_failed", "The workbook didn't save as intended, so the backup was "
                                                         "restored and nothing changed.",
                            {"unexpected_changes": unexpected[:20], "wrong_cells": wrong[:20]})
    return backup


def set_tracked(ws, written: dict, row: int, col: int, value) -> None:
    ns.set_cell(ws, row, col, value)
    written[(ws.title, ws.cell(row, col).coordinate)] = value


def roles_locked(ctx: Context) -> bool:
    log = ctx.roster.parent / ns.LOG_NAME
    if not log.exists():
        return False
    ws = load_workbook(log).active
    return any(ns.clean(r[1]) == f"H3 Role emails sent ({ctx.code})" for r in ws.iter_rows(min_row=2, values_only=True))


# ---------------------------------------------------------------- commands

def cmd_snapshot(args):
    ctx = Context(args)
    tab = ctx.tab
    ns.emit({
        "ok": True, "workbook": str(ctx.roster), "simulation": ctx.code, "class_tab": ctx.class_tab,
        "students": len(ctx.students), "missing_email": [s.name for s in ctx.students if not s.email],
        "class_list_warnings": ctx.class_warnings,
        "draft_table": {"matches": len(tab.groups(tab.draft_members)) if tab.draft_members else 0,
                        "rows_available": len(tab.draft_prefilled) + len({m.row for m in tab.draft_members})},
        "final_table": {"matches": len(tab.groups(tab.final_members)) if tab.final_members else 0,
                        "absent": [m.name for m in tab.absent],
                        "rows_available": tab.draft_header - tab.final_header - 1},
        "roles_locked": roles_locked(ctx),
        "earlier_simulations_found": sorted({i.split("_")[0] for ids in ctx.history.ids_by_student.values() for i in ids}),
        "history_names_not_linked": ctx.unlinked_history,
        "can_draft": ctx.sim.get("draft_method") == "alphabetical-halves",
    })


def cmd_draft(args, write: bool = False):
    ctx = Context(args)
    groups, absent = compute_draft(ctx, args)
    checks = check_groups(ctx, groups, absent, "draft")
    result = {"ok": True, "simulation": ctx.code, "matches": len(groups), "students": sum(map(len, groups.values())),
              "known_absent": [p.name for p in absent], "draft": table_preview(groups, ctx.roles),
              "swaps_applied": args.swap, **checks}
    if not write:
        ctx.log("T2 Draft preview", f"{len(groups)} matches; absent: {[p.name for p in absent] or 'none'}; "
                                    f"swaps: {args.swap or 'none'}; {checks['summary']}.")
        ns.emit(result)
        return
    if checks["errors"]:
        raise ns.SkillError("draft_has_errors", "The draft has errors, so it wasn't written.", checks)
    if checks["warnings"] and not args.accept_warnings:
        raise ns.SkillError("warnings_not_accepted", "The draft has warnings. Confirm them with the instructor, then "
                                                     "run write-draft again with --accept-warnings.", checks)
    tab, ws = ctx.tab, ctx.wb[ctx.code]
    if tab.draft_members:
        if not args.replace:
            raise ns.SkillError("draft_exists", f"The {ctx.code} draft table already has names. Ask the instructor "
                                                "before replacing it, then use --replace.",
                                {"current_draft": table_preview(ctx.tab_groups(tab.draft_members), ctx.roles)})
        old_roles = {ctx.person_from_tab(m).key: m.role for m in tab.draft_members}
        changed = [p.name for ps in groups.values() for p in ps if p.key in old_roles and old_roles[p.key] != p.role]
        if changed and roles_locked(ctx) and not args.confirm_role_change:
            raise ns.SkillError("roles_locked", "Role emails have already gone out, and this draft changes roles for: "
                                                f"{', '.join(changed)}. Confirm with the instructor that she will "
                                                "re-send those packets, then add --confirm-role-change.",
                                {"role_changes": changed})
    rows = draft_rows(groups, ctx.roles)
    region = sorted(set(tab.draft_prefilled) | {m.row for m in tab.draft_members})
    first_row = tab.draft_header + 1
    if not region or len(rows) > len(region) or region != list(range(first_row, first_row + len(region))):
        raise ns.SkillError("tab_too_short", f"The {ctx.code} draft table needs {len(rows)} rows, but the prepared "
                                             f"tab has {len(region)} numbered rows under MATCH. Add match numbers to "
                                             "the tab and try again.")
    written: dict = {}
    for i, row in enumerate(region):
        if i < len(rows):
            match, by_role = rows[i]
            set_tracked(ws, written, row, tab.draft_match_column, match)
            for role, col in tab.draft_columns.items():
                set_tracked(ws, written, row, col, by_role[role].name if by_role[role] else None)
        else:  # unused prepared rows: clear names and the leftover match number, as on her own tabs
            for col in (tab.draft_match_column, *tab.draft_columns.values()):
                if ws.cell(row, col).value is not None:
                    set_tracked(ws, written, row, col, None)
    backup = save_and_verify(ctx, written, f"before {ctx.code} draft")
    result.update({"written_to": f"'{ctx.code}' draft table, rows {region[0]}-{region[len(rows) - 1]}",
                   "backup": str(backup)})
    warning = ctx.log("T4 Write draft", f"Draft written: {len(groups)} matches, rows {region[0]}-{region[len(rows) - 1]}. "
                                        f"Accepted warnings: {checks['warnings'] or 'none'}. Backup: {backup.name}.")
    if warning:
        result["log_warning"] = warning
    ns.emit(result)


def cmd_check(args):
    ctx = Context(args)
    tab = ctx.tab
    if args.stage == "final":
        if not tab.final_members:
            raise ns.SkillError("no_final_table", f"The {ctx.code} final table is empty.")
        groups = ctx.tab_groups(tab.final_members)
        absent = [ctx.person_from_tab(m) for m in tab.absent]
        draft_roles = {ctx.person_from_tab(m).key: m.role for m in tab.draft_members} if tab.draft_members else None
    else:
        if not tab.draft_members:
            raise ns.SkillError("no_draft_table", f"The {ctx.code} draft table is empty.")
        groups, absent, draft_roles = ctx.tab_groups(tab.draft_members), [], None
    checks = check_groups(ctx, groups, absent, args.stage, draft_roles)
    ctx.log("T3 Check", f"{args.stage} table: {checks['summary']}.")
    ns.emit({"ok": True, "simulation": ctx.code, "stage": args.stage, "matches": len(groups),
             "table": table_preview(groups, ctx.roles), **checks})


def cmd_bcc(args):
    ctx = Context(args)
    tab = ctx.tab
    members = tab.final_members or tab.draft_members
    if not members:
        raise ns.SkillError("no_draft_table", f"The {ctx.code} draft table is empty. Write the draft first.")
    groups = ctx.tab_groups(members)
    lists, missing = {}, []
    for role in ctx.roles:
        people = [p for ps in groups.values() for p in ps if p.role == role]
        emails = [p.email for p in people if p.email]
        missing += [p.name for p in people if not p.email]
        lists[role] = {"count": len(emails), "bcc": "; ".join(emails)}
    path = ctx.roster.parent / f"{ctx.code} role emails {date.today().isoformat()}.txt"
    text = "\n\n".join(f"{role} ({v['count']} students):\n{v['bcc']}" for role, v in lists.items())
    try:
        path.write_text(text + "\n", encoding="utf-8")
        saved = str(path)
    except PermissionError:
        saved = None
    counts = ", ".join(f"{role}: {v['count']}" for role, v in lists.items())
    ctx.log("T5 Role BCC lists", f"{counts}; missing email: {missing or 'none'}.")
    ns.emit({"ok": True, "simulation": ctx.code, "lists": lists, "missing_email": missing, "saved_to": saved})


def cmd_roles_sent(args):
    ctx = Context(args)
    ctx.log("H3 Role emails sent", "The instructor confirmed the role emails were sent. Roles are locked.")
    ns.emit({"ok": True, "simulation": ctx.code, "roles_locked": True})


def propose_final(ctx: Context, args):
    tab = ctx.tab
    if not tab.draft_members:
        raise ns.SkillError("no_draft_table", f"The {ctx.code} draft table is empty, so there is nothing to update.")
    groups = ctx.tab_groups(tab.draft_members)
    draft_roles = {p.key: p.role for ps in groups.values() for p in ps}
    everyone = [p for ps in groups.values() for p in ps]
    # Students on the class list but not in the draft were usually already known to be absent when drafting.
    off_draft = [Person(s.name, "", "", s, "exact") for s in ctx.students if s.key not in draft_roles]
    absent, extra_absent, problems = [], [], []
    for entry in args.absent:
        if not entry.strip():
            continue
        found, candidates, rule = match_entry(entry, everyone)
        if found:
            absent.append(found)
            continue
        if not candidates or rule == "none":
            other, _, _ = match_entry(entry, off_draft)
            if other:
                extra_absent.append(other)
                continue
        problems.append({"entry": entry, "reason": "more than one student fits" if candidates and rule != "none"
                         else "no student fits", "suggestions": [p.name for p in candidates]})
    if problems:
        raise ns.SkillError("absence_unclear", "Some absent students couldn't be matched to one student in the draft.",
                            {"unclear": problems})
    absent_keys = {p.key for p in absent}
    remaining = {m: [p for p in ps if p.key not in absent_keys] for m, ps in groups.items()}
    complete = {m for m, ps in remaining.items() if all(any(p.role == r for p in ps) for r in ctx.roles)}
    placements = {}
    for spec in args.place:
        name, _, match = spec.rpartition("=")
        student = ctx.by_name(name)
        if not match.strip().isdigit() or int(match) not in complete:
            raise ns.SkillError("bad_option", f"--place {spec}: match {match} isn't a match still in use.")
        placements[student.key] = int(match)
    final = {m: list(remaining[m]) for m in sorted(complete)}
    moves, needs_placement = [], []
    for m in sorted(set(remaining) - complete):
        stranded = remaining[m]
        if not stranded:
            continue
        lost = ", ".join(p.name for p in groups[m] if p.key in absent_keys)
        for p in stranded:
            if p.key in placements:
                target, how = placements[p.key], "placed by the instructor"
            else:
                earlier = [x for x in final if x < m]
                later = [x for x in final if x > m]
                target = earlier[-1] if earlier else (later[0] if later else None)
                how = "the match just before" if earlier else "the next match (there is no earlier one)"
                if target is None:
                    raise ns.SkillError("no_match_left", "No complete match is left to join.")
                too_big = len(final[target]) + 1 > MAX_GROUP
                repeat = any(ctx.history.shared_ids(p.key, q.key) for q in final[target])
                if too_big or repeat:
                    needs_placement.append({"student": p.name, "from_match": m, "suggested_match": target,
                                            "reason": "that match would have more than three students" if too_big
                                            else "that match would repeat a partner from an earlier simulation"})
                    continue
            final[target].append(p)
            moves.append(f"{p.name} joins match {target} as a second {p.role.title()} because {lost} "
                         f"(match {m}) is absent ({how}).")
    all_absent = absent + extra_absent
    checks = check_groups(ctx, final, all_absent, "final", draft_roles)
    if needs_placement:
        checks["errors"].append("Some stranded students need the instructor to choose a match.")
    return final, all_absent, moves, needs_placement, checks, draft_roles


def cmd_absences(args, write: bool = False):
    ctx = Context(args)
    final, absent, moves, needs_placement, checks, _ = propose_final(ctx, args)
    result = {"ok": True, "simulation": ctx.code, "absent": [p.name for p in absent], "moves": moves,
              "needs_placement": needs_placement, "final": table_preview(final, ctx.roles), "matches": len(final),
              **checks}
    if not write:
        ctx.log("T9 Absence proposal", f"Absent: {[p.name for p in absent] or 'none'}; moves: {moves or 'none'}; "
                                       f"{checks['summary']}.")
        ns.emit(result)
        return
    if checks["errors"]:
        raise ns.SkillError("final_has_errors", "The final matches have errors, so they weren't written.", result)
    if checks["warnings"] and not args.accept_warnings:
        raise ns.SkillError("warnings_not_accepted", "The final matches have warnings. Confirm them with the "
                                                     "instructor, then add --accept-warnings.", checks)
    tab, ws = ctx.tab, ctx.wb[ctx.code]
    region = list(range(tab.final_header + 1, tab.draft_header))
    role_cols = {rc.role: rc for rc in tab.final_columns}
    table_cols = {tab.match_column} | {c for rc in tab.final_columns for c in
                                       (rc.name, rc.email, rc.current_id, *rc.prior_ids.values())}
    # Columns beside the table that she fills herself (Gender, Intervention): never written, but checked.
    other_cols = [c for c in range(1, max(table_cols) + 3) if c not in table_cols]
    occupied = [ws.cell(r, c).coordinate for r in region for c in table_cols
                if ws.cell(r, c).value is not None and not (c == tab.match_column and isinstance(ws.cell(r, c).value, (int, float)))]
    other_filled = [ws.cell(r, c).coordinate for r in region for c in other_cols if ws.cell(r, c).value is not None]
    if (occupied or other_filled) and not args.replace:
        raise ns.SkillError("final_area_not_empty", f"The {ctx.code} final table already has entries. Ask the "
                                                    "instructor before replacing it, then use --replace.",
                            {"cells": (occupied + other_filled)[:20]})
    rows = draft_rows(final, ctx.roles)
    needed = len(rows) + (1 + len(absent) if absent else 0)
    if needed > len(region) - 1:
        raise ns.SkillError("tab_too_short", f"The {ctx.code} final table needs {needed} rows above the draft table "
                                             f"but only {len(region) - 1} are free.")
    written: dict = {}
    for row in region:
        for col in table_cols:
            if ws.cell(row, col).value is not None:
                set_tracked(ws, written, row, col, None)

    def write_person(row, p: Person, role: str, pair_id: str):
        rc = role_cols[role]
        set_tracked(ws, written, row, rc.name, p.name)
        set_tracked(ws, written, row, rc.email, p.email or (p.student.email if p.student else None))
        set_tracked(ws, written, row, rc.current_id, pair_id)
        for code, col in rc.prior_ids.items():
            ids = [i for i in ctx.history.ids_by_student.get(p.key, set()) if i.startswith(code + "_")]
            missed = code in ctx.history.absences_by_student.get(p.key, set())
            set_tracked(ws, written, row, col, ids[0] if ids else (f"{code}_0" if missed else None))

    r = region[0]
    current = None
    for match, by_role in rows:
        current = match if match is not None else current
        set_tracked(ws, written, r, tab.match_column, match)
        for role, p in by_role.items():
            if p:
                write_person(r, p, role, f"{ctx.code}_{current}")
        r += 1
    r += 1
    first_role = ctx.roles[0]
    for p in absent:  # under their own role's columns; students absent from the draft go under the first role
        write_person(r, p, p.role if p.role in role_cols else first_role, f"{ctx.code}_0")
        r += 1
    backup = save_and_verify(ctx, written, f"before {ctx.code} final")
    result.update({"written_to": f"'{ctx.code}' final table, rows {region[0]}-{r - 1}", "backup": str(backup)})
    if other_filled:
        result["note"] = ("Gender, Intervention, or other columns next to the final table had entries; they were left "
                          "untouched, so check they still line up with the right students.")
    warning = ctx.log("T9 Write final", f"Final matches written: {len(final)} matches; absent: "
                                        f"{[p.name for p in absent] or 'none'}; moves: {moves or 'none'}. "
                                        f"Backup: {backup.name}.")
    if warning:
        result["log_warning"] = warning
    ns.emit(result)


def cmd_log(args):
    ctx = Context(args)
    warning = ctx.log(args.step, args.details)
    ns.emit({"ok": True, **({"log_warning": warning} if warning else {})})


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    def add(name):
        sp = sub.add_parser(name)
        sp.add_argument("--roster", required=True, help="The instructor's roster workbook (.xlsx)")
        sp.add_argument("--simulation", default="UC", help="Simulation code (default UC)")
        sp.add_argument("--same-person", action="append", default=[],
                        help="'Tab Name=Class Name' when she confirms a tab name is a class-list student")
        return sp

    add("snapshot").set_defaults(func=cmd_snapshot)
    for name, write in (("draft", False), ("write-draft", True)):
        sp = add(name)
        sp.add_argument("--absent", action="append", default=[], help="A student already known to be absent")
        sp.add_argument("--swap", action="append", default=[], help="'Last, First;Last, First' to swap two students")
        if write:
            sp.add_argument("--accept-warnings", action="store_true")
            sp.add_argument("--replace", action="store_true", help="Replace a draft table that already has names")
            sp.add_argument("--confirm-role-change", action="store_true")
        sp.set_defaults(func=lambda a, w=write: cmd_draft(a, w))
    sp = add("check")
    sp.add_argument("--stage", choices=["draft", "final"], default="draft")
    sp.set_defaults(func=cmd_check)
    add("bcc").set_defaults(func=cmd_bcc)
    add("roles-sent").set_defaults(func=cmd_roles_sent)
    for name, write in (("absences", False), ("write-final", True)):
        sp = add(name)
        sp.add_argument("--absent", action="append", default=[], help="An absent student, as she named them")
        sp.add_argument("--place", action="append", default=[], help="'Last, First=MATCH' to place a stranded student")
        if write:
            sp.add_argument("--accept-warnings", action="store_true")
            sp.add_argument("--replace", action="store_true", help="Replace a final table that already has entries")
        sp.set_defaults(func=lambda a, w=write: cmd_absences(a, w))
    sp = add("log")
    sp.add_argument("--step", required=True)
    sp.add_argument("--details", required=True)
    sp.set_defaults(func=cmd_log)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    ns.run_cli(main)
