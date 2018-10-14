#!/usr/bin/env python3

import signal

from periodtask import TaskList, Task


def send(subject, message, html_message=None):
    print('|%s|' % message)


tasks = TaskList(
    Task(
        'example_task',
        ('tests/task_script.py', 'e'),
        ['0 0 0'],
        run_on_start=True,
        mail_success=send,
        stop_signal=signal.SIGINT,
        max_lines=((2, 5), 3),
    )
)

tasks.start()
