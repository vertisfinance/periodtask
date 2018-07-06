periodtask
==========

Periodic task with timezone

.. image:: https://travis-ci.org/vertisfinance/periodtask.svg?branch=master
    :target: https://travis-ci.org/vertisfinance/periodtask
.. image:: https://coveralls.io/repos/github/vertisfinance/periodtask/badge.svg?branch=master
:target: https://coveralls.io/github/vertisfinance/periodtask?branch=master

.. code-block:: python

  from periodtask import Task, TaskList, Period, send_mail

  def _send_mail(subject, message, html_message=None):
      return send_mail(
          subject, message,
          from_email='from@my.service',
          recipient_list=['admins@my.service'],
          html_message=html_message
      )

  tasks = TaskList(
      Task(
        name='test',
        command=('/periodtask/test_script.py',),
        periods=[
            '* * * * * Europe/Budapest * */5',
            Period(
                timezone='Europe/Budapest',
                minutes=list(range(0, 60)),
                seconds=list(range(0, 60, 5)),
            ),
        ],
        run_on_start=True,
        mail_failure=True,
        mail_success=False,
        mail_skipped=True,
        wait_timeout=5,
        stop_signal=signal.SIGINT,
        send_mail_func=_send_mail,
        policy=SKIP
      )
  )

  tasks.start()
