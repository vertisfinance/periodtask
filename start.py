#!/usr/bin/python3
import logging
import sys
import os
import signal

from periodtask import TaskList, Task, send_mail, DELAY


stdout = logging.StreamHandler(sys.stdout)
fmt = logging.Formatter('%(levelname)s|%(name)s|%(asctime)s|%(message)s')
stdout.setFormatter(fmt)
root = logging.getLogger()
root.addHandler(stdout)
root.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG')))


def _send_mail(subject, message, html_message=None):
    return send_mail(
        subject, message,
        from_email='richard.bann@vertis.com',
        recipient_list=['richard.bann@vertis.com'],
        html_message=html_message
    )


tasklist = TaskList(
    Task(
        name='test',
        command=('/periodtask/test_script.py',),
        periods=[
            '* * * * * Europe/Budapest * 30',
        ],
        # mail_failure=True,
        # mail_success=True,
        # mail_delayed=True,
        send_mail_func=_send_mail,
        wait_timeout=5,
        max_lines=5,
        stop_signal=signal.SIGINT,
        policy=DELAY,
        stdout_level=logging.DEBUG
    ),
    Task(
        name='ls_dev',
        command=('ls', '-al'),
        periods='*',
        # run_on_start=True,
        # mail_failure=True,
        # mail_success=True,
        # mail_delayed=True,
        send_mail_func=_send_mail,
        wait_timeout=5,
        max_lines=None,
        stop_signal=signal.SIGINT,
        policy=DELAY
    )
)

tasklist.start()
