import sys
import time
from PyQt4 import QtGui, QtCore
 
 
class Main(QtGui.QWidget):
 
    def __init__(self):
 
        QtGui.QWidget.__init__(self)
 
        self.setupUi()
 
        self.setGeometry(300,300,250,130)
 
        self.setWindowTitle("Clock")
 
    def setupUi(self):
 
        layout = QtGui.QVBoxLayout(self)
 
 
        timer = QtCore.QTimer(self)
 
        timer.timeout.connect(self.timeout)
 
        timer.start(10)
 
 
        self.button = QtGui.QPushButton("Show seconds", self)
 
        self.button.setCheckable(True)
 
        self.button.clicked.connect(self.toggle)
 
        layout.addWidget(self.button)
 
 
        self.lcd = QtGui.QLCDNumber(self)
 
        layout.addWidget(self.lcd)
 
    def timeout(self):
 
        if self.button.isChecked():
            self.lcd.display(time.strftime("%H"+":"+"%M"+":"+"%S"))
 
        else:
            self.lcd.display(time.strftime("%H"+":"+"%M"))
 
    def toggle(self, checked):
 
        if checked:
            self.button.setText("Hide seconds")
            self.lcd.setDigitCount(8)
 
        else:
            self.button.setText("Show seconds")
            self.lcd.setDigitCount(5)
 
if __name__ == "__main__":
 
    app = QtGui.QApplication(sys.argv)
 
    main = Main()
    main.show()
 
    sys.exit(app.exec_())