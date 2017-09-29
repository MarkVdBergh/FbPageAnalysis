
import sys
from PyQt5 import QtWidgets
app = QtWidgets.QApplication(sys.argv)
button = QtWidgets.QPushButton("Hello, World!")
button.setFixedSize(100, 50)
button.show()
app.exec_()