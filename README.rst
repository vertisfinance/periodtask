periodtask
==========

Periodic task with timezone

.. code-block:: python

  from periodtask import Task, Period, parse_cron, send_mail

  def _send_mail(subject, message, html_message=None):
      return send_mail(
          subject, message,
          from_email='from@my.service',
          recipient_list=['admins@my.service'],
          html_message=html_message
      )

  task = Task(
      name='test',
      command=('/periodtask/test_script.py',),
      periods=[
          Period(
              timezone='Europe/Budapest',
              minutes=list(range(0, 60)),
              seconds=list(range(0, 60, 5)),
          ),
          parse_cron('* * * * * Europe/Budapest * */5')
      ],
      run_on_start=True,
      mail_failure=True,
      mail_success=True,
      mail_skipped=True,
      wait_timeout=5,
      stop_signal=signal.SIGINT,
      send_mail_func=_send_mail,
      policy=SKIP
  )
  task.start()
