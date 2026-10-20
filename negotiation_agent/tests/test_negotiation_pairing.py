"""Tests for the negotiation-pairing skill, run against the fictional example files.

    python negotiation_agent/tests/test_negotiation_pairing.py

Works with pytest too. Each test copies the examples into a temporary folder, so the repo is never changed.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
SCRIPT = ROOT / "skills" / "negotiation-pairing" / "scripts" / "pairing.py"
sys.path.insert(0, str(SCRIPT.parent))
import nps_shared as ns  # noqa: E402

BEFORE = "BUS 4489 F26 Roster - before Used Car.xlsx"
DRAFTED = "BUS 4489 F26 Roster - Used Car drafted.xlsx"
AFTER = "BUS 4489 F26 Roster - after Used Car.xlsx"
EXPECTED = json.loads((EXAMPLES / "expected" / "used-car.json").read_text(encoding="utf-8"))
ABSENT = ["Adebayo", "Castellano, Rosa", "tzimmerm@example.edu"]  # three ways she might name them


def workspace() -> Path:
    tmp = Path(tempfile.mkdtemp())
    for f in (BEFORE, DRAFTED, AFTER):
        shutil.copy(EXAMPLES / f, tmp / f)
    return tmp


def run(folder: Path, *args) -> dict:
    out = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=folder, capture_output=True, text=True)
    assert out.stdout, out.stderr
    return json.loads(out.stdout)


def as_tables(groups: dict) -> dict:
    return {m: {r: [p.name for p in ps if p.role == r] for r in ("BUYER", "SELLER")} for m, ps in groups.items()}


def expected_tables(key: str) -> dict:
    return {m["match"]: {"BUYER": m["BUYER"], "SELLER": m["SELLER"]} for m in EXPECTED[key]}


def uc_tab(path: Path) -> ns.SimTab:
    return ns.read_sim_tab(load_workbook(path), "UC", ["BUYER", "SELLER"])


def all_values(path: Path, skip_tab: str | None = None) -> dict:
    wb = load_workbook(path)
    return {(ws.title, c.coordinate): c.value for ws in wb.worksheets if ws.title != skip_tab
            for row in ws.iter_rows() for c in row if c.value is not None}


def test_draft_preview_uses_her_alphabetical_method():
    result = run(workspace(), "draft", "--roster", BEFORE)
    assert result["ok"] and result["matches"] == 19 and not result["errors"]
    preview = {m["match"]: {"BUYER": m["BUYER"], "SELLER": m["SELLER"]} for m in result["draft"]}
    assert preview == expected_tables("draft")


def test_write_draft_fills_only_the_draft_table():
    folder = workspace()
    before = all_values(folder / BEFORE, skip_tab="UC")
    result = run(folder, "write-draft", "--roster", BEFORE)
    assert result["ok"], result
    assert Path(result["backup"]).exists()
    assert all_values(folder / BEFORE, skip_tab="UC") == before, "a tab other than UC changed"
    tab = uc_tab(folder / BEFORE)
    assert as_tables(tab.groups(tab.draft_members)) == expected_tables("draft")
    assert not tab.final_members
    # The draft table now matches the example "drafted" workbook cell for cell.
    ours, theirs = load_workbook(folder / BEFORE)["UC"], load_workbook(folder / DRAFTED)["UC"]
    for r in range(tab.draft_header, tab.draft_header + 23):
        assert [ours.cell(r, c).value for c in (1, 2, 3)] == [theirs.cell(r, c).value for c in (1, 2, 3)], r
    again = run(folder, "write-draft", "--roster", BEFORE)
    assert not again["ok"] and again["error"] == "draft_exists"
    assert run(folder, "write-draft", "--roster", BEFORE, "--replace")["ok"]


def test_known_absence_and_swap():
    folder = workspace()
    result = run(folder, "draft", "--roster", BEFORE, "--absent", "Owen Bennett",
                 "--swap", "Alvarez, Maya;Nakamura, Ren")
    assert result["ok"] and result["known_absent"] == ["Bennett, Owen"]
    names = [n for m in result["draft"] for r in ("BUYER", "SELLER") for n in m[r]]
    assert "Bennett, Owen" not in names and len(names) == 38 and result["matches"] == 19
    # Without Owen Bennett the halves shift: Maya Alvarez (a Buyer) and Ren Nakamura (now the first Seller)
    # trade places, keeping each other's role and match.
    role_of = {n: r for m in result["draft"] for r in ("BUYER", "SELLER") for n in m[r]}
    assert role_of["Alvarez, Maya"] == "SELLER" and role_of["Nakamura, Ren"] == "BUYER"
    unclear = run(folder, "draft", "--roster", BEFORE, "--absent", "Park")
    assert not unclear["ok"] and unclear["error"] == "absence_unclear"
    assert set(unclear["unclear"][0]["suggestions"]) == {"Park, Daniel", "Park, Danielle"}


def test_check_reports_her_excel_edits():
    folder = workspace()
    wb = load_workbook(folder / DRAFTED)
    ws = wb["UC"]
    tab = ns.read_sim_tab(wb, "UC", ["BUYER", "SELLER"])
    row = tab.draft_header + 2                      # match 2
    ws.cell(row, 3).value = ws.cell(row - 1, 3).value  # her typo: match 1's Seller copied into match 2
    wb.save(folder / DRAFTED)
    result = run(folder, "check", "--roster", DRAFTED)
    assert result["ok"]
    assert any("appears twice" in e for e in result["errors"])
    assert any("Nakamura, Ren" in w and "not in any match" in w for w in result["warnings"])


def test_bcc_lists_by_role():
    folder = workspace()
    result = run(folder, "bcc", "--roster", DRAFTED)
    assert result["ok"]
    assert result["lists"]["BUYER"]["count"] == 19 and result["lists"]["SELLER"]["count"] == 20
    assert "tzimmerm@example.edu" in result["lists"]["SELLER"]["bcc"]
    assert Path(result["saved_to"]).exists()


def test_absences_follow_her_rule_and_match_the_after_example():
    folder = workspace()
    args = ["--roster", DRAFTED, *sum((["--absent", a] for a in ABSENT), [])]
    proposal = run(folder, "absences", *args)
    assert proposal["ok"] and not proposal["errors"], proposal
    final = {m["match"]: {"BUYER": m["BUYER"], "SELLER": m["SELLER"]} for m in proposal["final"]}
    assert final == expected_tables("final")
    assert any("Mendes, Rafael joins match 2" in m for m in proposal["moves"])
    assert any("O'Neill, Siobhan joins match 4" in m for m in proposal["moves"])
    before = all_values(folder / DRAFTED, skip_tab="UC")
    written = run(folder, "write-final", *args)
    assert written["ok"], written
    assert all_values(folder / DRAFTED, skip_tab="UC") == before
    tab = uc_tab(folder / DRAFTED)
    assert as_tables(tab.groups(tab.final_members)) == expected_tables("final")
    assert {m.name: m.pair_id for m in tab.absent} == {n: "UC_0" for n in EXPECTED["absent_in_class"]}
    # The whole final table (names, emails, pair IDs) matches the example "after" workbook.
    ours, theirs = load_workbook(folder / DRAFTED)["UC"], load_workbook(folder / AFTER)["UC"]
    for r in range(1, tab.draft_header):
        assert [ours.cell(r, c).value for c in range(1, 11)] == [theirs.cell(r, c).value for c in range(1, 11)], r
    again = run(folder, "write-final", *args)
    assert not again["ok"] and again["error"] == "final_area_not_empty"


def test_stranded_student_who_doesnt_fit_needs_her_choice():
    folder = workspace()
    # Grace Mahoney is the only Buyer in match 19 (with two Sellers): both Sellers are stranded, and
    # match 18 can take only one of them.
    proposal = run(folder, "absences", "--roster", DRAFTED, "--absent", "Mahoney")
    assert proposal["ok"] and proposal["needs_placement"], proposal
    stuck = proposal["needs_placement"][0]["student"]
    placed = run(folder, "absences", "--roster", DRAFTED, "--absent", "Mahoney", "--place", f"{stuck}=17")
    assert placed["ok"] and not placed["errors"] and not placed["needs_placement"], placed


def drop_from_class_list(path: Path, name: str) -> None:
    wb = load_workbook(path)
    ws = wb["Att - Fall"]
    row = next(c.row for c in ws["B"] if c.value == name)
    ws.delete_rows(row)
    wb.save(path)


def test_student_who_dropped_after_the_draft_is_treated_as_absent():
    folder = workspace()
    drop_from_class_list(folder / DRAFTED, "Bennett, Owen")  # the only Buyer in match 3
    check = run(folder, "check", "--roster", DRAFTED)
    assert check["ok"] and not check["errors"], check
    assert any("Bennett, Owen" in w and "listed as absent" in w for w in check["warnings"])
    # Not named as absent: still listed as absent, and the partner moves under her rule.
    for named in ([], ["--absent", "Bennett"]):
        proposal = run(folder, "absences", "--roster", DRAFTED, *named)
        assert proposal["ok"] and not proposal["errors"], proposal
        assert proposal["absent"] == ["Bennett, Owen"] and proposal["dropped"] == ["Bennett, Owen"]
        assert any("Nguyen, Katherine joins match 2" in m and "no longer on the class list" in m
                   for m in proposal["moves"])
    written = run(folder, "write-final", "--roster", DRAFTED)
    assert written["ok"], written
    tab = uc_tab(folder / DRAFTED)
    assert [(m.name, m.role, m.pair_id) for m in tab.absent] == [("Bennett, Owen", "BUYER", "UC_0")]
    assert 3 not in tab.groups(tab.final_members)


def test_a_likely_name_is_still_asked_about_not_treated_as_dropped():
    folder = workspace()
    wb = load_workbook(folder / DRAFTED)
    ws = wb["Att - Fall"]
    next(c for c in ws["B"] if c.value == "Bennett, Owen").value = "Bennett, Oliver"  # same last name, new first
    wb.save(folder / DRAFTED)
    proposal = run(folder, "absences", "--roster", DRAFTED)
    assert proposal["ok"] and not proposal["dropped"]
    assert any("may be Bennett, Oliver" in e for e in proposal["errors"]), proposal["errors"]


def test_roles_are_locked_after_emails_go_out():
    folder = workspace()
    assert run(folder, "roles-sent", "--roster", DRAFTED)["ok"]
    result = run(folder, "write-draft", "--roster", DRAFTED, "--replace", "--swap", "Alvarez, Maya;Nakamura, Ren")
    assert not result["ok"] and result["error"] == "roles_locked"
    assert set(result["role_changes"]) == {"Alvarez, Maya", "Nakamura, Ren"}


def test_repeat_partners_are_warned_for_the_next_simulation():
    folder = workspace()
    wb = load_workbook(folder / AFTER)
    ws = wb["SL"]
    tab = ns.read_sim_tab(wb, "SL", ["SUPERVISOR", "SUBORDINATE"])
    r = tab.draft_header + 1
    ws.cell(r, 2).value, ws.cell(r, 3).value = "Alvarez, Maya", "Nakamura, Ren"      # partners in UC_2
    ws.cell(r + 1, 2).value, ws.cell(r + 1, 3).value = "Bennett, Owen", "Park, Daniel"  # never partners
    wb.save(folder / AFTER)
    result = run(folder, "check", "--roster", AFTER, "--simulation", "SL")
    assert result["ok"]
    repeats = [w for w in result["warnings"] if w.startswith("Repeat partners")]
    assert len(repeats) == 1 and "UC_2" in repeats[0] and "Alvarez, Maya" in repeats[0]
    refused = run(folder, "draft", "--roster", AFTER, "--simulation", "SL")
    assert not refused["ok"] and refused["error"] == "draft_method_unknown"


if __name__ == "__main__":
    failures = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            try:
                fn()
                print(f"PASS {name}")
            except AssertionError as exc:
                failures += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)
