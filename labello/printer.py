import subprocess
import tempfile
import logging
from labello import settings

logger = logging.getLogger(__name__)


def get_status(printer=""):
    p = subprocess.Popen(args=["lpstat", "-h", settings.printer_host, "-p", printer], stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b""):
        if printer in line.decode():
            return line.decode()
    return "failed to get status"


def send_raw(data, printer):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".epl") as fp:
        fp.write(data.encode("ISO-8859-1"))  # magic encode
        fp.write("\n\n".encode())
        command = "lp -h {} -d {} -o raw {}".format(settings.printer_host, printer, fp.name)
    logger.debug(command)
    res = subprocess.call(command, shell=True)
    return res
