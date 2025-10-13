from fastapi.security import OAuth2AuthorizationCodeBearer
import config

oauth_2_scheme = OAuth2AuthorizationCodeBearer(
    tokenUrl=config.KC_TOKEN_ENDPOINT,
    authorizationUrl=config.KC_AUTHORIZATION_URL,
    refreshUrl=config.KC_REFRESH_URL
)