import json
import unittest
from pathlib import Path

from tools import lookup_club_room


class LookupTests(unittest.TestCase):
    def test_all_clubs(self):
        path = Path(__file__).resolve().parents[1] / "schedule.json"
        for club in json.loads(path.read_text(encoding="utf-8")):
            with self.subTest(club_id=club["club_id"]):
                self.assertEqual(lookup_club_room(club["club_id"]), club["room"])

    def test_unknown_club(self):
        self.assertEqual(lookup_club_room("missing"), "Клуб не найден")
