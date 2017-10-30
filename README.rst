periodtask
==========

Periodic task with timezone

.. code-block:: python

  from periodtask import Task, Period, parse_cron, send_mail


  task = Task(
      name='test',
      command=('/periodtask/test_script.py',),
      periods=[
          Period(
              timezone='Europe/Budapest',
              minutes=list(range(0, 60)),
              seconds=list(range(0, 60, 5)),
          ),
          # cron fmt: minutes, hours, days, months, weekdays,
          #           timezone, years, seconds
          # in contrast to Cron:
          #     - `weekdays` is not treated specially
          #     - no special handling of daylight saving time changes
          parse_cron('* * * * * Europe/Budapest * */5')
      ],
      run_on_start=True,
      mail_failure=True,
      mail_success=True,
      mail_skipped=True,
      wait_timeout=5,
      stop_signal=signal.SIGINT,
      send_mail_func=send_mail,
      from_email='richardbann@gmail.com',
      recipient_list=['richard.bann@vertis.com']
  )
  task.start()
