#!/usr/bin/python3
import logging
import sys
import os
import signal

from periodtask import Task, Period


stdout = logging.StreamHandler(sys.stdout)
fmt = logging.Formatter('%(levelname)s|%(name)s|%(asctime)s|%(message)s')
stdout.setFormatter(fmt)
root = logging.getLogger()
root.addHandler(stdout)
root.setLevel(getattr(logging, os.environ.get('LOG_LEVEL', 'DEBUG')))


task = Task(
    'test',
    ('/periodtask/test_script.py',),
    [
        Period(
            timezone='Europe/Budapest',
            minutes=list(range(0, 60)),
            seconds=list(range(0, 60, 5)),
        )
    ],
    mail_failure=True,
    run_on_start=True,
    wait_timeout=5,
    stop_signal=signal.SIGINT,
    from_email='richardbann@gmail.com',
    recipient_list=['richard.bann@vertis.com']
)
task.start()
