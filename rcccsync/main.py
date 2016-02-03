import csv
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


def list_emails(subgroup=''):
    subgroup = subgroup.lower()
    cl = get_client()
    rows = cl.get_list_feed(config.SHEET_ID, config.WORKSHEET_ID)
    for row in rows.entry:
        email = row.get_value('emailone') or row.get_value('emailtwo')
        if email and ((not subgroup) or row.get_value(subgroup)):
            print (
                "%s %s %s <%s>" % (
                    row.get_value('title') or '',
                    row.get_value('firstname') or '',
                    row.get_value('lastname') or '',
                    email,
                )
            ).strip()


def main(subgroup=''):
    """Take CSV with firstname, lastname, email, phone; add to spreadsheet."""
    subgroup = subgroup.lower()
    cl = get_client()
    rows = cl.get_list_feed(config.SHEET_ID, config.WORKSHEET_ID)
    reader = csv.DictReader(sys.stdin)
    incoming = dict((x['email'].lower(), x) for x in reader)
    for row in rows.entry:
        data = row.to_dict()
        found = False
        for emailcol in ['emailone', 'emailtwo']:
            email = (data.get(emailcol) or '').lower()
            if email in incoming:
                print "Found %s" % email
                newdata = incoming.pop(email)
                found = True
        if found:
            update = {}
            if subgroup:
                print "  adding to %s" % subgroup
                update[subgroup] = 'X'
            field_map = {
                'cellphone': 'phone',
                'firstname': 'firstname',
                'lastname': 'lastname'
            }
            for field, newfield in field_map.items():
                if newdata[newfield] and not data.get(field):
                    print "  updating %s to %s" % (field, newdata[newfield])
                    update[field] = newdata[newfield]
            if update:
                row.from_dict(update)
                cl.update(row)
    for newrow in incoming.values():
        print "Adding %s %s <%s>" % (
            newrow['firstname'], newrow['lastname'], newrow['email'])
        row = ListEntry()
        row.set_value('firstname', newrow['firstname'])
        row.set_value('lastname', newrow['lastname'])
        row.set_value('emailone', newrow['email'])
        row.set_value('cellphone', newrow['phone'])
        if subgroup:
            row.set_value(subgroup, 'X')
        cl.add_list_entry(row, config.SHEET_ID, config.WORKSHEET_ID)


def name_and_email_to_csv():
    """Take lines like 'First Last <foo@example.com>' on stdin, output csv."""
    writer = csv.writer(sys.stdout)
    writer.writerow(['firstname', 'lastname', 'email', 'phone'])
    for row in (parse_name_and_email(x) for x in sys.stdin.xreadlines()):
        writer.writerow(list(row) + [''])


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
