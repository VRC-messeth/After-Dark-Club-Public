import copy
import unittest
from launch_medal_season import launch_record


class LaunchTests(unittest.TestCase):
    def setUp(self):
        self.record = {"schemaVersion": 1, "seasonId": "medals-2026-09", "startsUtc": 0}

    def test_launch_once(self):
        result, changed = launch_record(self.record, "VRC-messeth", "medals-2026-09", 1790085600)
        self.assertTrue(changed)
        again, changed = launch_record(result, "VRC-messeth", "medals-2026-09", 1790090000)
        self.assertFalse(changed)
        self.assertEqual(result, again)
        self.assertEqual(0, self.record["startsUtc"])

    def test_wrong_actor_cannot_launch(self):
        with self.assertRaises(ValueError):
            launch_record(self.record, "visitor", "medals-2026-09", 1790085600)

    def test_wrong_season_cannot_launch(self):
        with self.assertRaises(ValueError):
            launch_record(self.record, "VRC-messeth", "another-season", 1790085600)

    def test_corrupt_records_do_not_reset(self):
        for field, value in [("schemaVersion", 2), ("startsUtc", -1), ("startsUtc", True), ("startsUtc", "0")]:
            record = copy.deepcopy(self.record)
            record[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                launch_record(record, "VRC-messeth", "medals-2026-09", 1790085600)


if __name__ == "__main__":
    unittest.main()

