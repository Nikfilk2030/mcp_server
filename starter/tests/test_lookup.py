import unittest

from tools import lookup_club_room


class LookupTests(unittest.TestCase):
    def test_known_club(self):
        self.assertEqual(lookup_club_room("orbit"), "Б-204")

    def test_unknown_club(self):
        self.assertEqual(lookup_club_room("missing"), "Клуб не найден")
