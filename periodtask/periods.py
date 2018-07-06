import logging

import pytz


logger = logging.getLogger('periodtask.periods')


class BadPeriodDef(Exception):
    pass


class BadCronFormat(Exception):
    pass


class Period:
    def __init__(
        self,
        minutes=set(range(0, 60, 5)),
        hours=set(range(0, 24)),
        days=set(range(1, 32)),
        months=set(range(1, 13)),
        weekdays=set(range(1, 8)),  # Monday: 1, ..., Sunday: 7
        timezone='UTC',
        years=set(range(1900, 3000)),
        seconds=set([0]),
    ):
        self.minutes = minutes
        self.hours = hours
        self.days = days
        self.months = months
        self.weekdays = weekdays
        self.timezone = pytz.timezone(timezone)
        self.years = years
        self.seconds = seconds

    def __str__(self):
        return '\n'.join([
            'minutes: %s' % self.minutes,
            'hours: %s' % self.hours,
            'days: %s' % self.days,
            'months: %s' % self.months,
            'weekdays: %s' % self.weekdays,
            'timezone: %s' % self.timezone,
            'years: %s' % self.years,
            'seconds: %s' % self.seconds,
        ])


def parse_period(p):
    if isinstance(p, Period):
        return p
    if isinstance(p, str):
        return parse_cron(p)
    raise BadPeriodDef(p)


def parse_cron(cron_string):
    parts = ['*/5', '*', '*', '*', '*', 'UTC', '*', '0']
    try:
        for i, p in enumerate([p.strip() for p in cron_string.split()]):
            parts[i] = p
    except IndexError:
        raise BadCronFormat('too many parts of format string')

    minutes = to_list(parts[0], 0, 59)
    hours = to_list(parts[1], 0, 59)
    days = to_list(parts[2], 1, 31)
    months = to_list(parts[3], 1, 12)
    weekdays = to_list(parts[4], 1, 7)
    timezone = parts[5]
    years = to_list(parts[6], 1900, 3000)
    seconds = to_list(parts[7], 0, 60)

    try:
        pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        raise BadCronFormat('unknown timezone: %s' % timezone)

    return Period(
        minutes, hours, days, months, weekdays, timezone, years, seconds
    )


def to_list(fmt, low, high):
    ret = _to_list(fmt, low, high)
    if not ret:
        raise BadCronFormat('empty set, would never run: %s' % fmt)
    return ret


def _to_list(fmt, low, high, inner=False):
    try:
        fmt = fmt.strip()
        fmt = int(fmt)
    except ValueError:
        pass

    if fmt == '':
        return set()

    if isinstance(fmt, int):
        if fmt < low or fmt > high:
            desc = 'value not in range %s-%s (%s)' % (low, high, fmt)
            raise BadCronFormat(desc)
        return {fmt}

    if isinstance(fmt, list):
        if inner:
            raise BadCronFormat('too complex')

        def sublist(x):
            return _to_list(x, low, high, inner=True)

        return set.union(*(sublist(x) for x in fmt))

    if isinstance(fmt, str):
        splitted = fmt.split(',')
        if len(splitted) > 1:
            def sublist(x):
                return _to_list(x, low, high)
            return set.union(*(sublist(x) for x in splitted))

        if fmt == '*':
            return set(range(low, high + 1))

        _rng = fmt.split('/', maxsplit=1)
        if len(_rng) == 1:
            rng, step = _rng[0], 1
        else:
            [rng, step] = _rng
        if step == '':
            step = 1
        try:
            step = int(step)
        except ValueError:
            desc = 'step should be an integer (%s)' % fmt
            raise BadCronFormat(desc)

        if rng == '*':
            return set(range(low, high + 1, step))

        splitted = rng.split('-', maxsplit=1)
        if len(splitted) != 2:
            raise BadCronFormat('invalid range (%s)' % fmt)
        try:
            a, b = int(splitted[0]), int(splitted[1])
        except ValueError:
            raise BadCronFormat('invalid range (%s)' % fmt)

        a = low if a < low else a
        b = high if b > high else b
        return set(range(a, b + 1, step))

    raise BadCronFormat('invalid type (%s)' % fmt)
