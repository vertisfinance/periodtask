==========
periodtask
==========

Scheduled tasks with timezones and configurable e-mail alerts.

Features
========

- ``cron``-like expressions to define a schedule
- Timezone in ``cron`` expressions
- Multiple ``cron`` schedule for each task
- Configurable e-mail alerts
- Different policies (``SKIP``, ``DELAY``, ``RUN``) to handle situations
  when an instance of a task to start is already running

Topics
======

.. toctree::
  :maxdepth: 3

  quickref
  cronref
  API

Release Notes
=============

0.7.0
-----
- Former ``email_limitation`` is changed to email thresholds. This is a
  breaking change!

0.6.0
-----
- Improved handling of ``max_lines``.
- Added task param ``failure_email_limitation``.

0.5.5
-----
- Improved wording of builtin e-mail templates.
- Added the ``email_limitation`` parameter to ``Task``.

0.5.3
-----
- Bugfix: ``mail_success``, ``mail_failure``, ``mail_skipped``,
  ``mail_delayed`` parameters of ``Task`` were not handled correctly.

0.5.2
-----
- ``template_dir`` given to ``Task`` extends the default template dir, so
  templates can be overridden individually.
