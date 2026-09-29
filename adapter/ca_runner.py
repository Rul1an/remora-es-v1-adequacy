# corpus-adequacy adapter: runs the suite's own build_record() and prints its failures list
# (row 3). Scored on failures, not on --check, because the record hashes checker.py.
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from run_evidence_sufficiency import build_record
print(json.dumps({"failures": "|".join(sorted(build_record()["failures"]))}))
