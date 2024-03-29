import os

APP_VERSION = "0.1.0"

APP_TITLE = "🏷️ labello"
APP_NAME = "Labello"

APP_BASE_URL = "banana.at.hsp.net.pl:8000"

APP_HOME_URL = "//hsp.sh"
APP_WIKI_URL = "//wiki.hsp.sh/labello"
APP_REPO_URL = "//github.com/hspsh/labello"

APP_IMAGES_PATH = "./images/"

printer_name = "Zebra_LP2824"

labels = {"protected": [1, 2, 3, 4, 5, 6, 7, 8, 9]}

SECRET_KEY = os.environ["APP_SECRET_KEY"]
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")
