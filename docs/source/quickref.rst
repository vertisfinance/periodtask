Quick reference
===============

.. code-block:: python

  #!/usr/bin/env python3

  import logging
  import os
  import signal

  from periodtask import TaskList, Task, SKIP
  from periodtask.mailsender import MailSender


  logging.basicConfig(level=logging.DEBUG)

  # we send STDOUT and STDERR to these loggers
  stdout_logger = logging.getLogger('periodtask.stdout')
  stderr_logger = logging.getLogger('periodtask.stderr')


  # this function will be called with (subject, message, html_message),
  # but MailSender needs to know more to send
  send_success = MailSender(
      os.environ.get('EMAIL_HOST'),  # the SMTP server host
      int(os.environ.get('EMAIL_PORT')),  # the SMTP port
      os.environ.get('SUCCESS_EMAIL_FROM'),  # the sender
      os.environ.get('SUCCESS_EMAIL_RECIPIENT'),  # the list of recipients
      timeout=10,  # connection timeout in seconds
      use_ssl=False,  # ... and some SMTP specific parameters
      use_tls=False,
      username=None,
      password=None
  ).send_mail


  tasks = TaskList(
      Task(
          'lister',  # name of the task
          ('ls', '-hal'),  # the command to run; see Popen
          # a list of cron-like expressions:
          # sec min hour day month year timezone
          # defaults: 0 */5 * * * * UTC
          ['0 * * * * * UTC'],  # sec min hour day month year timezone
          mail_success=send_success,  # e-mail sending function or None
          mail_failure=None, mail_skipped=None, mail_delayed=None,
          wait_timeout=5,  # killing after 5 seconds if the process still runs
          stop_signal=signal.SIGTERM,  # after sending this signal
          max_lines=10,  # length of STDOU, STDERR head and tail (None for all)
          run_on_start=True,  # we may want to run the task on startup
          policy=SKIP,  # we skip the schedule if still running
          template_dir='/tmp',  # e-mail template dirs (list or string)
          stdout_logger=stdout_logger,
          stdout_level=logging.DEBUG,  # send STDOUT logs to this level
          stderr_logger=stderr_logger,
          stderr_level=logging.WARNING,  # send STDERR logs to this level
          cwd=None,  # run the command in this directory (None to keep current)
          email_limitation=True  # send only one skipped or delayed message
      ),
      Task(  # you can specify more than one task
          'catter', ('cat', 'README.rst'), '5 20,40 7-19 MON-FRI *',
          run_on_start=True
      )
  )

  tasks.start()  # blocking... the process will exit on SIGINT and SIGTERM
