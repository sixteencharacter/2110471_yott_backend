import os
import sys
sys.path.append(os.getcwd())

import jwt
from jwt import PyJWKClient
from fastapi import Depends
from typing import Annotated , Optional
from fastapi import HTTPException
from config import oauth_2_scheme
import config
from .database import sessionmanager
from models import Person
from services import kc_user_cache , Cache

async def validate_access_token(
    access_token: Annotated[str, Depends(oauth_2_scheme)]
):
    url = config.KC_CERT_URL
    optional_custom_headers = {"User-agent": "yott-backend-agent"}
    print(url)
    jwks_client = PyJWKClient(url, headers=optional_custom_headers)

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(access_token)
        data = jwt.decode(
            access_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=config.KC_CLIENT_AUD,
            options={"verify_exp": True},
        )

        async with sessionmanager.session() as session:
            new_user = Person(
                family_name = data["family_name"],
                given_name = data["given_name"],
                preferred_username = data["preferred_username"],
                email = data["email"],
                uid = data["sub"]
            )
            if kc_user_cache.get(new_user.uid) is None : # if cache missed
                await session.merge(new_user)
                await session.commit()
                kc_user_cache.set(new_user.uid,True)

        return data
    except jwt.exceptions.InvalidTokenError as err:
        print(err)
        raise HTTPException(status_code=401, detail="Not authenticated")
    
async def validate_accessToken_without_raise(token : str , cache_engine : Optional[Cache] = None) :
    data , err = None , None
    try :
        data = await validate_access_token(token)
        cache_engine.set(token,data)
    except Exception as e :
        if cache_engine :
            if cache_engine.get(token) is not None:
                data = cache_engine.get(token)        
            else :
                err = e
        else : 
            err = e

    return data , err