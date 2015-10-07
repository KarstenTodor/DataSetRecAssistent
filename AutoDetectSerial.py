import sys
import serial
from serial.tools import list_ports

class AutoDetectSerial:
    def __init__(self):
        self.device_port = self.getPort()
        if self.device_port == None:
            print "Autodetection of board failed."

    def getPort(self):
        """Discover the dev board ."""
        ports_available = list(list_ports.comports())
        dev_port = tuple()
        for port in ports_available:
            if port[1].startswith("USB Serial"):
                dev_port = port
        if dev_port:
            return dev_port

    def open(self, baudrate):
        self.con = serial.Serial(self.device_port[0], baudrate)

    def close(self):
        if self.con.isOpen():
            self.con.close()

if __name__ == "__main__":
    print "Welcome to Example: Autodetect Serial Connection!"
    try:
        serialc = AutoDetectSerial(115200)
        print "Connected to: %s" % serialc.device_port[1]
        serialc.close()
    except TypeError:
        print "Cannot find a dev board connected..."