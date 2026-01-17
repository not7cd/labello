import os
import subprocess
import tempfile
import logging
from labello import settings

logger = logging.getLogger(__name__)


class Printer:
    def get_status(self) -> str:
        raise NotImplementedError()

    def get_state(self) -> str:
        status = self.get_status().lower()
        if "error" in status or "not found" in status or "failed" in status:
            return "error"
        if "printing" in status:
            return "printing"
        if "idle" in status or "exists" in status or "ready" in status:
            return "idle"
        return "error"

    def send_raw(self, data: str) -> int:
        raise NotImplementedError()


class CUPSPrinter(Printer):
    def __init__(self, host, name):
        self.host = host
        self.name = name

    def get_status(self):
        p = subprocess.Popen(
            args=["lpstat", "-h", self.host, "-p", self.name], stdout=subprocess.PIPE
        )
        for line in iter(p.stdout.readline, b""):
            if self.name in line.decode():
                return line.decode().strip()
        return "failed to get status"

    def send_raw(self, data: str):
        raw_data = data.encode("ISO-8859-1") + b"\n\n"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".epl") as fp:
            fp.write(raw_data)
            command = "lp -h {} -d {} -o raw {}".format(self.host, self.name, fp.name)
        logger.debug(command)
        res = subprocess.call(command, shell=True)
        return res


class DevicePrinter(Printer):
    def __init__(self, device_path):
        self.device_path = device_path

    def get_status(self):
        if os.path.exists(self.device_path):
            return "Device {} exists".format(self.device_path)
        else:
            return "Device {} not found".format(self.device_path)

    def send_raw(self, data: str):
        raw_data = data.encode("ISO-8859-1") + b"\n\n"
        logger.debug("Sending raw data to device %s", self.device_path)
        try:
            with open(self.device_path, "wb") as f:
                f.write(raw_data)
            return 0
        except Exception as e:
            logger.error("Failed to write to device %s: %s", self.device_path, e)
            return 1


class DummyPrinter(Printer):
    def get_status(self):
        return "Dummy printer ready"

    def send_raw(self, data: str):
        logger.info("Dummy printer received %d bytes of data", len(data))
        logger.debug("Raw data: %s", data)
        return 0


def get_printer() -> Printer:
    ptype = settings.printer_type
    if ptype == "dummy":
        return DummyPrinter()
    if ptype == "device" or settings.printer_device:
        return DevicePrinter(settings.printer_device)
    return CUPSPrinter(settings.printer_host, settings.printer_name)


# Global printer instance
printer = get_printer()


# Backward compatibility wrappers
def get_status(printer_name=None):
    return printer.get_status()


def send_raw(data, printer_name=None):
    return printer.send_raw(data)
