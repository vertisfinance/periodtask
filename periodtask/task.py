import time
import logging
from datetime import datetime
from subprocess import Popen, PIPE, TimeoutExpired
import signal
import threading

import pytz
from mako.template import Template

from . import mailsender


logger = logging.getLogger('periodtask.task')


FAILURE_TEMPLATE = """
task: ${task.name}<br/>
started for: ${task.process.formatted_sec}<br/>
returncode: ${task.process.returncode}<br/>
stdout:<br/>
<pre>${stdout}</pre>
stderr:<br/>
<pre>${stderr}</pre>
"""


class Period:
    def __init__(
        self,
        timezone='UTC',
        years=list(range(1900, 3000)),
        months=list(range(1, 13)),
        weeks=[],
        days=list(range(1, 32)),
        weekdays=list(range(1, 8)),  # Monday: 1, ..., Sunday: 7
        hours=list(range(0, 24)),
        minutes=list(range(0, 60, 5)),
        seconds=[0],
    ):
        self.timezone = pytz.timezone(timezone)
        self.years = years
        self.months = months
        self.weeks = weeks
        self.days = days
        self.weekdays = weekdays
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds


class Task:
    def __init__(
        self, name, command, periods,
        run_on_start=False,
        mail_success=False,
        mail_failure=False,
        mail_skipped=False,
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
        self.stop_signal = stop_signal
        self.wait_timeout = wait_timeout
        self.send_mail_func = send_mail_func
        self.from_email = from_email
        self.recipient_list = recipient_list

        self.last_checked = None
        self.process = None
        self.first_check = True
        self.sec_fmt = (
            '%s-%s-%s %s:%s:%s (%s) '
            '(ISO year: %s, week: %s, weekday: %s)')

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
            iso_year, iso_week, iso_weekday = isocalendar
            month = dt.month
            day = dt.day
            hour = dt.hour
            minute = dt.minute
            second = dt.second

            if all([
                (
                    period.weeks and
                    iso_week in period.weeks and
                    iso_year in period.years
                ) or (
                    not period.weeks and
                    year in period.years
                ),
                iso_weekday in period.weekdays,
                month in period.months,
                day in period.days,
                hour in period.hours,
                minute in period.minutes,
                second in period.seconds
            ]):
                return self.sec_fmt % (
                    year, month, day, hour, minute, second, period.timezone,
                    iso_year, iso_week, iso_weekday
                )
            return False

    def start_subprocess(self, formatted_sec):
        msg = 'task %s starts process for %s' % (self.name, formatted_sec)
        logger.info(msg)
        self.process = Popen(
            self.command,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            encoding='utf-8',
            start_new_session=True,
        )
        self.process.formatted_sec = formatted_sec

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
        subproc = self.process
        if not subproc:
            return
        retcode = subproc.poll()
        if retcode is None:
            return
        msg = 'task %s started for %s terminated with code %s'
        msg = msg % (self.name, subproc.formatted_sec, retcode)
        logger.info(msg)

        logger.debug('start communicate')
        stdout_data, stderr_data = subproc.communicate()
        logger.debug('end communicate')

        if retcode == 0:
            if self.mail_success:
                subject = 'TASK SUCCESS: %s' % self.name
                self.send_mail(subject, msg)
        else:
            if self.mail_failure:
                subject = 'TASK FAILURE: %s' % self.name
                html = Template(FAILURE_TEMPLATE, default_filters=['h'])
                html = html.render(
                    task=self,
                    stdout=stdout_data,
                    stderr=stderr_data,
                )
                self.send_mail(subject, msg, html_message=html)

        self.process = None

    def skipped(self, formatted_sec):
        msg = 'task %s skipped for %s' % (self.name, formatted_sec)
        logger.warning(msg)
        if self.mail_skipped:
            subject = 'TASK SKIPPED: %s' % self.name
            msg = 'task %s started for %s still running, call for %s skipped'
            msg = msg % (self.name, self.process.formatted_sec, formatted_sec)
            self.send_mail(subject, msg)

    def check_for_second(self, sec):
        formatted_sec = self.check_second(sec)
        if not formatted_sec:
            return
        if self.process:
            self.skipped(formatted_sec)
            return
        self.start_subprocess(formatted_sec)

    def stop(self):
        if self.process:
            logger.warning('sending %s to process' % self.stop_signal)
            self.process.send_signal(self.stop_signal)
            try:
                logger.warning('waiting for process to terminate...')
                self.process.wait(timeout=self.wait_timeout)
            except TimeoutExpired:
                logger.warning('killing the process...')
                self.process.kill()
                self.process.wait()
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
