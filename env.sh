export LABELLO_SECRET_KEY=$(openssl rand -hex 16)

export LABELLO_BASE_URL="localhost:8000"
export LABELLO_PRINTER_NAME="Zebra_LP2824"
export LABELLO_PRINTER_HOST="localhost:631"

env | grep LABELLO_ > .env
