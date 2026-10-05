import copy
from dataclasses import FrozenInstanceError
import itertools
import json
import unittest
from unittest.mock import patch

from queue_lab import model, model_document, render
from queue_lab.admission import LabError, check_tree
from queue_lab.core import Job, _validate
from tests.support import cases, document, encode, ledger_oracle


class ModelTests(unittest.TestCase):
    def test_full_frozen_hand_reports(self):
        self.assertEqual(len(cases()), 21)
        for case in cases():
            with self.subTest(name=case["name"]):
                if case["expected"]["status"] == "error":
                    with self.assertRaises(LabError) as caught:
                        model(encode(case["input"]))
                    self.assertEqual(caught.exception.code, case["expected"]["code"])
                else:
                    self.assertEqual(model(encode(case["input"])), case["expected"])
                    self.assertEqual(model_document(case["input"]), case["expected"])

    def test_independent_lifecycle_ordinal_slot_oracle(self):
        for capacity, slots in itertools.product((1, 2), repeat=2):
            for tail in itertools.product("UDCX", repeat=4):
                events, target = [("submit", 1, 0, None)], 1
                for index, symbol in enumerate(tail, start=2):
                    slot = 1 + (index % slots)
                    if symbol == "U":
                        target = index
                        events.append(("submit", target, index, None))
                    elif symbol == "D":
                        events.append(("start", slot, index, None))
                    else:
                        events.append(("complete", slot, index, target if symbol == "C" else 9))
                doc = document(events, (capacity, slots))
                expected = ledger_oracle(doc)
                if expected["status"] == "error":
                    with self.assertRaises(LabError) as caught:
                        model_document(doc)
                    self.assertEqual(caught.exception.code, expected["code"])
                else:
                    self.assertEqual(model_document(doc), expected)

    def test_conservation_peaks_and_labels(self):
        for case in cases():
            if case["expected"]["status"] == "error":
                continue
            report = model_document(case["input"])
            c = report["summary"]
            self.assertEqual(c["events"], c["submissions"] + c["start_requests"] + c["completions"])
            self.assertEqual(c["submissions"], c["admitted"] + c["rejected"])
            self.assertEqual(c["start_requests"], c["started"] + c["not_started"])
            self.assertEqual(c["not_started"], c["busy_not_started"] + c["empty_not_started"])
            self.assertEqual(c["admitted"], c["started"] + c["waiting"])
            self.assertEqual(c["started"], c["completions"] + c["in_service"])
            self.assertEqual(c["admitted"], c["completions"] + c["unfinished"])
            self.assertEqual(c["unfinished"], c["waiting"] + c["in_service"])
            for name in ("waiting", "in_service", "unfinished"):
                self.assertEqual(c["peak_" + name], max([0] + [r["after"][name + "_count"] for r in report["rows"]]))
            self.assertEqual((report["effects"], report["actual_execution"]), ("unmodeled", "unverified"))

    def test_failed_starts_and_no_auto_start(self):
        for name in ("busy-preserves-head", "empty-start", "busy-before-empty", "completion-no-auto-start"):
            case = next(item for item in cases() if item["name"] == name)
            report = model_document(case["input"])
            self.assertEqual(report, case["expected"])
            last = report["rows"][-1]
            if last["result"]["decision"] == "not_started":
                self.assertEqual(last["before"]["waiting"], last["after"]["waiting"])
                self.assertEqual(last["before"]["in_service"], last["after"]["in_service"])
        doc = document([("submit",1,0,None),("submit",2,0,None)], (1,1))
        report = model_document(doc)
        self.assertEqual(report["summary"]["started"], 0)
        self.assertEqual(report["summary"]["rejected"], 1)

    def test_snapshots_input_frozen_and_independent(self):
        doc = document([("submit",1,0,None),("start",1,1,None)])
        original = copy.deepcopy(doc)
        first, second = model_document(doc), model_document(doc)
        self.assertEqual(doc, original)
        first["rows"][0]["after"]["waiting"][0]["job_id"] = "invented"
        self.assertEqual(second["rows"][0]["after"]["waiting"][0]["job_id"], "lab-job-0001")
        self.assertEqual(first["rows"][1]["before"]["waiting"][0]["job_id"], "lab-job-0001")
        first["final_state"]["in_service"][0]["job_id"] = "invented"
        self.assertEqual(first["rows"][-1]["after"]["in_service"][0]["job_id"], "lab-job-0001")
        for record, field in ((_validate(doc).events[0], "kind"), (Job("lab-job-0001",0), "job_id")):
            with self.assertRaises(FrozenInstanceError):
                setattr(record, field, "invented")

    def test_late_structure_before_ownership(self):
        doc = document([("complete",1,0,9),("submit",1,1,None)])
        doc["events"][-1]["extra"] = True
        with patch("queue_lab.core._simulate") as replay:
            with self.assertRaises(LabError) as caught:
                model_document(doc)
            self.assertEqual(caught.exception.code, "schema.invalid")
            replay.assert_not_called()

    def test_duplicate_submission_even_rejected_completed(self):
        for events in ([('submit',1,0,None),('submit',2,0,None),('submit',2,0,None)],
                       [('submit',1,0,None),('start',1,0,None),('complete',1,0,1),('submit',1,0,None)]):
            with self.assertRaises(LabError) as caught:
                model_document(document(events))
            self.assertEqual(caught.exception.code, "schema.invalid")

    def test_exact_schema_missing_extra_null_and_unknown(self):
        base = document()
        for path in ((), ("policy",), ("events",0)):
            for mode in ("missing", "extra", "null"):
                doc = copy.deepcopy(base)
                target = doc
                for part in path:
                    target = target[part]
                if mode == "missing":
                    del target[next(iter(target))]
                elif mode == "extra":
                    target["extra"] = 1
                else:
                    target[next(iter(target))] = None
                with self.assertRaises(LabError):
                    model_document(doc)
        for field, value in (("schema_version",True),("profile","other"),("queue_id","lab-queue-１２３４"),
                             ("events",None),("source_kind",[])):
            doc = copy.deepcopy(base)
            doc[field] = value
            with self.assertRaises(LabError):
                model_document(doc)
        for kind in ([], "other", None):
            doc = document()
            doc["events"][0]["kind"] = kind
            with self.assertRaises(LabError):
                model_document(doc)
        doc = document([("submit",1,0,None),("start",1,0,None)])
        doc["events"][-1]["event_id"] = doc["events"][0]["event_id"]
        with self.assertRaises(LabError):
            model_document(doc)

    def test_policy_slot_and_time_bounds(self):
        for field, upper in (("waiting_capacity",8),("service_slots",4)):
            for value in (True,0,-1,upper+1,None,"1",1.0):
                doc = document()
                doc["policy"][field] = value
                with self.assertRaises(LabError):
                    model_document(doc)
            for value in (1,upper):
                doc = document()
                doc["policy"][field] = value
                self.assertEqual(model_document(doc)["status"], "modeled")
        for value in (True,0,2,-1,None,"1",1.0):
            doc = document([("start",1,0,None)])
            doc["events"][0]["slot_id"] = value
            with self.assertRaises(LabError):
                model_document(doc)
        for value in (True,-1,3600001,None,"1",0.0):
            doc = document()
            doc["events"][0]["time_ms"] = value
            with self.assertRaises(LabError):
                model_document(doc)
        with self.assertRaises(LabError):
            model_document(document([("submit",1,1,None),("start",1,0,None)]))

    def test_event_cardinality_at_and_over(self):
        for kind in ("submit", "start", "complete"):
            events = [(kind,i if kind=='submit' else 1,0,1 if kind=='complete' else None) for i in range(65)]
            with self.assertRaises(LabError) as caught:
                model_document(document(events))
            self.assertEqual(caught.exception.code, "input.limit")
            # Complete-only64 is semantically invalid, not structurally limited.
            doc = document(events[:64])
            if kind == "complete":
                with self.assertRaises(LabError) as caught:
                    model_document(doc)
                self.assertEqual(caught.exception.code, "trace.invalid")
            else:
                self.assertEqual(model_document(doc)["summary"]["events"],64)
        events = [(kind,i,3600000,None) for i in range(64) for kind in ("submit","start")]
        # All starts refer to slot1; submissions remain unique.
        doc = document([(k,t if k=='submit' else 1,ms,None) for k,t,ms,_ in events], (8,4))
        self.assertEqual(model_document(doc)["summary"]["events"],128)
        doc["events"].append(dict(event_id="lab-event-9999",kind="start",slot_id=1,time_ms=3600000))
        with self.assertRaises(LabError) as caught:
            model_document(doc)
        self.assertEqual(caught.exception.code, "input.limit")

    def test_large_admitted_report_growth_and_defensive_seam(self):
        events = [("submit",i,0,None) for i in range(1,9)] + [("start",i,0,None) for i in range(1,5)]
        events += [("submit",i,0,None) for i in range(9,13)]
        events += [("submit",i,3600000,None) for i in range(13,65)]
        events += [("start",1,3600000,None)] * 60
        doc = document(events,(8,4))
        report = model_document(doc)
        self.assertEqual(report["summary"]["events"],128)
        self.assertEqual(report["summary"]["unfinished"],12)
        self.assertLess(len(encode(doc)),65536)
        self.assertLess(len(render(report).encode()),262144)
        with patch("queue_lab.core.MAX_OUTPUT",len(render(report).encode())-1):
            with self.assertRaises(LabError) as caught:
                model_document(doc)
            self.assertEqual(caught.exception.code,"output.error")
        with self.assertRaises(LabError):
            render({"injected":"x"*262144})

    def test_native_cycles_aliases_and_hook_identity(self):
        cycle=[]
        cycle.append(cycle)
        with self.assertRaises(LabError):
            model_document(cycle)
        shared=[0]
        check_tree([shared,shared])
        calls=[]
        class Meta(type):
            def __eq__(cls, other):
                calls.append("class equality")
                return False
            def __hash__(cls):
                calls.append("class hash")
                return 7
        class Exotic(metaclass=Meta):
            pass
        class Mapping(dict,metaclass=Meta):
            def items(self):
                calls.append("items")
                return ()
        class String(str,metaclass=Meta):
            def __hash__(self):
                calls.append("key hash")
                return super().__hash__()
        class Integer(int,metaclass=Meta):
            def __str__(self):
                calls.append("number str")
                return "1"
        bad_key={String("key"):0}
        calls.clear()  # Construction is outside the admission API.
        for value in (Exotic(),Mapping(),String("value"),Integer(1),bad_key,object(),(1,),b"{}"):
            with self.assertRaises(LabError):
                model_document(value)
        self.assertEqual(calls,[])

    def test_native_visit_depth_number_string_and_byte_bounds(self):
        values=[[0]*31 for _ in range(128)]
        values[-1].pop()
        check_tree(values)
        values[-1].append(0)
        with self.assertRaises(LabError):
            check_tree(values)
        nested=0
        for _ in range(8):
            nested=[nested]
        check_tree(nested)
        with self.assertRaises(LabError):
            check_tree([nested])
        check_tree(9999999999999999)
        for number in (10**16,-10**15,1<<10000,1.0,float('nan')):
            with self.assertRaises(LabError):
                check_tree(number)
        check_tree('é'*64)
        for value in ('é'*65,'\ud800',{str(i):'x'*128 for i in range(500)}):
            with self.assertRaises(LabError):
                model_document(value)
        with self.assertRaises(LabError):
            model(bytearray(encode(document())))
        self.assertEqual(json.loads(render(model(encode(document()))))["status"],"modeled")


if __name__ == "__main__":
    unittest.main()
