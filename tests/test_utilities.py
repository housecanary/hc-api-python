import unittest
from housecanary import utilities


class UtilitiesTestCase(unittest.TestCase):
    """Tests for Utilities"""

    def test_get_readable_time_string(self):
        self.assertEqual('30 Seconds', utilities.get_readable_time_string(30))
        self.assertEqual('1 Minute', utilities.get_readable_time_string(60))
        self.assertEqual('5 Minutes', utilities.get_readable_time_string(300))
        self.assertEqual('5 Minutes 30 Seconds', utilities.get_readable_time_string(330))
        self.assertEqual('1 Hour 1 Minute 1 Second', utilities.get_readable_time_string(3661))
        self.assertEqual('2 Hours', utilities.get_readable_time_string(7200))
        self.assertEqual('1 Day 2 Hours', utilities.get_readable_time_string(93600))
        self.assertEqual('2 Days', utilities.get_readable_time_string(172800))
