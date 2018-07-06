import unittest

from periodtask import Period
from periodtask.periods import (
    parse_cron, parse_period, BadPeriodDef, BadCronFormat
)


class CronTest(unittest.TestCase):
    def test_Period(self):
        period = Period()
        self.assertEqual(period.seconds, set([0]))

    def test_Period_str(self):
        period = Period()
        self.assertEqual(len(str(period).splitlines()), 8)

    def test_parse_period_raises(self):
        with self.assertRaises(BadPeriodDef):
            parse_period(0)

    def test_parse_period_raises_2(self):
        with self.assertRaises(BadCronFormat):
            parse_period('?')

    def test_parse_period(self):
        period = parse_period(Period())
        self.assertEqual(period.seconds, set([0]))

    def test_cron_1(self):
        period = parse_cron('0')
        self.assertEqual(period.minutes, set([0]))

    def test_cron_2(self):
        period = parse_period('1-3,5')
        self.assertEqual(period.minutes, set([1, 2, 3, 5]))
