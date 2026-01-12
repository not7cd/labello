import os

APP_VERSION = "0.2.0"
APP_TITLE = "🏷️ labello"
APP_NAME = "Labello"
APP_WIKI_URL = "//forum.hsp.sh/t/-/114"
APP_REPO_URL = "//github.com/not7cd/labello"

APP_HOME_URL = os.environ.get("LABELLO_HOME_URL", "//hsp.sh")
APP_BASE_URL = os.environ.get("LABELLO_BASE_URL", "localhost:8000")

APP_IMAGES_PATH = os.environ.get("LABELLO_IMAGES_PATH", "./images/")

printer_name = os.environ.get("LABELLO_PRINTER_NAME", "Zebra_LP2824")
printer_host = os.environ.get("LABELLO_PRINTER_HOST", "localhost:631")

labels = {"protected": [1, 2, 3, 4, 5, 6, 7, 8, 9]}

SECRET_KEY = os.environ.get("LABELLO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")
