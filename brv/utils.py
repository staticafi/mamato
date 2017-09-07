#!/usr/bin/env python

import sys

def err(msg):
    sys.stderr.write(msg)
    sys.stderr.write('\n')
    sys.exit(1)

def dbg(msg):
    print('[BRV-dbg] {0}'.format(msg))
