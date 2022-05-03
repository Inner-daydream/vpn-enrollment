"""Provides utilities to provide Azure AD Oauth2 login"""

import flask
import msal

def ms_load_cache(session):
    """Load cache from the session"""
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def ms_save_cache(cache=None,session=None):
    """Save cache to the session"""
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def ms_build_msal_app(cache=None, authority=None,client_id=None,client_secret=None):
    """Build an instance of the app for Oauth2"""
    return msal.ConfidentialClientApplication(
        client_id, authority=authority,
        client_credential=client_secret, token_cache=cache)

def ms_build_auth_code_flow(authority=None, scopes=None,client_id=None,client_secret=None):
    """Performs authentication and redirect to url configured in Azure portal"""
    return ms_build_msal_app(
        authority=authority,
        client_id=client_id,
        client_secret=client_secret).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=flask.url_for('ms_authorized', _external=True))


def _get_token_from_cache(scope=None,authority=None,client_secret=None,client_id=None,session=None):
    """Get the token from a user previously logged in"""
    cache = ms_load_cache(session)  # This web app maintains one cache per session
    cca = ms_build_msal_app(
        cache=cache,
        authority=authority,
        client_secret=client_secret,
        client_id=client_id)
    accounts = cca.get_accounts()
    if accounts:  # So all accounts belong to the current signed-in user
        result = cca.acquire_token_silent(scope, account=accounts[0])
        ms_save_cache(cache)
        return result
