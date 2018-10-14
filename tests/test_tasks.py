import unittest

from . import ts
from periodtask import Task, TaskList


class TaskTest(unittest.TestCase):
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
            self.assertEqual(len(text.splitlines()), 105)

        tl = TaskList(
            Task(
                'test2', ('seq', '100', '200'), '*', run_on_start=True,
                mail_success=send
            )
        )

        tasklist.append(tl)
        tl.start()

    def test_max_lines(self):
        tasklist = []

        def send(subject, text, html_message):
            tasklist[0]._stop(check_subprocesses=False)
            self.assertEqual(len(text.splitlines()), 9)

        tl = TaskList(
            Task(
                'test3', ('tests/task_script.py',), '*', run_on_start=True,
                mail_success=send,
                max_lines=2,
            )
        )

        tasklist.append(tl)
        tl.start()

    def test_skip_ok_mail_limitation(self):
        tasklist = []
        messages = {'skipped': 0, 'ok': 0}

        def send(subject, text, html_message):
            if subject.find('SKIPPED') >= 0:
                messages['skipped'] += 1
            elif subject.find('EXITED') >= 0:
                messages['ok'] += 1

            if messages['ok'] == 1:
                self.assertEqual(messages['skipped'], 1)
                tasklist[0]._stop(check_subprocesses=False)

        tl = TaskList(
            Task(
                'test4',
                ('tests/longtask.py',),
                '* *',
                mail_skipped=send,
                # email_limitation=False
            )
        )
        tasklist.append(tl)

        tl.start()

    def test_skip_mail_no_limitation(self):
        tasklist = []
        messages = [0]

        def send(subject, text, html_message):
            if subject.find('SKIPPED') >= 0:
                messages[0] += 1
            else:
                raise Exception('Should only send skipped messages')

            if messages[0] == 3:
                tasklist[0]._stop(check_subprocesses=False)

        tl = TaskList(
            Task(
                'test5',
                ('tests/longtask.py',),
                '* *',
                mail_skipped=send,
                email_limitation=False
            )
        )
        tasklist.append(tl)

        tl.start()

    def test_max_lines2(self):
        tasklist = []

        def send(subject, text, html_message):
            tasklist[0]._stop(check_subprocesses=False)
            self.assertEqual(len(text.splitlines()), 16)

        tl = TaskList(
            Task(
                'test2', ('tests/task_script.py',), '*', run_on_start=True,
                mail_success=send,
                max_lines=((1, 10), None),
            )
        )

        tasklist.append(tl)
        tl.start()

    def test_max_lines3(self):
        tasklist = []

        def send(subject, text, html_message):
            tasklist[0]._stop(check_subprocesses=False)
            self.assertEqual(len(text.splitlines()), 24)

        tl = TaskList(
            Task(
                'test3', ('tests/task_script.py',), '*', run_on_start=True,
                mail_success=send,
                max_lines=((None, 2), None),
            )
        )

        tasklist.append(tl)
        tl.start()

    def test_max_lines4(self):
        tasklist = []

        def send(subject, text, html_message):
            tasklist[0]._stop(check_subprocesses=False)
            self.assertEqual(len(text.splitlines()), 24)

        tl = TaskList(
            Task(
                'test4', ('tests/task_script.py',), '*', run_on_start=True,
                mail_success=send,
                max_lines=((2, None), None),
            )
        )

        tasklist.append(tl)
        tl.start()

    def test_max_lines5(self):
        tasklist = []

        def send(subject, text, html_message):
            tasklist[0]._stop(check_subprocesses=False)
            self.assertEqual(len(text.splitlines()), 15)

        tl = TaskList(
            Task(
                'test5', ('tests/task_script.py', 'e'), '*', run_on_start=True,
                mail_success=send,
                max_lines=((0, 1), 2),
            )
        )

        tasklist.append(tl)
        tl.start()

    def test_multi_fail(self):
        tasklist = []
        messages = {'COMPLETED': 0, 'FAILURE': 0}

        def send(subject, text, html_message):
            if subject.find('COMPLETED') >= 0:
                messages['COMPLETED'] += 1
            elif subject.find('FAILURE') >= 0:
                messages['FAILURE'] += 1
            else:
                raise Exception('Should not be here...')
            if messages['COMPLETED'] == 1:
                self.assertEqual(messages['FAILURE'], 1)
                tasklist[0]._stop(check_subprocesses=False)

        tl = TaskList(
            Task(
                'test_multi_fail',
                ('tests/errsuccess.py', 'test_multi_fail.db', '5'),
                '* *',
                mail_failure=send,
                mail_success=send,
                max_lines=0
            )
        )
        tasklist.append(tl)
        tl.start()
