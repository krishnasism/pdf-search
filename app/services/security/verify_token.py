from settings.config import get_settings
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

token_auth_scheme = HTTPBearer()


class VerifyToken:
    """Does all the token verification using PyJWT"""

    def __init__(self, token):
        self.token = token
        self.settings = get_settings()

        # This gets the JWKS from a given URL and does processing so you can
        # use any of the keys available
        jwks_url = f"https://{self.settings.auth0_domain}/.well-known/jwks.json"
        self.jwks_client = jwt.PyJWKClient(jwks_url)

    def verify(self):
        # This gets the key id from the token
        try:
            self.signing_key = self.jwks_client.get_signing_key_from_jwt(self.token).key
        except jwt.exceptions.PyJWKClientError as error:
            return {"status": "error", "msg": error.__str__()}
        except jwt.exceptions.DecodeError as error:
            return {"status": "error", "msg": error.__str__()}

        try:
            payload = jwt.decode(
                self.token,
                self.signing_key,
                algorithms=self.settings.auth0_algorithms,
                audience=self.settings.auth0_api_audience,
                issuer=self.settings.auth0_issuer,
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        return payload


# This is the function that FastAPI will use to verify the token
def verify_token(token: str = Depends(token_auth_scheme)):
    auth_res = VerifyToken(token.credentials).verify()
    if "status" in auth_res:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return True
