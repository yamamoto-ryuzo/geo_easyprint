#-*- coding:utf-8 -*-

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from print_ui import Ui_Dialog


class Form(QDialog, Ui_Dialog):
    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.checkBox.setVisible(False)
