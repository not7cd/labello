export LABELLO_SECRET_KEY=$(openssl rand -hex 16)

export LABELLO_BASE_URL="localhost:8000"
export LABELLO_PRINTER_NAME="Zebra_LP2824"
export LABELLO_PRINTER_HOST="localhost:631"

# export LABELLO_PRINTER_TYPE="device"
# export LABELLO_PRINTER_DEVICE="/dev/usb/lp0"

# export LABELLO_PRINTER_TYPE="dummy"

env | grep LABELLO_ > .env
