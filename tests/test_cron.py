import unittest
from datetime import datetime

import pytz

from periodtask.periods import Period, BadCronFormat


def to_ts(s):
    dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.utc)
    ts = (dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
    return int(ts)


class CronTest(unittest.TestCase):
    def test_bad_1(self):
        with self.assertRaises(BadCronFormat):
            Period('* * * * * * * UTC')

    def test_bad_2(self):
        with self.assertRaises(BadCronFormat):
            Period('* * * * * * whatever')

    def test_bad_3(self):
        with self.assertRaises(BadCronFormat):
            Period('*/2/3')

    def test_bad_4(self):
        with self.assertRaises(BadCronFormat):
            Period('1-2-3')

    def test_bad_5(self):
        with self.assertRaises(BadCronFormat):
            Period('0-99')

    def test_bad_6(self):
        with self.assertRaises(BadCronFormat):
            Period('0-a')

    def test_bad_7(self):
        with self.assertRaises(BadCronFormat):
            Period('9-8')

    def test_bad_8(self):
        with self.assertRaises(BadCronFormat):
            Period('*/a')

    def test_bad_9(self):
        with self.assertRaises(BadCronFormat):
            Period('* * * * 0 * UTC')

    def test_check_1(self):
        p = Period()
        self.assertEqual(
            p._check(to_ts('2018-07-09 18:05:00')),
            '2018-07-09 18:05:00 UTC, MON'
        )

    def test_check_2(self):
        p = Period('10-20/5 * * * * *')
        self.assertFalse(
            p._check(to_ts('2018-07-09 18:05:00'))
        )
        self.assertEqual(
            p._check(to_ts('2018-07-09 18:05:10')),
            '2018-07-09 18:05:10 UTC, MON'
        )
        self.assertEqual(
            p._check(to_ts('2018-07-09 18:05:15')),
            '2018-07-09 18:05:15 UTC, MON'
        )
        self.assertEqual(
            p._check(to_ts('2018-07-09 18:05:20')),
            '2018-07-09 18:05:20 UTC, MON'
        )
        self.assertFalse(
            p._check(to_ts('2018-07-09 18:05:25'))
        )

    def test_check_3(self):
        p = Period('0 * * sun * *')
        self.assertFalse(
            p._check(to_ts('2018-07-09 18:05:00'))
        )
        self.assertEqual(
            p._check(to_ts('2018-07-08 18:05:00')),
            '2018-07-08 18:05:00 UTC, SUN'
        )

    def test_dow_range(self):
        p = Period('* * * mon-wed * *')
        self.assertFalse(
            p._check(to_ts('2018-07-08 18:05:00'))
        )
        self.assertEqual(
            p._check(to_ts('2018-07-09 18:05:00')),
            '2018-07-09 18:05:00 UTC, MON'
        )
        self.assertEqual(
            p._check(to_ts('2018-07-10 18:05:00')),
            '2018-07-10 18:05:00 UTC, TUE'
        )
        self.assertEqual(
            p._check(to_ts('2018-07-11 18:05:00')),
            '2018-07-11 18:05:00 UTC, WED'
        )
        self.assertFalse(
            p._check(to_ts('2018-07-12 18:05:00'))
        )

    def test_any_fail(self):
        p = Period('0 */3 0-12 sun/L 7 2018-2020')
        self.assertFalse(p._check(to_ts('2018-07-12 18:05:00')))
        self.assertFalse(p._check(to_ts('2018-07-12 18:06:00')))
        self.assertFalse(p._check(to_ts('2018-08-12 10:06:00')))
        self.assertFalse(p._check(to_ts('2017-07-12 10:06:00')))
        self.assertFalse(p._check(to_ts('2018-07-08 10:06:00')))

    def test_first(self):
        p = Period('0 */3 0-12 sun/F 7 2018-2020')
        self.assertEqual(
            p._check(to_ts('2018-07-01 10:06:00')),
            '2018-07-01 10:06:00 UTC, SUN'
        )
        self.assertFalse(p._check(to_ts('2018-07-08 10:06:00')))

        p = Period('0 */3 0-12 sun/FF 7 2018-2020')
        self.assertEqual(
            p._check(to_ts('2018-07-08 10:06:00')),
            '2018-07-08 10:06:00 UTC, SUN'
        )
        self.assertFalse(p._check(to_ts('2018-07-15 10:06:00')))

        p = Period('0 */3 0-12 sun/FFF 7 2018-2020')
        self.assertEqual(
            p._check(to_ts('2018-07-15 10:06:00')),
            '2018-07-15 10:06:00 UTC, SUN'
        )
        self.assertFalse(p._check(to_ts('2018-07-08 10:06:00')))

    def test_last(self):
        p = Period('0 */3 0-12 sun/L 7 2018-2020')
        self.assertEqual(
            p._check(to_ts('2018-07-29 10:06:00')),
            '2018-07-29 10:06:00 UTC, SUN'
        )
        self.assertFalse(p._check(to_ts('2018-07-22 10:06:00')))

        p = Period('0 */3 0-12 sun/LL 7 2018-2020')
        self.assertEqual(
            p._check(to_ts('2018-07-22 10:06:00')),
            '2018-07-22 10:06:00 UTC, SUN'
        )
        self.assertFalse(p._check(to_ts('2018-07-29 10:06:00')))
        self.assertFalse(p._check(to_ts('2018-07-15 10:06:00')))

        p = Period('0 */3 0-12 sun/LLL 7 2018-2020')
        self.assertEqual(
            p._check(to_ts('2018-07-15 10:06:00')),
            '2018-07-15 10:06:00 UTC, SUN'
        )
        self.assertFalse(p._check(to_ts('2018-07-08 10:06:00')))
        self.assertFalse(p._check(to_ts('2018-07-22 10:06:00')))

    def test_more_last_first(self):
        p = Period('0 * * sun/F,sun/L')
        self.assertEqual(
            p._check(to_ts('2018-07-01 00:00:00')),
            '2018-07-01 00:00:00 UTC, SUN'
        )
        self.assertEqual(
            p._check(to_ts('2018-07-29 00:00:00')),
            '2018-07-29 00:00:00 UTC, SUN'
        )
