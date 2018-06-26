import logging
from datetime import datetime
import signal
import os

import pytz
from mako.lookup import TemplateLookup

from .process_thread import ProcessThread
from .periods import parse_period


logger = logging.getLogger('periodtask.task')
(SKIP, DELAY, RUN) = (0, 1, 2)


base_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(base_dir, 'templates')


class Task:
    def __init__(
        self, name, command, periods,
        run_on_start=False,
        mail_success=False,
        mail_failure=False,
        mail_skipped=False,
        mail_delayed=False,
        send_mail_func=None,
        wait_timeout=10,
        max_lines=50,
        stop_signal=signal.SIGTERM,
        policy=SKIP,
        template_dir=template_dir
    ):
        if not isinstance(periods, list) and not isinstance(periods, tuple):
            periods = [periods]
        self.periods = [parse_period(x) for x in periods]

        self.name = name
        self.command = command
        self.run_on_start = run_on_start
        self.mail_success = mail_success
        self.mail_failure = mail_failure
        self.mail_skipped = mail_skipped
        self.mail_delayed = mail_delayed
        self.send_mail_func = send_mail_func
        self.wait_timeout = wait_timeout
        self.max_lines = max_lines
        self.stop_signal = stop_signal
        self.policy = policy
        self.template_lookup = TemplateLookup(
            directories=[template_dir], default_filters=['h']
        )

        self.process_threads = []
        self.first_check = True
        self.sec_fmt = (
            '{:4}-{:0>2}-{:0>2} {:0>2}:{:0>2}:{:0>2} ({}) (day of week: {})'
        )
        self.delay_queue = []

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
                return self.sec_fmt.format(
                    year, month, day, hour, minute, second, period.timezone,
                    weekday
                )
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
            self.max_lines
        )
        self.process_threads.append(thrd)
        thrd.start()

    def send_mail(self, subject, message, html_message=None):
        if callable(self.send_mail_func):
            self.send_mail_func(
                subject, message, html_message=html_message)
        else:
            logger.warning('task.send_mail_func is not callable')

    def send_mail_template(
        self, subject_template, text_template, html_template, **kwargs
    ):
        get_template = self.template_lookup.get_template
        subject = get_template(subject_template)
        subject = subject.render(**kwargs)
        subject = ''.join(subject.splitlines())
        text = get_template(text_template)
        text = text.render(**kwargs)
        html = get_template(html_template)
        html = html.render(**kwargs)
        self.send_mail(subject, text, html_message=html)

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
                    self.send_mail_template(
                        'success_subject.txt',
                        'success.txt',
                        'success.html',
                        subproc=subproc
                    )
            else:
                if self.mail_failure:
                    self.send_mail_template(
                        'failure_subject.txt',
                        'failure.txt',
                        'failure.html',
                        subproc=subproc
                    )

        self.process_threads = new_process_threads

    def skipped_or_delayed(self, formatted_sec, typ='skipped'):
        msg = 'task %s %s for %s' % (self.name, typ, formatted_sec)
        logger.warning(msg)
        if getattr(self, 'mail_%s' % typ):
            self.send_mail_template(
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
                if formatted_sec:
                    self.skipped_or_delayed(self.delay_queue.pop(0))
                return
            elif self.policy == DELAY:
                if formatted_sec:
                    self.skipped_or_delayed(formatted_sec, typ='delayed')
                return

        if self.delay_queue:
            self.start_process_thread(self.delay_queue.pop(0))

    def stop(self):
        if self.process_threads:
            for proc in self.process_threads:
                proc.stop()
                proc.join()
            self.check_subprocesses()
        logger.info('task stopped: %s' % self.name)
