#!/usr/bin/python
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_test2.ui'
#
# Created: Tue Nov 12 11:50:34 2013
#      by: PyQt5 UI code generator (自動変換)
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import qgis.utils


def _translate(context, text):
    return QtCore.QCoreApplication.translate(context, text)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName('EditTool')
        Dialog.setFixedSize(400, 200)

        # レイアウト選択 ComboBox のみ配置
        self.layoutComboBox = QtWidgets.QComboBox(Dialog)
        self.layoutComboBox.setGeometry(QtCore.QRect(10, 10, 380, 30))
        self.layoutComboBox.setObjectName('layoutComboBox')
        try:
            project = qgis.utils.iface.project()
            manager = project.layoutManager()
            for layout in manager.layouts():
                try:
                    page = layout.pageCollection().page(0)
                    size = page.pageSize()
                    w, h = size.width(), size.height()
                    if w > 0 and h > 0:
                        orientation = "横" if w > h else "縦"
                        display_name = f"{layout.name()}（{int(w)}×{int(h)} mm, {orientation}）"
                    else:
                        display_name = f"{layout.name()}（サイズ不明, 向き不明）"
                except Exception:
                    display_name = f"{layout.name()}（サイズ不明, 向き不明）"
                self.layoutComboBox.addItem(display_name, layout.name())
        except Exception:
            pass
        self.layoutComboBox.currentIndexChanged.connect(self.updatePreview)

        # プレビュー用のGroupBoxのみ配置
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 50, 380, 140))
        self.groupBox.setObjectName('groupBox')
        self.groupBox.setTitle('プレビュー')

        self.updatePreview()

    def updatePreview(self):
        layout_name = self.layoutComboBox.currentData()
        layout = self.getLayoutByName(layout_name)
        try:
            project = qgis.utils.iface.project()
            manager = project.layoutManager()
            print("全レイアウト一覧:")
            for l in manager.layouts():
                page = l.pageCollection().page(0)
                size = page.pageSize()
                print(f"  {l.name()} : {size.width()} x {size.height()} mm")
            if layout:
                page = layout.pageCollection().page(0)
                size = page.pageSize()  # QSizeF (mm)
                print(f"選択レイアウト: {layout_name}, 実layout名: {layout.name()}, サイズ: {size.width()} x {size.height()} mm")
                dpi = 96  # 必要に応じてQGISのDPIを取得
                width_px = int(size.width() / 25.4 * dpi)
                height_px = int(size.height() / 25.4 * dpi)
                if hasattr(self, 'previewWidget'):
                    self.previewWidget.setFixedSize(width_px, height_px)
                else:
                    self.groupBox.setFixedSize(width_px, height_px)
        except Exception as e:
            print(e)

    def getLayoutByName(self, name):
        try:
            project = qgis.utils.iface.project()
            manager = project.layoutManager()
            print("getLayoutByName: 全レイアウト一覧とサイズ")
            for layout in manager.layouts():
                page = layout.pageCollection().page(0)
                size = page.pageSize()
                print(f"  {layout.name()} : {size.width()} x {size.height()} mm")
                if layout.name() == name:
                    print(f"選択レイアウト: {name} のサイズ: {size.width()} x {size.height()} mm")
                    return layout
        except Exception as e:
            print(f"getLayoutByName error: {e}")
        return None

    # 不要なUI要素はすべて削除しました。ComboBoxとプレビューGroupBoxのみ残しています。


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())
