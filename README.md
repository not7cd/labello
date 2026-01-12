# Labello

Aim of this project is to create label library and control software for zebra printer and other alike.

## Development

```bash
# we are using poetry for dependency management
poetry install

# run once to create secrets
source env.sh

# run once to create database
poetry run python helpers/db_create.py

# run app in for development in virtual env
FLASK_APP=labello.web FLASK_ENV=development poetry run flask run
# or
poetry run python -m labello
```

## Deploy

```
systemctl edit helpers/labello.service
```