from gdata.spreadsheets.client import SpreadsheetsClient

from . import auth


def get_client(access_code):
    return auth.authorize_client(SpreadsheetsClient(), access_code)
