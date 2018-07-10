import unittest

from . import ts
from periodtask import Task


class CronTest(unittest.TestCase):
    def test_simple_task(self):
        task = Task(
            'test1', ('ls',), '* * * * * -1526',
            run_on_start=False
        )
        task.check_for_second(ts('2018-07-10 10:15:00'))
        self.assertEqual(len(task.process_threads), 0)
