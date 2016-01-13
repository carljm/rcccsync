#!/usr/bin/env python
from rcccsync.main import store_access_code, get_new_access_code

if __name__ == '__main__':
    store_access_code(get_new_access_code())
