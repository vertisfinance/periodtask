import logging
from datetime import datetime, timedelta

import pytz


logger = logging.getLogger('periodtask.periods')


class BadCronFormat(Exception):
    pass


class Period:
    DOW = {
        'MON': 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5, 'SAT': 6, 'SUN': 7
    }
    SEC_FMT = '{:4}-{:0>2}-{:0>2} {:0>2}:{:0>2}:{:0>2} {}, {}'
    VALID_LF = (
        'F', 'FF', 'FFF', 'FFFF', 'FFFFF',
        'L', 'LL', 'LLL', 'LLLL', 'LLLLL',
    )
    DELTA = timedelta(days=7)

    def __init__(self, cron='0 */5 * * * * UTC'):
        (
            self.seconds, self.minutes, self.hours, self.days,
            self.months, self.years, self.timezone
        ) = self._parse_cron(cron)

    def _parse_cron(self, cron):
        parts = ['0', '*/5', '*', '*', '*', '*', 'UTC']
        try:
            for i, p in enumerate([p for p in cron.split()]):
                parts[i] = p
        except IndexError:
            raise BadCronFormat('too many parts of format string') from None

        seconds = self._parse_part(parts[0], 0, 60)
        minutes = self._parse_part(parts[1], 0, 59)
        hours = self._parse_part(parts[2], 0, 59)
        days = self._parse_part(parts[3], 1, 31, dom_allowed=True)
        months = self._parse_part(parts[4], 1, 12)
        years = self._parse_part(parts[5], 0, None)
        timezone = parts[6]
        try:
            pytz.timezone(timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            raise BadCronFormat('unknown timezone: %s' % timezone) from None

        return (
            seconds, minutes, hours, days, months, years,
            pytz.timezone(timezone)
        )

    def _parse_part(self, part, low, high, dom_allowed=False):
        part = part.strip()
        splitted = part.split(',')
        return [self._parse_split(x, low, high, dom_allowed) for x in splitted]

    def _parse_split(self, split, low, high, dom_allowed):
        try:
            return self._parse_atom(split, low, high, dow=False)
        except BadCronFormat:
            if dom_allowed:
                return self._parse_atom(split, 1, 7, dow=True)
            else:
                raise

    def _parse_atom(self, atom, low, high, dow=False):
        atom = atom.strip()

        # the star is an alias to '-'
        atom = '-' if atom == '*' else atom

        # handle the case when it is a simple integer
        n = self._parse_int(atom, low, high, dow)
        if n is not None:
            return (n, n + 1, 1, dow)

        # parse the step part
        _rng_step = atom.split('/')
        if len(_rng_step) == 1:
            rng, step = atom, 1
        elif len(_rng_step) == 2:
            rng, step = _rng_step
        else:
            desc = 'invalid format: %s' % atom
            raise BadCronFormat(desc)

        # parse the range
        rng = '-' if rng == '*' else rng
        lo_hi = rng.split('-')
        if len(lo_hi) == 1:
            lo, hi = lo_hi[0], lo_hi[0]
        elif len(lo_hi) == 2:
            lo, hi = lo_hi
        else:
            desc = 'invalid format: %s' % atom
            raise BadCronFormat(desc)
        if dow:
            lo, hi = 'MON' if lo == '' else lo, 'SUN' if hi == '' else hi
        else:
            lo, hi = low if lo == '' else lo, high if hi == '' else hi
        lo = self._parse_int(lo, low, high, dow)
        if lo is None:
            desc = 'lower bound is invalid: %s' % atom
            raise BadCronFormat(desc)

        if hi is not None:
            hi = self._parse_int(hi, low, high, dow)
            if hi is None:
                desc = 'upper bound is invalid: %s' % atom
                raise BadCronFormat(desc)

        if hi is not None and lo > hi:
            desc = 'lower bound is too high: %s' % atom
            raise BadCronFormat(desc)

        # parse step
        if dow and step in self.VALID_LF:
            pass
        else:
            step = self._parse_int(step, 1, high)
            if step is None:
                desc = 'step is invalid: %s' % atom
                raise BadCronFormat(desc)
        return (lo, hi if hi is None else hi + 1, step, dow)

    def _parse_int(self, n, low, high, dow=False):
        if dow:
            try:
                return self.DOW[n.upper()]
            except (KeyError, AttributeError):
                return None
        try:
            n = int(n)
        except ValueError:
            return
        else:
            if n < low:
                desc = 'value is lower than %s (%s)' % (low, n)
                raise BadCronFormat(desc)
            if high is not None and n > high:
                desc = 'value is higher than %s (%s)' % (high, n)
                raise BadCronFormat(desc)
            return n

    def _check_part(self, part, actual):
        for lo, hi, step, _ in part:
            hi = actual + 1 if hi is None else hi
            if actual in range(lo, hi, step):
                return True
        return False

    def _check(self, sec):
        utc = datetime.utcfromtimestamp(sec).replace(tzinfo=pytz.utc)
        dt = self.timezone.normalize(utc).astimezone(self.timezone)
        isocalendar = dt.isocalendar()

        year = dt.year
        weekday = isocalendar[2]
        month = dt.month
        day = dt.day
        hour = dt.hour
        minute = dt.minute
        second = dt.second

        if not self._check_part(self.seconds, second):
            return False
        if not self._check_part(self.minutes, minute):
            return False
        if not self._check_part(self.hours, hour):
            return False
        if not self._check_part(self.months, month):
            return False
        if not self._check_part(self.years, year):
            return False

        ok = False
        for lo, hi, step, dow in self.days:
            if not dow:
                if day in range(lo, hi, step):
                    ok = True
                    break
            else:
                if weekday not in range(lo, hi):
                    continue
                if isinstance(step, int):
                    if weekday in range(lo, hi, step):
                        ok = True
                        break
                else:
                    delta = self.DELTA
                    var_dt = dt
                    if step[0] == 'F':
                        delta = -delta
                    ok2 = True
                    for i in range(1, len(step)):
                        var_dt += delta
                        if var_dt.month != month:
                            ok2 = False
                            break
                    if ok2:
                        var_dt += delta
                        if var_dt.month != month:
                            ok = True
                            break
        if not ok:
            return False

        return self.SEC_FMT.format(
                year, month, day, hour, minute, second, self.timezone,
                list(self.DOW.keys())[weekday - 1]
            )
