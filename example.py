#!/usr/bin/env python3

import logging
import os

from periodtask import TaskList, Task, Period
from periodtask.mailsender import MailSender


logging.basicConfig(level=logging.INFO)

send_success = MailSender(
    os.environ.get('EMAIL_HOST'),
    int(os.environ.get('EMAIL_PORT')),
    os.environ.get('EMAIL_FROM'),
    os.environ.get('EMAIL_RECIPIENT'),
).send_mail

tasks = TaskList(
    Task(
        name='ls',
        command=('ls', '-al'),
        periods='* * * * * Europe/Budapest * 0',
        run_on_start=True,
        mail_success=True,
        send_mail_func=send_success,
    ),
    Task(
        name='cat',
        command=('cat', 'README.rst'),
        periods=(
            '* * * * * Europe/Budapest * 0',
            Period(
                minutes=list(range(0, 60, 5)),
                hours=list(range(0, 24)),
                days=list(range(1, 32)),
                months=list(range(1, 13)),
                weekdays=list(range(1, 8)),  # Monday: 1, ..., Sunday: 7
                timezone='UTC',
                years=list(range(1900, 3000)),
                seconds=[0],
            )
        ),
        mail_success=send_success,
    )
)

tasks.start()
