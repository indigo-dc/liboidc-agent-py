# liboidcagent

A python library for requesting OpenID Connect access tokens from
[oidc-agent](https://github.com/indigo-dc/oidc-agent).

## Usage

```python
import liboidcagent as agent

token, issuer, expires_at = agent.get_token_response("iam")
token, issuer, expires_at = agent.get_token_response("iam", 60)

tokenresponse = agent.get_token_response("iam", application_hint="Example-Py-App")
tokenresponse = agent.get_token_response("iam", 60, "Example-Py-App")
tokenresponse = agent.get_token_response("iam", 60, "Example-Py-App", "openid profile email")
tokenresponse = agent.get_token_response("iam", 60, "Example-Py-App", "openid profile email", "foo bar")

token = agent.get_access_token("iam", 60, "Example-Py-App")

token, issuer, expires_at = agent.get_token_response_by_issuer_url("https://issuer.example.com", 60, "Example-Py-App")

token = agent.get_access_token_by_issuer_url("https://issuer.example.com", 60, "Example-Py-App")
```

## Installation
`pip install liboidcagent`


## License
`liboidcagent` is provided under the [MIT License](https://opensource.org/licenses/MIT).

