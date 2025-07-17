# -*- coding: utf-8 -*-

"""
Print UI - PyQt5対応版
"""

from qgis.PyQt import QtCore, QtGui, QtWidgets


def tr(text):
    """翻訳用の関数"""
    return QtCore.QCoreApplication.translate("EasyPrint", text)


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(485, 197)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.checkBox = QtWidgets.QCheckBox(Dialog)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 1, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 3, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout.addItem(spacerItem, 1, 1, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 4)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(tr("EasyPrint"))
        self.checkBox.setText(tr("Print as raster (fast)"))
        self.pushButton.setText(tr("Page setup"))
        self.label.setText(
            tr("Printer settings are set to \"A4\" \"Landscape\"") + "\n" +
            tr("To change paper size or orientation,") + "\n" +
            tr("please set the paper size using the \"Page Setup\" button below") + "\n\n" +
            tr("Also, if you set different settings from the size and orientation set in the EasyPrint settings screen") + "\n" +
            tr("margins may appear or content may overflow") + "\n\n" +
            tr("Printing may take time") + "\n" +
            tr("If you operate the screen while printing is in progress, the screen may freeze") + "\n" +
            tr("Please wait for a while")
        )

