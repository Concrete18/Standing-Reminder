import unittest
from Standing_Reminder import Reminder  # type: ignore


class TestGetIdleDuration(unittest.TestCase):
    def setUp(self):
        self.test = Reminder()

    def main_test(self):
        idle_duration = self.test.get_idle_duration()
        self.assertTrue(type(idle_duration) is int)
