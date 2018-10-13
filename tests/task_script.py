#!/usr/bin/env python3
import sys


for i in range(20):
    print(i)

if len(sys.argv) > 1:
    for i in range(20):
        print(i, file=sys.stderr)
