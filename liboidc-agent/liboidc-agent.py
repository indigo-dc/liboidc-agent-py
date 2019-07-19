"""This module enables python applications to request OpenID Connect access tokens from oidc-agent"""

import os
import socket
import json


def get_token_response_by_issuer_url(issuer_url,
                                     min_valid_period=0,
                                     application_hint=None,
                                     scope=None):
    """Gets token response by issuerURL; return triple of (access_token, issuer, expires_at)"""
    return _communicate_with_sock(
        _create_token_request_issuer(issuer_url, min_valid_period,
                                     application_hint, scope))


def get_token_response(account_name,
                       min_valid_period=0,
                       application_hint=None,
                       scope=None):
    """Gets token response by account short name; return triple of (access_token, issuer,
    expires_at)"""
    return _communicate_with_sock(
        _create_token_request_account(account_name, min_valid_period,
                                      application_hint, scope))


def get_access_token(account_name,
                     min_valid_period=0,
                     application_hint=None,
                     scope=None):
    """Gets access token by account short name"""
    return get_token_response(account_name, min_valid_period, application_hint,
                              scope)


def get_access_token_by_issuer_url(issuer_url,
                                   min_valid_period=0,
                                   application_hint=None,
                                   scope=None):
    """Gets access token by issuer url"""
    return get_token_response_by_issuer_url(issuer_url, min_valid_period,
                                            application_hint, scope)


def _create_token_request(acc_iss_data, min_valid_period, application_hint,
                          scope):
    data = {'request': 'access_token'}
    data[acc_iss_data[0]] = acc_iss_data[1]
    if scope:
        data['scope'] = scope
    if application_hint:
        data['application_hint'] = application_hint
    data['min_valid_period'] = min_valid_period
    return json.dumps(data)


def _create_token_request_account(account, min_valid_period, application_hint,
                                  scope):
    return _create_token_request(('account', account), min_valid_period,
                                 application_hint, scope)


def _create_token_request_issuer(issuer, min_valid_period, application_hint,
                                 scope):
    return _create_token_request(('issuer', issuer), min_valid_period,
                                 application_hint, scope)


def _communicate_with_sock(request):
    try:
        socket_path = os.environ['OIDC_SOCK']
    except KeyError:
        raise OidcAgentConnectError('OIDC_SOCK env var not set')

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(socket_path)
    except socket.error:
        raise OidcAgentConnectError('Could not connect to oidc-agent')

    sock.sendall(request.encode('utf-8'))
    res = b''
    while True:
        part = sock.recv(4096)
        res += part
        if len(part) < 4096:
            break

    data = json.loads(res)
    if 'error' in data:
        error = data['error']
        raise OidcAgentError(error)
    return data['access_token'], data['issuer'], data['expires_at']


class OidcAgentError(Exception):
    """Basic exception for errors raised by liboidc-agent"""

    def __init__(self, message):
        super(OidcAgentError, self).__init__(message)


class OidcAgentConnectError(OidcAgentError):
    """Errors while connecting to oidc-agent"""

    def __init__(self, message):
        super(OidcAgentConnectError, self).__init__(message)


tokenresponse = get_token_response("iam", 60, "Example-Py-App")
