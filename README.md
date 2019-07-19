# liboidcagent

A python library for requesting OpenID Connect access tokens from
[oidc-agent](https://github.com/indigo-dc/oidc-agent).

## Usage

```python
import liboidcagent as oidc

token, issuer, expires_at = oidc.get_token_response("iam")
token, issuer, expires_at, oidc.get_token_response("iam", 60)
tokenresponse = oidc.get_token_response("iam", application_hint="Example-Py-App")
tokenresponse = oidc.get_token_response("iam", 60, "Example-Py-App")
tokenresponse = oidc.get_token_response("iam", 60, "Example-Py-App", "openid profile email")

token = oidc.get_access_token("iam", 60, "Example-Py-App")

token, issuer, expires_at = oidc.get_token_response_by_issuer("https://issuer.example.com", 60, "Example-Py-App")

token = oidc.get_access_token_by_issuer_url("https://issuer.example.com", 60, "Example-Py-App")
```


## Installation
`pip install liboidcagent`


## License
`liboidcagent` is provided under the [MIT License](https://opensource.org/licenses/MIT).

