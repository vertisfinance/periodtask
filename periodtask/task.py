import logging
import signal
import os

from mako.lookup import TemplateLookup

from .process_thread import ProcessThread
from .periods import Period


logger = logging.getLogger('periodtask.task')
(SKIP, DELAY, RUN) = (0, 1, 2)


base_dir = os.path.dirname(os.path.realpath(__file__))
default_template_dir = os.path.join(base_dir, 'templates')


class Task:
    """
    Represents a task to schedule.

    :param str name: The name of the task, will apear in logs and emails.
    :param tuple command: See ``args`` param of the `Popen constructor
      <https://docs.python.org/3/library/subprocess.html#subprocess.Popen>`_.
    :param list/str periods: A cron expression (str) or a list of them. See
      :doc:`cronref` for more information. By default (when set to an empyt
      string) this will be equivalent to ``0 */5 * * * * UTC``.
    :param bool run_on_start: Indicates weather the task should run when the
      scheduler starts no matter what was given in ``periods``. Useful for
      manually testing the task.
    :param func/bool mail_success: If set to a truthy value an email will be
      sent after the task run successfully. If this is a function, this
      function will be used to send out the email (if **send_mail_func** does
      not override it). The signature of the function is

      .. code-block:: python

        def send_mail(subject, message, html_message=None)
    :param func/bool mail_failure: Controls emails sent when the task fails.
      Otherwise it is the same as **mail_success**.
    :param func/bool mail_skipped: Controls emails sent when the task is
      skipped due to the defined **policy**.
    :param func/bool mail_deleyed: Controls emails sent when the task is
      delayed due to the defined **policy**.
    :param func send_mail_func: If set, this must be a function. This function
      will be used to send emails, no matter what was set in **mail_...**
      params.
    :param number wait_timeout: After sending **stop_signal** to the task
      process, we wait this many seconds for the process to stop. If the
      timeout expires, we kill the process.
    :param int/tuple max_lines: STDOUT and STDERR are collected from the task
      process. To avoid haevy memory usage we only store this many lines in
      memory. More precisely STDOUT head and tail, STDERR head and tail are
      list of lines. This parameter controls the maximum length of these lists.

      examples:

        ==================== ==== ==== ==== ====
        parameter            stdout    stderr
        -------------------- --------- ---------
        value                head tail head tail
        ==================== ==== ==== ==== ====
        ``2``                2    2    2    2
        ``(2, 3)``           2    2    3    3
        ``(10, (2,3))``      10   10   2    3
        ``((1, 2), (3, 4))`` 1    2    3    4
        ==================== ==== ==== ==== ====

    :param int stop_signal: This signal will be sent to the task process when
      we want to stop it gracefully.
    :param int policy: Available values are ``periodtask.SKIP``,
      ``periodtask.DELAY`` and ``periodtask.RUN``.

      **SKIP**
        If a process is (still) running and the task is scheduled, this new
        process will be skipped. If requested, an email will be sent.

      **DELAY**
        If a process is (still) running and the task is scheduled, this new
        process will be delayed and will run immediatelly when the actual
        process terminates. If requested, an email will be sent.

      **RUN**
        Tasks will always run when scheduled.

    :param list/str template_dir: Directories to look for email templates in.
    :param logging.logger stdout_logger: The logger to use for the STDOUT of
      the task process.
    :param int stdout_level: The STDOUT of the task process will be logged to
      this level.
    :param logging.logger stderr_logger: The logger to use for the STDERR of
      the task process.
    :param int stderr_level: The STDERR of the task process will be logged to
      this level.
    :param str cwd: The task process will run with ``cwd`` as the working
      directory. See the `Popen constructor
      <https://docs.python.org/3/library/subprocess.html#subprocess.Popen>`_.
    :param bool email_limitation: If ``True``, only one ``skip`` or ``delay``
      email will be sent. When the blocking process terminates, an extra
      email will be sent using the ``mail_skipped`` or ``mail_delayed``
      functions.
    :param bool failure_email_limitation: To disable consecutive failure
      emails this param should be set to ``True``. If left ``None``, the
      value of this param is derived from ``email_limitation``.
    """
    def __init__(
        self, name, command,
        periods='',
        run_on_start=False,
        mail_success=None,
        mail_failure=None,
        mail_skipped=None,
        mail_delayed=None,
        send_mail_func=None,
        wait_timeout=10,
        max_lines=50,
        stop_signal=signal.SIGTERM,
        policy=SKIP,
        template_dir=[],
        stdout_logger=logging.getLogger('periodtask.stdout'),
        stdout_level=logging.INFO,
        stderr_logger=logging.getLogger('periodtask.stderr'),
        stderr_level=logging.INFO,
        cwd=None,
        email_limitation=True,
        failure_email_limitation=None
    ):
        if not isinstance(periods, list) and not isinstance(periods, tuple):
            periods = [periods]
        # self.periods = [parse_period(x) for x in periods]
        self.periods = [Period(x) for x in periods]

        self.name = name
        self.command = command
        self.run_on_start = run_on_start
        self.mail_success = mail_success
        self.mail_failure = mail_failure
        self.mail_skipped = mail_skipped
        self.mail_delayed = mail_delayed

        if mail_success and send_mail_func:
            self.mail_success = send_mail_func
        if mail_failure and send_mail_func:
            self.mail_failure = send_mail_func
        if mail_skipped and send_mail_func:
            self.mail_skipped = send_mail_func
        if mail_delayed and send_mail_func:
            self.mail_delayed = send_mail_func

        self.wait_timeout = wait_timeout
        self.max_lines = max_lines
        self.stop_signal = stop_signal
        self.policy = policy
        if isinstance(template_dir, list):
            template_dir = template_dir + [default_template_dir]
        else:
            template_dir = [template_dir] + [default_template_dir]
        self.template_lookup = TemplateLookup(
            directories=template_dir, default_filters=['h']
        )
        self.stdout_logger = stdout_logger
        self.stdout_level = stdout_level
        self.stderr_logger = stderr_logger
        self.stderr_level = stderr_level
        self.cwd = cwd
        self.email_limitation = email_limitation
        self.failure_email_limitation = failure_email_limitation
        if self.failure_email_limitation is None:
            self.failure_email_limitation = self.email_limitation

        self.process_threads = []
        self.first_check = True
        self.delay_queue = []
        self.email_limitation_active = False
        self.fail_mail_sent = False

    def check_second(self, sec):
        if self.first_check:
            self.first_check = False
            if self.run_on_start:
                return 'START'
        for period in self.periods:
            chk = period._check(sec)
            if chk:
                return chk
        return False

    def start_process_thread(self, formatted_sec):
        msg = 'task %s starts process for %s' % (self.name, formatted_sec)
        logger.info(msg)
        thrd = ProcessThread(
            self.name,
            self.command,
            self.stop_signal,
            self.wait_timeout,
            formatted_sec,
            self.max_lines,
            self.stdout_logger,
            self.stdout_level,
            self.stderr_logger,
            self.stderr_level,
            self.cwd,
        )
        self.process_threads.append(thrd)
        thrd.start()

    def send_mail_template(
        self, send_func,
        subject_template, text_template, html_template, **kwargs
    ):
        get_template = self.template_lookup.get_template
        subject = get_template(subject_template)
        subject = subject.render(**kwargs)
        subject = ''.join(subject.splitlines())
        text = get_template(text_template)
        text = text.render(**kwargs)
        html = get_template(html_template)
        html = html.render(**kwargs)
        send_func(subject, text, html_message=html)

    def check_subprocesses(self):
        if not self.process_threads:
            return

        new_process_threads = []
        for subproc in self.process_threads:
            if subproc.is_alive():
                new_process_threads.append(subproc)
                continue
            retcode = subproc.returncode
            msg = 'task %s started for %s terminated with code %s'
            msg = msg % (self.name, subproc.formatted_sec, retcode)
            logger.info(msg)

            if retcode == 0:
                if self.mail_success:
                    self.fail_mail_sent = False
                    self.send_mail_template(
                        self.mail_success,
                        'success_subject.txt',
                        'success.txt',
                        'success.html',
                        subproc=subproc
                    )
            else:
                if self.mail_failure:
                    if (
                        not self.failure_email_limitation or
                        not self.fail_mail_sent
                    ):
                        self.fail_mail_sent = True
                        self.send_mail_template(
                            self.mail_failure,
                            'failure_subject.txt',
                            'failure.txt',
                            'failure.html',
                            subproc=subproc
                        )

            # If we have sent out a skipped or delayed email, we have to
            # send an ok email here
            func = None
            if self.email_limitation_active:
                self.email_limitation_active = False
                if self.policy == SKIP:
                    func = self.mail_skipped
                elif self.policy == DELAY:
                    func = self.mail_delayed

            if func:
                self.send_mail_template(
                    func,
                    'ok_subject.txt',
                    'ok.txt',
                    'ok.html',
                    subproc=subproc
                )

        self.process_threads = new_process_threads

    def skipped_or_delayed(self, formatted_sec, typ='skipped'):
        if getattr(self, 'mail_%s' % typ):
            self.send_mail_template(
                getattr(self, 'mail_%s' % typ),
                '%s_subject.txt' % typ,
                '%s.txt' % typ,
                '%s.html' % typ,
                running=self.process_threads,
                current_sec=formatted_sec,
                task_name=self.name,
                delay_queue=self.delay_queue
            )

    def check_for_second(self, sec):
        formatted_sec = self.check_second(sec)
        if formatted_sec:
            self.delay_queue.append(formatted_sec)

        if self.process_threads:
            if self.policy == SKIP:
                if not formatted_sec:
                    return

                msg = 'task %s %s for %s' % (
                    self.name, 'skipped', formatted_sec
                )
                logger.warning(msg)

                if not self.email_limitation_active:
                    self.skipped_or_delayed(formatted_sec)
                    self.delay_queue.pop(0)
                    if self.email_limitation:
                        self.email_limitation_active = True
                return
            elif self.policy == DELAY:
                if not formatted_sec:
                    return

                msg = 'task %s %s for %s' % (
                    self.name, 'delayed', formatted_sec
                )
                logger.warning(msg)

                if not self.email_limitation_active:
                    self.skipped_or_delayed(formatted_sec, typ='delayed')
                    if self.email_limitation:
                        self.email_limitation_active = True
                return

        if self.delay_queue:
            self.start_process_thread(self.delay_queue.pop(0))
            return True

    def stop(self, check_subprocesses=True):
        if self.process_threads:
            for proc in self.process_threads:
                proc.stop()
                proc.join()
            if check_subprocesses:
                self.check_subprocesses()
        logger.info('task stopped: %s' % self.name)
