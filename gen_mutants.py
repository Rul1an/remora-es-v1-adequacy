"""Generate the agreed fault classes for REMORA evidence-sufficiency-v1 checker.py @31c4060.
Classes (REMORA#629, agreed by the owner 5892078766):
 1 guard removal (every not_established guard; compound guards split per half)
 2 absence read as violation      3 refusal read as enforcement
 4 premise typing loosened (per ladder: every `is True`/`is not True` to truthiness)
 5 read-back comparison: canonical -> raw equality
 6 guard order swapped (adjacent guard blocks per ladder, plus the B01 precedence swap)
 7 status polarity flip in a terminal return     8 reason string changed, status kept
 G guidance table (row 2): attach condition dropped; each decisive_if text changed
 + positive control (_unknown returns ESTABLISHED), inert control (docstring edit)"""
import re, json, sys
src = open(sys.argv[1]).read()
M = []
def add(cls, label, a, r):
    M.append({"label": f"[{cls}] {label}", "anchor": a, "replacement": r})
funcs = {}
for name in ("admission_accounting", "tested_route_enforcement", "postcondition_observed"):
    s = src.index(f"def {name}("); e = src.index("\n\n\ndef ", s)
    funcs[name] = src[s:e]
# guard blocks: an `if` line followed by `return _unknown(claim, "reason", scope)`
G = re.compile(r'(?m)^( +)if (.+):\n\1    return _unknown\(claim, "([a-z_]+)", scope\)\n')
guards = {n: list(G.finditer(b)) for n, b in funcs.items()}
# 1 guard removal
for n, gs in guards.items():
    for g in gs:
        ind, cond, reason = g.group(1), g.group(2), g.group(3)
        block = g.group(0)
        parts = [p for p in re.split(r" or (?=o\.get|\")", cond)]
        if len(parts) == 1:
            add(1, f"{n}: guard '{reason}' removed", block, block.replace(f"if {cond}:", "if False:", 1))
        else:
            for i, p in enumerate(parts):
                rest = " or ".join(q for j, q in enumerate(parts) if j != i)
                add(1, f"{n}: guard '{reason}' half `{p}` removed", block, block.replace(f"if {cond}:", f"if {rest}:", 1))
add(1, "admission_accounting: admission_matches check removed",
    '        if o.get("admission_matches") is True:\n', '        if True:\n')
# 2 absence read as violation (skip mandatory, window, coverage at once)
a = '    if o.get("mandatory_admission") is not True:\n        return _unknown(claim, "admission_requirement_not_defined", scope)\n'
add(2, "absent admission returned as violated after the presence check", a,
    '    return _result(\n        claim,\n        EvidenceStatus.VIOLATED,\n        "mandatory_admission_absent_in_complete_bounded_history",\n        scope,\n    )\n' + a)
# 3 refusal read as enforcement (skip window, control, attribution at once)
a = '    if o.get("effect_window_complete") is not True:\n        return _unknown(claim, "no_effect_observation_not_complete", scope)\n'
add(3, "no observed effect credited as enforcement, skipping window/control/attribution", a,
    '    return _result(\n        claim,\n        EvidenceStatus.ESTABLISHED,\n        "named_route_refused_at_required_boundary_in_test_scope",\n        scope,\n    )\n' + a)
# 4 typing loosened per ladder
for n, b in funcs.items():
    nb = re.sub(r'(o\.get\("[a-z_]+"\)) is not True', r'not \1', b)
    nb = re.sub(r'(o\.get\("[a-z_]+"\)) is True', r'\1', nb)
    if nb != b: add(4, f"{n}: every `is True` check relaxed to truthiness", b, nb)
# 5 canonical -> raw equality
add(5, "postcondition: canonical comparison replaced by raw equality",
    'if canonical(o["expected_state"]) == canonical(o["observed_state"]):',
    'if o["expected_state"] == o["observed_state"]:')
# 6 guard order: adjacent top-level (indent 4) guard blocks, per ladder
for n, gs in guards.items():
    top = [g for g in gs if g.group(1) == "    "]
    for x, y in zip(top, top[1:]):
        if funcs[n][x.end():y.start()] == "":
            add(6, f"{n}: guards '{x.group(3)}' and '{y.group(3)}' swapped", x.group(0) + y.group(0), y.group(0) + x.group(0))
# 6 B01 precedence: attribution checked before the observed-effect violation
eff = '    if o.get("protected_effect_observed") is True:\n'
attr = '    if o.get("required_boundary_refusal_accepted") is not True:\n        return _unknown(claim, "refusal_not_attributed_to_required_boundary", scope)\n'
add(6, "tested_route_enforcement: attribution checked before the observed-effect violation (B01 precedence)", attr, "")
M[-1]["anchor"] = eff; M[-1]["replacement"] = attr + eff  # applied as insert; original attribution guard left in place (redundant later)
# 7 polarity flips in terminal returns
for m in re.finditer(r'EvidenceStatus\.(ESTABLISHED|VIOLATED),\n(\s+)"([a-z_]+)",', src):
    st, ind, reason = m.groups(); other = "VIOLATED" if st == "ESTABLISHED" else "ESTABLISHED"
    add(7, f"terminal '{reason}': {st} flipped to {other}", m.group(0), m.group(0).replace(st, other, 1))
# 8 reason strings mutated, status kept
for m in re.finditer(r'return _unknown\(claim, "([a-z_]+)", scope\)', src):
    add(8, f"reason '{m.group(1)}' changed", m.group(0), m.group(0).replace(m.group(1), m.group(1) + "_x", 1))
for m in re.finditer(r'(EvidenceStatus\.(?:ESTABLISHED|VIOLATED),\n\s+)"([a-z_]+)",', src):
    add(8, f"reason '{m.group(2)}' changed", m.group(0), m.group(0).replace(f'"{m.group(2)}"', f'"{m.group(2)}_x"', 1))
# G guidance table (row 2)
add("G", "_result: guidance never attached", 'if status is EvidenceStatus.NOT_ESTABLISHED and reason in _REASON_GUIDANCE:', 'if False:')
gs = src[src.index("_REASON_GUIDANCE"):src.index("\n}\n", src.index("_REASON_GUIDANCE"))]
for m in re.finditer(r'"([a-z_]+)": \(\n\s+\(.*?\),\n\s+("[^"]+"),', gs, re.S):
    add("G", f"guidance decisive_if for '{m.group(1)}' changed", m.group(2), m.group(2)[:-1] + ' (mutated)"')
# controls
C = [{"label": "CONTROL positive: _unknown returns ESTABLISHED", "control": True, "control_polarity": "positive",
      "anchor": "return _result(claim, EvidenceStatus.NOT_ESTABLISHED, reason, scope)",
      "replacement": "return _result(claim, EvidenceStatus.ESTABLISHED, reason, scope)"},
     {"label": "CONTROL inert: docstring edit", "control": True, "control_polarity": "inert",
      "anchor": '"""Does accepted evidence establish a covering admission for this execution?',
      "replacement": '"""Does accepted evidence establish a covering admission for this execution (inert)?'}]
bad = [x["label"] for x in M + C if src.count(x["anchor"]) != 1]
labels = [x["label"] for x in M]
print("mutants", len(M), "controls", len(C), "non-unique/absent anchors", bad, "dup labels", len(labels) - len(set(labels)))
from collections import Counter; print(Counter(l.split("]")[0][1:] for l in labels))
json.dump({"mutants": M, "controls": C}, open(sys.argv[2], "w"), indent=1)
