import logging
import time
import threading


logger = logging.getLogger('periodtask.tasklist')


class TaskList:
    def __init__(self, *args):
        self.tasks = args
        self.last_checked = None

    def start(self):
        logger.info('tasklist started')
        self.last_checked = int(time.time()) - 1
        try:
            while True:
                now = int(time.time())
                for task in self.tasks:
                    task.check_subprocesses()
                    for sec in range(self.last_checked + 1, now + 1):
                        task.check_for_second(sec)
                self.last_checked = now
                time.sleep(1)
        except KeyboardInterrupt:
            for task in self.tasks:
                task.stop()
            for thread in threading.enumerate():
                if thread != threading.main_thread():
                    thread.join()
