run:
    FLASK_APP=labello.web FLASK_ENV=development uv run flask run

init-db:
    @# TODO: fix import issues so no need to set PYTHONPATH
    PYTHONPATH=. uv run python helpers/db_create.py