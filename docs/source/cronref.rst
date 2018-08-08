Cron format reference
=====================

The cron expression is made up of 7 parts separated by one or more spaces.
If fewer parts are presented in an expression, the missing ones will be
substituted with defaults. Each part represents
::

  seconds minutes hours days months years timezone

respectively. The default is ``0 */5 * * * * UTC``.

Given a second (total seconds since EPOCH), this will be converted to a
timestamp: ``2018-08-07 16:57:30 WED`` based on the given timezone.
This timestamp matches the cron expression if the second (30 in the example)
matches the seconds part, the minute (57) matches the minutes part etc.

Each part is made up of atoms separated by a comma. The part matches if any
of the atoms matches.

An atom can be:

``*``
  Any possible value matches.

an integer (``12``)
  The given value matches.

a range (``12-23``)
  Any value in the range (inclusive) matches.
  Range lower or upper bounds can be empty: ``-12``, ``2-`` or even ``-``.
  (Note that ``*`` is equivalent to ``-``.)

a range (or ``*``) with step (``2-10/3``)
  In case of ``2-10/3`` the following values match: 2, 5, 8.

In case of the days part, normally the day of month is taken into account. If
the atom is given in a 'day of week' format, the weekday (``WED`` in the
example) and the day of month both considered. The day of week atom can be:

a weekday in upper or lowercase (``mon``)
  Valid values are ``MON``, ``TUE``, ``WED``, ``THU``,
  ``FRI``, ``SAT``, ``SUN`` (and the lowercase variants)

a range of weekdays (``MON-FRI``)
  To construct a valid range it is important to know that ``MON`` is
  considered the first day of the week while ``SUN`` is the last one.

a range (or a single value) with a 'first-last clause' (``sun/L``)
  ``L`` means '7 days from now is not in the current month', ``LL``
  means '14 days from now is not in the current month', etc.

  ``F`` means '7 days before now was not in the current month', ``FF``
  means '14 days before now was not in the current month', etc.

  Given the above rule, ``sun/L`` means 'last Sunday in the month'.

Examples
--------

- Last Sunday of each month at 21.00 according to UTC time:
  ``0 0 21 sun/L`` (note that 'each month', 'each year' and 'UTC' are
  dfaults)
- Everey weekday at 18.15 in Budapest time:
  ``0 15 18 mon-fri * * Europe/Budapest``
