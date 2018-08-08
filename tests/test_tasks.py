import unittest
import time

from . import ts
from periodtask import Task, TaskList


class CronTest(unittest.TestCase):
    def test_simple_task(self):
        task = Task(
            'test1', ('ls',), '* * * * * -1526',
            run_on_start=False
        )
        task.check_for_second(ts('2018-07-10 10:15:00'))
        self.assertEqual(len(task.process_threads), 0)

    def test_send_success(self):
        tasklist = []

        def send(subject, text, html_message):
            tasklist[0]._stop(check_subprocesses=False)
            tasklist.pop()
            self.assertEqual(len(text.splitlines()), 106)

        tl = TaskList(
            Task(
                'test2', ('seq', '100', '200'), '*', run_on_start=True,
                mail_success=send
            )
        )
        tasklist.append(tl)
        tl.start()
        while tasklist:
            time.sleep(0.1)

    def test_max_lines(self):
        tasklist = []

        def send(subject, text, html_message):
            tasklist[0]._stop(check_subprocesses=False)
            tasklist.pop()
            self.assertEqual(len(text.splitlines()), 10)
            # self.assertEqual(text, '')

        tl = TaskList(
            Task(
                'test3', ('tests/task_script.py',), '*', run_on_start=True,
                mail_success=send,
                max_lines=2,
            )
        )
        tasklist.append(tl)
        tl.start()
        while tasklist:
            time.sleep(0.1)
