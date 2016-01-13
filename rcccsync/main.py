import os
import sys

from gdata.spreadsheets.data import ListEntry

from .auth import get_authorize_url
from . import client
from . import config


def get_new_access_code():
    url = get_authorize_url()
    prompt = "Visit %s and paste access code here: " % url
    return raw_input(prompt)


def store_access_code(code):
    with open(config.ACCESS_CODE_FILE, 'w') as fh:
        fh.write(code)
    os.chmod(config.ACCESS_CODE_FILE, 0600)


def get_stored_access_code():
    with open(config.ACCESS_CODE_FILE, 'r') as fh:
        return fh.read().strip()


def get_client():
    return client.get_client(get_stored_access_code())


def main(subgroup=''):
    subgroup = subgroup.lower()
    cl = get_client()
    rows = cl.get_list_feed(config.SHEET_ID, config.WORKSHEET_ID)
    parsed = (parse_name_and_email(x) for x in sys.stdin.xreadlines())
    incoming = dict((x[2].lower(), x) for x in parsed)
    for row in rows.entry:
        data = row.to_dict()
        found = False
        for emailcol in ['emailone', 'emailtwo']:
            email = data.get(emailcol, '').lower()
            if email in incoming:
                print "Found %s" % email
                del incoming[email]
                found = True
        if found and subgroup:
            print "  adding to %s" % subgroup
            row.from_dict({subgroup: 'X'})
            cl.update(row)
    for first, last, email in incoming.values():
        print "Adding %s %s <%s>" % (first, last, email)
        row = ListEntry()
        row.set_value('firstname', first)
        row.set_value('lastname', last)
        row.set_value('emailone', email)
        if subgroup:
            row.set_value(subgroup, 'X')
        cl.add_list_entry(row, config.SHEET_ID, config.WORKSHEET_ID)


def parse_name_and_email(instr):
    """Parse combined name and email address into (first, last, email) tuple.

    E.g. for input "Some One <some@example.com>", return ('Some', 'One',
    'some@example.com').

    If given only an email address (e.g. "some@example.com") return ('', '',
    'some@example.com').

    If the name contains no spaces, consider it a first name.

    If the name contains multiple spaces, assume everything up to the first
    space is first name.

    """
    instr = instr.strip()
    if not ('<' in instr and instr.endswith('>')):
        return ('', '', instr)
    name, email = (bit.strip() for bit in instr[:-1].split('<', 1))
    try:
        fn, ln = name.split(' ', 1)
    except ValueError:
        fn, ln = name, ''
    return (fn, ln, email)
