import concurrent.futures
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))

spec = importlib.util.spec_from_file_location("pet", Path(__file__).parents[1] / "scripts/pet.py")
pet = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pet)


class PetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.db = pet.connect(self.root)
        self.transcript = self.root / "session.jsonl"

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def write(self, total):
        rows = [{"type": "session_meta", "payload": {"id": "session"}}]
        if total is not None:
            rows.append({"type": "event_msg", "payload": {"type": "token_count", "info": {
                "total_token_usage": {"total_tokens": total}}}})
        self.transcript.write_text("\n".join(json.dumps(x) for x in rows), encoding="utf-8")

    def event(self, kind):
        return {"hook_event_name": kind, "session_id": "session", "transcript_path": str(self.transcript)}

    def test_real_flow_and_repeated_stop(self):
        self.write(9000)
        pet.handle(self.db, self.event("SessionStart"))
        self.write(20500)
        self.assertEqual(pet.handle(self.db, self.event("Stop")), 11500)
        self.assertEqual(pet.handle(self.db, self.event("Stop")), 0)
        state = pet.status(self.db)
        self.assertEqual((state["level"], state["level_progress"]), (1, 0))
        self.assertEqual(state["credited_tokens"], 11500)

    def test_new_session_without_counter(self):
        self.write(None)
        pet.handle(self.db, self.event("SessionStart"))
        self.write(1500)
        self.assertEqual(pet.handle(self.db, self.event("Stop")), 1500)

    def test_first_stop_does_not_backfill(self):
        self.write(500000)
        self.assertEqual(pet.handle(self.db, self.event("Stop")), 0)

    def test_counter_regression(self):
        pet.record(self.db, "s", 100)
        pet.record(self.db, "s", 200)
        pet.record(self.db, "s", 50)
        pet.record(self.db, "s", 220)
        self.assertEqual(pet.status(self.db)["credited_tokens"], 120)

    def test_resume_excludes_unobserved_usage(self):
        pet.record(self.db, "s", 100)
        pet.record(self.db, "s", 10000, baseline=True)
        self.assertEqual(pet.record(self.db, "s", 11000), 1000)

    def test_wrong_session_and_missing_counter(self):
        self.write(1000)
        with self.assertRaises(ValueError):
            pet.snapshot(self.transcript, "wrong")
        self.write(None)
        with self.assertRaises(ValueError):
            pet.handle(self.db, self.event("Stop"))
        self.assertEqual(pet.status(self.db)["credited_tokens"], 0)

    def test_partial_line(self):
        self.write(1000)
        with self.transcript.open("a", encoding="utf-8") as f:
            f.write('\n{"type":')
        self.assertEqual(pet.snapshot(self.transcript, "session"), 1000)

    def test_concurrent_duplicate_callbacks(self):
        pet.record(self.db, "s", 0)
        def update(_):
            db = pet.connect(self.root)
            try:
                return pet.record(db, "s", 5000)
            finally:
                db.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            self.assertEqual(sum(pool.map(update, range(8))), 5000)


if __name__ == "__main__":
    unittest.main()
