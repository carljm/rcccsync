from gdata.gauth import OAuth2Token

from . import config


token = OAuth2Token(
    client_id=config.GOOGLE_CLIENT_ID,
    client_secret=config.GOOGLE_CLIENT_SECRET,
    scope='https://spreadsheets.google.com/feeds',
    user_agent='RCC Contacts Sync',
)


def get_authorize_url():
    return token.generate_authorize_url(
        redirect_url=config.GOOGLE_REDIRECT_URI)


def authorize_client(client, access_code):
    get_authorize_url()
    token.get_access_token(access_code)
    return token.authorize(client)
