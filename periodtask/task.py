import time
import logging
from datetime import datetime
import signal
import threading

import pytz
from mako.template import Template

from . import mailsender
from .process_thread import ProcessThread


logger = logging.getLogger('periodtask.task')


FAILURE_TEMPLATE = """
task: ${subproc.task_name}<br/>
started for: ${subproc.formatted_sec}<br/>
returncode: ${subproc.returncode}<br/>
stdout:<br/>
<pre>
${subproc.stdout_lines}
</pre>
stderr:<br/>
<pre>
${subproc.stderr_lines}
</pre>
"""

SUCCESS_TEMPLATE = """
task: ${subproc.task_name}<br/>
started for: ${subproc.formatted_sec}<br/>
returncode: ${subproc.returncode}<br/>
stdout:<br/>
<pre>
${subproc.stdout_lines}
</pre>
stderr:<br/>
<pre>
${subproc.stderr_lines}
</pre>
"""

SKIP_TEMPLATE = """
task running: ${subproc.task_name}<br/>
started for: ${subproc.formatted_sec}<br/>
current: ${current_sec}
stdout:<br/>
<pre>
${subproc.stdout_lines}
</pre>
stderr:<br/>
<pre>
${subproc.stderr_lines}
</pre>
"""


class Task:
    def __init__(
        self, name, command, periods,
        run_on_start=False,
        mail_success=False,
        mail_failure=False,
        mail_skipped=False,
        max_lines=50,
        stop_signal=signal.SIGTERM,
        wait_timeout=10,
        send_mail_func=mailsender.send_mail,
        from_email=None,
        recipient_list=None,
    ):
        self.name = name
        self.command = command
        self.periods = periods
        self.run_on_start = run_on_start
        self.mail_success = mail_success
        self.mail_failure = mail_failure
        self.mail_skipped = mail_skipped
        self.max_lines = max_lines
        self.stop_signal = stop_signal
        self.wait_timeout = wait_timeout
        self.send_mail_func = send_mail_func
        self.from_email = from_email
        self.recipient_list = recipient_list

        self.last_checked = None
        self.process_thread = None
        self.first_check = True
        self.sec_fmt = '%s-%s-%s %s:%s:%s (%s) (day of week: %s)'

    def check_second(self, sec):
        if self.first_check:
            self.first_check = False
            if self.run_on_start:
                return 'run_on_start'
        for period in self.periods:
            utc = datetime.utcfromtimestamp(sec).replace(tzinfo=pytz.utc)
            dt = period.timezone.normalize(utc).astimezone(period.timezone)
            isocalendar = dt.isocalendar()

            year = dt.year
            weekday = isocalendar[2]
            month = dt.month
            day = dt.day
            hour = dt.hour
            minute = dt.minute
            second = dt.second

            if (
                second in period.seconds and
                minute in period.minutes and
                hour in period.hours and
                day in period.days and
                month in period.months and
                weekday in period.weekdays and
                year in period.years
            ):
                return self.sec_fmt % (
                    year, month, day, hour, minute, second, period.timezone,
                    weekday
                )
            return False

    def start_process_thread(self, formatted_sec):
        msg = 'task %s starts process for %s' % (self.name, formatted_sec)
        logger.info(msg)
        self.process_thread = ProcessThread(
            self.name,
            self.command,
            self.stop_signal,
            self.wait_timeout,
            formatted_sec,
            self.max_lines
        )
        self.process_thread.start()

    def send_mail(self, subject, message, html_message=None):
        if self.from_email and self.recipient_list:
            self.send_mail_func(
                subject, message,
                from_email=self.from_email,
                recipient_list=self.recipient_list,
                html_message=html_message
            )
        else:
            logger.warning('from_email or recipient_list not set')

    def check_subprocess(self):
        subproc = self.process_thread
        if not subproc:
            return
        if subproc.is_alive():
            return
        retcode = subproc.returncode
        msg = 'task %s started for %s terminated with code %s'
        msg = msg % (self.name, subproc.formatted_sec, retcode)
        logger.info(msg)

        if retcode == 0:
            if self.mail_success:
                subject = 'TASK SUCCESS: %s' % self.name
                html = Template(SUCCESS_TEMPLATE, default_filters=['h'])
                html = html.render(subproc=subproc)
                self.send_mail(subject, msg, html_message=html)
        else:
            if self.mail_failure:
                subject = 'TASK FAILURE: %s' % self.name
                html = Template(FAILURE_TEMPLATE, default_filters=['h'])
                html = html.render(subproc=subproc)
                self.send_mail(subject, msg, html_message=html)

        self.process_thread = None

    def skipped(self, formatted_sec):
        msg = 'task %s skipped for %s' % (self.name, formatted_sec)
        logger.warning(msg)
        if self.mail_skipped:
            started_for = self.process_thread.formatted_sec
            subject = 'TASK SKIPPED: %s' % self.name
            msg = 'task %s started for %s still running, call for %s skipped'
            msg = msg % (self.name, started_for, formatted_sec)
            html = Template(SKIP_TEMPLATE, default_filters=['h'])
            html = html.render(
                subproc=self.process_thread,
                current_sec=formatted_sec
            )
            self.send_mail(subject, msg, html_message=html)

    def check_for_second(self, sec):
        formatted_sec = self.check_second(sec)
        if not formatted_sec:
            return
        if self.process_thread:
            self.skipped(formatted_sec)
            return
        self.start_process_thread(formatted_sec)

    def stop(self):
        if self.process_thread:
            self.process_thread.stop()
            self.process_thread.join()
            self.check_subprocess()
        for thread in threading.enumerate():
            if thread != threading.main_thread():
                thread.join()

        logger.info('task stopped')

    def start(self):
        logger.info('task %s started' % self.name)
        self.last_checked = int(time.time()) - 1
        try:
            while True:
                self.check_subprocess()
                now = int(time.time())
                for sec in range(self.last_checked + 1, now + 1):
                    self.check_for_second(sec)
                self.last_checked = now
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
