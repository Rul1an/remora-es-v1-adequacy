# corpus-adequacy adapter for REMORA evidence-sufficiency-v1 (not part of the suite).
# Mirrors run_evidence_sufficiency.build_record() for ONE case: same loader (imported), same
# assess() call and scope. Mode "verdict" prints status+reason (row 1); mode "guidance" prints
# missing_evidence+decisive_if (row 2). Nothing else is interpreted.
import json, os, sys
from copy import deepcopy
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from run_evidence_sufficiency import load_json
from checker import assess
from pathlib import Path
mode, vec = sys.argv[1], sys.argv[2]
cid = json.load(open(vec))["id"]
case = {c["id"]: c for c in load_json(Path(HERE) / "cases.json")["cases"]}[cid]
scope = {"kind": "synthetic_fixture", "suite": "evidence-sufficiency-v1", "bounded": True, "case": cid}
v = assess(case["claim"], deepcopy(case["observations"]), scope=scope).as_dict()
if mode == "verdict":
    print(json.dumps({"status": v["status"], "reason": v["reason"]}))
else:
    print(json.dumps({"missing_evidence": "|".join(v["missing_evidence"]), "decisive_if": v.get("decisive_if") or ""}))
