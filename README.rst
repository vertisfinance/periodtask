periodtask
==========

.. image:: https://travis-ci.org/vertisfinance/periodtask.svg?branch=master
  :target: https://travis-ci.org/vertisfinance/periodtask

.. image:: https://coveralls.io/repos/github/vertisfinance/periodtask/badge.svg?branch=master
  :target: https://coveralls.io/github/vertisfinance/periodtask?branch=master

Periodic tasks with timezone. Read the docs on
`readthedocs <https://periodtask.readthedocs.io/en/stable/index.html>`_.

Features
--------

- ``cron``-like expressions to define a schedule
- Timezone in ``cron`` expressions
- Multiple ``cron`` schedule for each task
- Configurable e-mail alerts
- Different policies (``SKIP``, ``DELAY``, ``RUN``) to handle situations
  when an instance of a task to start is already running
