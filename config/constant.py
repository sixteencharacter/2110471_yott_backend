import os
import sys
sys.path.append(os.getcwd())
from dotenv import load_dotenv

load_dotenv(".env")

RELOAD_DIRS = [
    # "./routers",
    # "./services",
    # "./utils",
    # "./config",
    "."
]

KC_CERT_URL=os.environ.get("KC_CERT_URL")
KC_TOKEN_ENDPOINT=os.environ.get("KC_TOKEN_ENDPOINT")
KC_AUTHORIZATION_URL=os.environ.get("KC_AUTHORIZATION_URL")
KC_REFRESH_URL=os.environ.get("KC_REFRESH_URL")
KC_CLIENT_AUD=os.environ.get("KC_CLIENT_AUD")
PGSQL_URI=os.environ.get("PGSQL_URI")
PGSQL_ASYNC_URI=os.environ.get("PGSQL_ASYNC_URI")