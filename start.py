#!/usr/bin/python3
import logging
import sys

from periodtask import Task


stdout = logging.StreamHandler(sys.stdout)
fmt = logging.Formatter('%(levelname)s|%(name)s|%(asctime)s|%(message)s')
stdout.setFormatter(fmt)
root = logging.getLogger()
root.addHandler(stdout)
root.setLevel(logging.DEBUG)


task = Task()
task.start()
