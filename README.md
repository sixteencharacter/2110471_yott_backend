# 2110471_yott_backend
YOTT ! : YOTT : Ye Olde Tongue Twister

Yott Backend

This repository contains the backend for the Yott project. It uses Docker Compose to run a local Keycloak server (preconfigured) and a PostgreSQL database.

## Prerequisites (First time installation)

- Docker and Docker Compose installed on your machine.
- Download the preconfigured Keycloak zip from the provided Google Drive link: <ask your pal>

	After downloading, extract the zip and place the extracted `keycloak` folder at the root of this repository (so the path will be `./keycloak`). The repository expects a preconfigured Keycloak directory with `conf/`, `data/`, and `themes/` subfolders.

	The folder structure should look like this at the repository root:

	- docker-compose.yml
	- keycloak/
		- conf/
		- data/
		- themes/

	Note: The repository already contains a `keycloak` directory with sample subfolders. Replace or overwrite it with the extracted preconfigured Keycloak folder from the Google Drive zip.
- Download the .env file from <ask your pal> and place it in the root directory of the folder
- Install python modules with `pip install -r requirements.txt`
- Run main.py with `python main.py`

## Update Database
1. after fixing any db model you should commit to db using 
`alembic revision --autogenerate -m "commit msg"` then do second step
2. run the scripts `alembic upgrade head` to sync the database with the schema

## Quick start

1. Ensure the `keycloak` folder (extracted from the Google Drive zip) is placed at the repository root as described in Prerequisites.
2. From the repository root, build and start services:

```bash
docker compose up -d --build
```

## Security reminder

The `docker-compose.yml` included in this repository uses simple passwords for local development. Do not use these credentials in production.
