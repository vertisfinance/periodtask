#!/usr/bin/env python3

import time

for i in range(22):
    if i % 10 == 9:
        print(i)
    else:
        print(i, end='')
    time.sleep(1.5)
