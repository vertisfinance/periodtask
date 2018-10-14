#!/usr/bin/env python3
import sys
import os


filepath = os.path.join('/tmp', sys.argv[1])
errcnt = int(sys.argv[2])


try:
    with open(filepath, 'r') as f:
        cnt = int(f.read())
except FileNotFoundError:
    cnt = 0


if cnt == errcnt:
    print('ok')
    os.remove(filepath)
else:
    cnt += 1
    with open(filepath, 'w') as f:
        f.write(str(cnt))
    raise Exception('error')
