import threading
from subprocess import Popen, PIPE, TimeoutExpired
import select
import logging


logger = logging.getLogger('periodtask.process_thread')


class ProcessThread(threading.Thread):
    def __init__(
        self, task_name, command, stop_signal, wait_timeout,
        formatted_sec, max_lines,
        stdout_logger, stdout_level, stderr_logger, stderr_level,
        cwd
    ):
        self.task_name = task_name
        self.command = command
        self.stop_signal = stop_signal
        self.wait_timeout = wait_timeout
        self.formatted_sec = formatted_sec
        self.max_lines = max_lines
        self.stdout_logger = stdout_logger
        self.stdout_level = stdout_level or logging.INFO
        self.stderr_logger = stderr_logger
        self.stderr_level = stderr_level or logging.INFO
        self.cwd = cwd

        self.stdout_head = []
        self.stdout_tail = []
        self.stderr_head = []
        self.stderr_tail = []

        self.returncode = None
        self.proc = None
        self.lock = threading.Lock()
        super(ProcessThread, self).__init__()

    def lines(self, head, tail):
        with self.lock:
            if tail:
                return (
                    '\n'.join(head) +
                    '\n...\n' +
                    '\n'.join(tail)
                )
            else:
                return '\n'.join(head)

    @property
    def stdout_lines(self):
        return self.lines(self.stdout_head, self.stdout_tail)

    @property
    def stderr_lines(self):
        return self.lines(self.stderr_head, self.stderr_tail)

    def read_descriptor(self, desc, head, tail, logger, level):
        data = desc.readline()
        if not data:
            return False
        else:
            data = data.rstrip('\r\n')
            if logger:
                logger.log(level, data)
            with self.lock:
                if self.max_lines is None:
                    head.append(data)
                elif self.max_lines == 0:
                    return True
                else:
                    if tail:
                        tail.append(data)
                        if len(tail) > self.max_lines:
                            tail.pop(0)
                    else:
                        head.append(data)
                        if len(head) > 2 * self.max_lines:
                            tail.extend(head[-self.max_lines:])
                            del head[self.max_lines:]
            return True

    def run(self):
        proc = self.proc = Popen(
            self.command,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            # encoding='utf-8',  # This only works 3.6 and above
            universal_newlines=True,
            start_new_session=True,
            bufsize=1,
            cwd=self.cwd,
        )

        stdout_live, stderr_live = True, True
        while stdout_live or stderr_live:
            r, w, e = select.select([proc.stdout, proc.stderr], [], [])
            if proc.stdout in r:
                stdout_live = self.read_descriptor(
                    proc.stdout,
                    self.stdout_head, self.stdout_tail,
                    self.stdout_logger, self.stdout_level
                )
            if proc.stderr in r:
                stderr_live = self.read_descriptor(
                    proc.stderr,
                    self.stderr_head, self.stderr_tail,
                    self.stdout_logger, self.stdout_level
                )

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
