#!/usr/bin/env python


def err(msg):
    import sys

    sys.stderr.write(msg)
    sys.stderr.write('\n')
    sys.stderr.flush()
    sys.exit(1)

def dbg(msg):
    print('[BRV-dbg] {0}'.format(msg))
