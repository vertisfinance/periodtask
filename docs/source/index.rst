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

Quick Reference (Cheat sheet)
=============================

If you already know the concepts but need a quick refresh on the API,
here is a detailed example::

  #!/usr/bin/env python3

  from periodtask import TaskList, Task

  TaskList(Task('lister', ('ls',))).start()


.. toctree::
  :maxdepth: 3

  tutorial
