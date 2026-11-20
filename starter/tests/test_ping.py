import unittest

from tools import ping


class PingTests(unittest.TestCase):
    def test_ping(self):
        self.assertEqual(ping(), "pong")
