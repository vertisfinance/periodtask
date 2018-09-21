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

0.5.5
-----
- Improved wording of buildtin e-mail templates.
- Added the ``email_limitation`` parameter to ``Task``.

0.5.3
-----
- Bugfix: ``mail_success``, ``mail_failure``, ``mail_skipped``,
  ``mail_delayed`` parameters of ``Task`` were not handled correctly.

0.5.2
-----
- ``template_dir`` given to ``Task`` extends the default template dir, so
  templates can be overridden individually.
