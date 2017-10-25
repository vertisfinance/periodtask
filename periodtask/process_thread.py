import threading
from subprocess import Popen, PIPE, TimeoutExpired
import select
import logging


logger = logging.getLogger('periodtask.process_thread')


class ProcessThread(threading.Thread):
    def __init__(
        self, task_name, command, stop_signal, wait_timeout, formatted_sec
    ):
        self.task_name = task_name
        self.command = command
        self.stop_signal = stop_signal
        self.wait_timeout = wait_timeout
        self.formatted_sec = formatted_sec
        self.stdout = []
        self.stderr = []
        self.returncode = None
        self.proc = None
        self.lock = threading.Lock()
        super(ProcessThread, self).__init__()

    @property
    def stdout_lines(self):
        with self.lock:
            return ''.join(self.stdout)

    @property
    def stderr_lines(self):
        with self.lock:
            return ''.join(self.stderr)

    def run(self):
        proc = self.proc = Popen(
            self.command,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            encoding='utf-8',
            start_new_session=True,
            bufsize=0
        )

        stdout_live, stderr_live = True, True
        while stdout_live or stderr_live:
            r, w, e = select.select([proc.stdout, proc.stderr], [], [])
            if proc.stdout in r:
                data = proc.stdout.readlines()
                if not data:
                    stdout_live = False
                else:
                    with self.lock:
                        self.stdout += data
            if proc.stderr in r:
                data = proc.stderr.readlines()
                if not data:
                    stderr_live = False
                else:
                    with self.lock:
                        self.stderr += data

        proc.wait()
        self.returncode = proc.returncode

    def stop(self):
        logger.warning('sending %s to process' % self.stop_signal)
        self.proc.send_signal(self.stop_signal)
        try:
            logger.warning('waiting for process to terminate...')
            self.proc.wait(timeout=self.wait_timeout)
        except TimeoutExpired:
            logger.warning('killing the process...')
            self.proc.kill()
            self.proc.wait()
