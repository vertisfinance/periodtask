#!/usr/bin/env python3
import sys


for i in range(20):
    print(i)

if len(sys.argv) == 2:
    if sys.argv[1] == 'e':
        for i in range(20):
            print(i, file=sys.stderr)
    elif sys.argv[1] == 'x':
        raise Exception('error')
