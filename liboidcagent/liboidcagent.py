"""This module enables python applications to request OpenID Connect
access tokens from oidc-agent"""

import socket
import base64
import os
import json
import binascii

import nacl.exceptions
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import Base64Encoder

from future.standard_library import install_aliases
install_aliases()
from urllib.parse import urlsplit


class OidcAgentError(Exception):
    """Basic exception for errors raised by liboidc-agent"""

    def __init__(self, message):
        super(OidcAgentError, self).__init__(message)


class OidcAgentRemoteError(OidcAgentError):
    """Basic exception for errors raised by liboidc-agent"""

    def __init__(self, message):
        super(OidcAgentRemoteError, self).__init__(message)


class OidcAgentConnectError(OidcAgentError):
    """Errors while connecting to oidc-agent"""

    def __init__(self, message):
        super(OidcAgentConnectError, self).__init__(message)


class OidcAgentCryptError(OidcAgentError):
    """Errors through de-/en-cryption"""

    def __init__(self, message):
        super(OidcAgentCryptError, self).__init__(message)


def _init_comm(remote):
    env_var = 'OIDC_REMOTE_SOCK' if remote else 'OIDC_SOCK'
    try:
        socket_path = os.environ[env_var]
    except KeyError:
        raise OidcAgentConnectError('{} env var not set'.format(env_var))

    sock = socket.socket(socket.AF_INET if remote else socket.AF_UNIX,
                         socket.SOCK_STREAM)
    if remote:
        split = urlsplit('//' + socket_path)
        host = split.hostname
        port = split.port if split.port else 42424
    try:
        if remote:
            sock.connect((host, port))
        else:
            sock.connect(socket_path)
    except socket.error as err:
        raise OidcAgentConnectError(
            'Could not connect to oidc-agent: {}'.format(err))
    return sock


def _comm_with_sock(sock, request):
    sock.sendall(request.encode('utf-8'))
    res = b''
    while True:
        part = sock.recv(4096)
        res += part
        if len(part) < 4096:
            break
    return res.decode("utf-8")


def _init_keys(sock):
    client_sk = PrivateKey.generate()
    client_pk = client_sk.public_key
    client_pk_base64 = client_pk.encode(Base64Encoder).decode('utf8')
    server_pk_base64 = _comm_with_sock(sock, client_pk_base64)
    try:
        server_pk = PublicKey(base64.b64decode(server_pk_base64))
    except binascii.Error:
        raise OidcAgentCryptError("Received malformed public key")
    return client_sk, client_pk, server_pk


def _encrypt_msg(msg, server_pk, client_sk):
    try:
        box = Box(client_sk, server_pk)
    except nacl.exceptions.TypeError:
        raise OidcAgentCryptError("Malformed encryption key")
    encrypted = box.encrypt(msg.encode('utf-8'), encoder=Base64Encoder)
    return "{}:{}:{}".format(
        len(msg), encrypted.nonce.decode('utf-8'),
        encrypted.ciphertext.decode('utf-8'))


def _decrypt_msg(crypt, server_pk, client_sk):
    split = crypt.split(":")
    try:
        nonce = base64.b64decode(split[1])
        cipher = base64.b64decode(split[2])
    except (IndexError, TypeError, binascii.Error):
        raise OidcAgentCryptError("Malformed cipher")
    box = Box(client_sk, server_pk)
    plain = box.decrypt(cipher, nonce)
    return plain.decode('utf-8')


def _is_json(myjson):
    try:
        _ = json.loads(myjson)
    except ValueError:
        return False
    return True


def _communicate_encrypted(remote, request):
    try:
        sock = _init_comm(remote)
        csk, _, spk = _init_keys(sock)
        encrypted_msg = _encrypt_msg(request, spk, csk)
        encrypted_res = _comm_with_sock(sock, encrypted_msg)
        if _is_json(encrypted_res):
            # response not encrypted
            return encrypted_res
        return _decrypt_msg(encrypted_res, spk, csk)
    except nacl.exceptions.CryptoError as err:
        raise OidcAgentCryptError("Crypto error: {}".format(err))


def _get_data_from_request(remote, request):
    res = _communicate_encrypted(remote, request)
    data = json.loads(res)
    if 'error' in data:
        error = data['error']
        if remote:
            raise OidcAgentRemoteError(error)
        else:
            raise OidcAgentError(error)
    return data['access_token'], data['issuer'], data['expires_at']


def _create_token_request(acc_iss_data, min_valid_period, application_hint,
                          scope, audience):
    data = {'request': 'access_token'}
    data[acc_iss_data[0]] = acc_iss_data[1]
    if scope:
        data['scope'] = scope
    if application_hint:
        data['application_hint'] = application_hint
    if audience:
        data['audience'] = audience
    data['min_valid_period'] = min_valid_period
    return json.dumps(data)


def _create_token_request_account(account, min_valid_period, application_hint,
                                  scope, audience):
    return _create_token_request(('account', account), min_valid_period,
                                 application_hint, scope, audience)


def _create_token_request_issuer(issuer, min_valid_period, application_hint,
                                 scope, audience):
    return _create_token_request(('issuer', issuer), min_valid_period,
                                 application_hint, scope, audience)


def get_token_response_by_issuer_url(issuer_url,
                                     min_valid_period=0,
                                     application_hint=None,
                                     scope=None,
                                     audience=None):
    """Gets token response by issuerURL; return triple of (access_token, issuer, expires_at)"""
    return _get_data_from_request(
        False,
        _create_token_request_issuer(issuer_url, min_valid_period,
                                     application_hint, scope, audience))


def get_token_response(account_name,
                       min_valid_period=0,
                       application_hint=None,
                       scope=None,
                       audience=None):
    """Gets token response by account short name; return triple of (access_token, issuer,
    expires_at)"""
    request = _create_token_request_account(account_name, min_valid_period,
                                            application_hint, scope, audience)
    try:
        return _get_data_from_request(False, request)
    except OidcAgentError as err:
        if str(err) == "No account configured with that short name" or str(
                err).startswith("Could not connect to oidc-agent") or str(
                    err) == "OIDC_SOCK env var not set":
            return _get_data_from_request(True, request)
        raise


def get_access_token(account_name,
                     min_valid_period=0,
                     application_hint=None,
                     scope=None,
                     audience=None):
    """Gets access token by account short name"""
    return get_token_response(account_name, min_valid_period, application_hint,
                              scope, audience)[0]


def get_access_token_by_issuer_url(issuer_url,
                                   min_valid_period=0,
                                   application_hint=None,
                                   scope=None,
                                   audience=None):
    """Gets access token by issuer url"""
    return get_token_response_by_issuer_url(
        issuer_url, min_valid_period, application_hint, scope, audience)[0]
