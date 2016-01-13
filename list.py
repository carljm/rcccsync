#!/usr/bin/env python
import sys

from rcccsync.main import list_emails

if __name__ == '__main__':
    list_emails(*sys.argv[1:])
