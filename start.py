#!/usr/bin/python3
import logging
import sys
import os
import signal

from periodtask import Task, parse_cron, send_mail


stdout = logging.StreamHandler(sys.stdout)
fmt = logging.Formatter('%(levelname)s|%(name)s|%(asctime)s|%(message)s')
stdout.setFormatter(fmt)
root = logging.getLogger()
root.addHandler(stdout)
root.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG')))


def _send_mail(subject, message, html_message=None):
    return send_mail(
        subject, message,
        from_email='richardbann@gmail.com',
        recipient_list=['richard.bann@vertis.com'],
        html_message=html_message
    )


task = Task(
    'test',
    ('/periodtask/test_script.py',),
    [parse_cron('* * * * * Europe/Budapest * */5')],
    run_on_start=True,
    mail_failure=True,
    mail_success=False,
    mail_skipped=False,
    send_mail_func=_send_mail,
    wait_timeout=5,
    max_lines=3,
    stop_signal=signal.SIGINT,
)
task.start()
