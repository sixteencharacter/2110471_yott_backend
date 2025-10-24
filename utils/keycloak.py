import os
import sys
sys.path.append(os.getcwd())

import jwt
from jwt import PyJWKClient , InvalidTokenError
from fastapi import Depends
from typing import Annotated , Optional
from fastapi import HTTPException
from config import oauth_2_scheme
import config
from .database import sessionmanager
from models import Person
from services import kc_user_cache , Cache
from sqlalchemy import select

async def validate_access_token(
    access_token: Annotated[str, Depends(oauth_2_scheme)]
):
    url = config.KC_CERT_URL if config.KC_CERT_URL is not None else "www.google.com"
    optional_custom_headers = {"User-agent": "yott-backend-agent"}
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
            existing_user = (await session.get(Person,new_user.uid))

            if kc_user_cache.get(new_user.uid) is None : # if cache missed
                if existing_user is not None:
                    existing_user.family_name = new_user.family_name
                    existing_user.given_name = new_user.given_name
                    existing_user.preferred_username = new_user.preferred_username
                    existing_user.email = new_user.email
                    await session.commit()
                else :
                    session.add(new_user)
                    await session.commit()
                    await session.refresh(new_user)

                kc_user_cache.set(new_user.uid,True)
        return data
    except InvalidTokenError as err:
        print(err)
        raise HTTPException(status_code=401, detail="Not authenticated")
    # except Exception as e :
    #     print(e)

async def validate_accessToken_without_raise(token : str , cache_engine : Optional[Cache] = None) :
    data , err = None , None
    try :
        data = await validate_access_token(token)
        if cache_engine is not None :
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
