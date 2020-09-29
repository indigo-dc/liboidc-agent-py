"""liboidc-agent - A python library for requesting OpenID Connect access tokens from oidc-agent."""

from .liboidcagent import OidcAgentError, OidcAgentRemoteError, OidcAgentConnectError, OidcAgentCryptError
from .liboidcagent import get_access_token, get_access_token_by_issuer_url
from .liboidcagent import get_token_response, get_token_response_by_issuer_url

__version__ = '0.3.0'
__author__ = 'Gabriel Zachmann'
__author_email__ = 'oidc-agent-contact@lists.kit.edu'
__all__ = []
