from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# from test import Ui_Dialog
from ui_test4 import Ui_Dialog

class ui_Control(QDialog, Ui_Dialog):
    def __init__(self, parent, fl):
        QDialog.__init__(self, parent, fl)
        self.setupUi(self)
