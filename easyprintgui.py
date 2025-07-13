# -*- coding: utf-8 -*-
from pathlib import Path
import sys
import math

from qgis.PyQt import uic
from qgis.PyQt.QtCore import pyqtSignal, Qt, QSettings
from qgis.PyQt.QtGui import QColor, QPixmap
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QColorDialog, QMessageBox
from qgis.core import QgsProject, QgsRectangle, QgsPointXY, QgsWkbTypes
from qgis.gui import QgsRubberBand


from .tools import utils
from . import settings

UI_FILE = "Ui_easyprint.ui"


class EasyPrintGui(QDialog):
    okClickedSimpleMap = pyqtSignal(
        str, str, str, str, str, bool, bool, bool, bool, bool, bool, bool, int, QColor
    )

    def __init__(self, parent, iface):
        super(EasyPrintGui, self).__init__(parent=parent)
        self.iface = iface
        self.newest_composer = None
        self.preview_rubber_band = None
        self.is_preview_active = False

        # ダイアログをツールウィンドウタイプにして、背景での操作を可能にする
        self.setWindowFlags(Qt.Tool | Qt.WindowStaysOnTopHint)
        
        # ダイアログサイズを調整してマップキャンバス操作領域を確保
        self.resize(380, 500)
        
        directory = Path(__file__).parent
        ui_file = directory / UI_FILE
        uic.loadUi(ui_file, self)

    def initGui(
        self, scales, paperformats, layouts, maplayers, vectorlayers, newest_composer
    ):

        # hidden GUI
        self.label_5.setVisible(False)
        self.layout.setVisible(False)
        self.label_6.setVisible(False)
        self.person.setVisible(False)
        self.label_27.setVisible(False)
        self.copyright.setVisible(False)
        self.label_29.setVisible(False)
        self.cuttinglines.setVisible(False)
        self.label_30.setVisible(False)
        self.foldingmarks.setVisible(False)

        self.button_show_composer = self.buttonBox.addButton(
            u"最後に閉じた(作成した)プレビュー画面を開く", QDialogButtonBox.ActionRole
        )
        self.button_show_composer.setEnabled(False)
        
        # Add print area preview button
        self.button_preview_area = self.buttonBox.addButton(
            u"印刷範囲プレビュー", QDialogButtonBox.ActionRole
        )
        
        self.buttonBox.layout().insertWidget(
            0, self.button_show_composer, 0, Qt.AlignLeft
        )
        self.buttonBox.layout().insertWidget(
            1, self.button_preview_area, 0, Qt.AlignLeft
        )

        self.settings = QSettings()

        # SimpleMap #
        # Set some stuff for the user scale spin box.
        self.userScale.setMinimum(1)
        self.userScale.setMaximum(100000000)
        self.userScale.setPrefix("1 : ")
        try:
            self.userScale.setValue(int(scales[0]))
        except TypeError:
            self.userScale.setValue(100000000)

        # Fill the combobox with available scales.
        for scale in scales:
            self.printScale.addItem("1 : " + scale)
        self.printScale.currentIndexChanged.connect(
            self.on_printScale_currentIndexChanged
        )

        # Fill the combobox with available paperformats.
        self.printFormat.addItems(paperformats)

        # Fill the combobox with available layouts.
        for l in layouts:
            self.layout.addItem(l.getID())

        self.person.setText(self.settings.value("easyprint/gui/person"))
        self.grids.setChecked(self.get_registry("easyprint/gui/grids", True))
        self.legend.setChecked(self.get_registry("easyprint/gui/legend", True))
        self.scalebar.setChecked(self.get_registry("easyprint/gui/scalebar", True))
        self.copyright.setChecked(self.get_registry("easyprint/gui/copyright", False))
        self.cuttinglines.setChecked(
            self.get_registry("easyprint/gui/cuttinglines", False)
        )
        self.foldingmarks.setChecked(
            self.get_registry("easyprint/gui/foldingmarks", False)
        )
        self.crsdesc.setChecked(
            self.get_registry("easyprint/gui/crsdescription", False)
        )

        self.background_color = Qt.white
        self.change_color_pix()
        self.map_background_button.clicked.connect(self.change_background_color)

        project = QgsProject.instance()
        manager = project.layoutManager()
        composers = manager.printLayouts()

        if newest_composer and newest_composer in composers:
            self.newest_composer = newest_composer
        elif newest_composer is None and composers:
            self.newest_composer = composers[-1]
        if self.newest_composer:
            self.button_show_composer.setEnabled(True)

        self.button_show_composer.clicked.connect(self.show_composer)
        self.button_preview_area.clicked.connect(self.toggle_print_area_preview)
        
        # Connect scale and format changes to update preview
        self.printScale.currentIndexChanged.connect(self.update_preview_if_active)
        self.printFormat.currentIndexChanged.connect(self.on_paper_format_changed)  # 用紙フォーマット変更時の処理を追加
        self.userScale.valueChanged.connect(self.update_preview_if_active)
        self.layout.currentIndexChanged.connect(self.on_layout_changed)  # レイアウト変更時の専用処理
        
        # マップキャンバスのズーム変更を検知してプレビュー更新
        self.iface.mapCanvas().scaleChanged.connect(self.on_canvas_scale_changed)

    def set_newest_composer(self, composer):
        self.newest_composer = composer
        self.button_show_composer.setEnabled(True)

    def hidden_view(self, view):
        composerView.composerViewHide.connect(self.hidden_view)
        window = view.composerWindow()
        reply = QMessageBox.question(
            window,
            u"保存しますか？",
            u"印刷(コンポーザー)の設定を保存しますか？",
            QMessageBox.Yes,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            window.close()
            self.iface.deleteComposer(view)

    def set_newestbutton_enabled(self, composer):
        project = QgsProject.instance()
        manager = project.layoutManager()
        composers = manager.printLayouts()
        if composer in composers:
            composers.remove(composer)
        if self.newest_composer == composer and not composers:
            self.newest_composer = None
            self.button_show_composer.setEnabled(False)
        elif self.newest_composer == composer and composers:
            # print('current composer remove')
            self.newest_composer = composers[-1]
        elif self.newest_composer is None and composers:
            self.newest_composer = composers[-1]
            self.button_show_composer.setEnabled(True)
        else:
            self.newest_composer = None
            self.button_show_composer.setEnabled(False)

    def show_composer(self):
        composer = self.newest_composer
        if not composer:
            return
        self.close()
        self.iface.openLayoutDesigner(composer)

    def change_background_color(self):
        color = QColorDialog.getColor(self.background_color)
        if not color.isValid():
            # カラーが選択されたかの判定
            return
        self.background_color = color
        self.change_color_pix()

    def change_color_pix(self):
        color_pix = QPixmap(24, 24)
        color_pix.fill(self.background_color)
        self.map_background.setPixmap(color_pix)

    def on_printScale_currentIndexChanged(self):
        currentIndex = self.printScale.currentIndex()
        if currentIndex == 1:
            self.userScale.setEnabled(True)
        else:
            self.userScale.setEnabled(False)

    def accept(self):
        # 印刷範囲プレビューを削除してから処理を続行
        self.hide_print_area_preview()
        
        super(EasyPrintGui, self).accept()
        self.set_registry("easyprint/gui/person", self.person.text())
        self.set_registry("easyprint/gui/grids", self.grids.isChecked())
        self.set_registry("easyprint/gui/legend", self.legend.isChecked())
        self.set_registry("easyprint/gui/scalebar", self.scalebar.isChecked())
        self.set_registry("easyprint/gui/copyright", self.copyright.isChecked())
        self.set_registry("easyprint/gui/cuttinglines", self.cuttinglines.isChecked())
        self.set_registry("easyprint/gui/foldingmarks", self.foldingmarks.isChecked())
        self.set_registry("easyprint/gui/crsdescription", self.crsdesc.isChecked())

        currentIndex = self.printScale.currentIndex()
        if currentIndex == 1:
            self.scale = "1 : " + str(self.userScale.value())
        else:
            self.scale = self.printScale.currentText()

        tabIndex = self.tabWidget.currentIndex()

        if tabIndex == 0:
            self.okClickedSimpleMap.emit(
                self.scale,
                self.printFormat.currentText(),
                self.title.text(),
                self.subtitle.text(),
                self.person.text(),
                self.crsdesc.isChecked(),
                self.grids.isChecked(),
                self.legend.isChecked(),
                self.scalebar.isChecked(),
                self.copyright.isChecked(),
                self.cuttinglines.isChecked(),
                self.foldingmarks.isChecked(),
                int(self.layout.currentIndex()),
                self.background_color,
            )

    def reject(self):
        """キャンセルボタンが押されたときにプレビューを削除"""
        self.hide_print_area_preview()
        super(EasyPrintGui, self).reject()

    def set_registry(self, key, value):
        if not self.settings:
            return -1
        # value = {True: 1, False: 0}.get(value, value)
        return self.settings.setValue(key, value)

    def get_registry(self, key, default=None):
        if not self.settings:
            return -1
        value = self.settings.value(key, default)
        return {"true": True, "false": False}.get(value, value)

    def toggle_print_area_preview(self):
        """印刷範囲プレビューのオン/オフを切り替え"""
        if self.is_preview_active:
            self.hide_print_area_preview()
        else:
            self.show_print_area_preview()

    def show_print_area_preview(self):
        """印刷範囲をマップキャンバス上に表示"""
        try:
            # 既存のラバーバンドを削除
            if self.preview_rubber_band:
                self.iface.mapCanvas().scene().removeItem(self.preview_rubber_band)
                self.preview_rubber_band = None
            
            # 最新のページサイズを取得（表示用）
            paper_width, paper_height = self.get_layout_page_size()
            
            # レイアウトから取得できない場合はフォーマット名から推測
            if paper_width is None or paper_height is None:
                paper_format = self.printFormat.currentText()
                paper_width, paper_height = self.get_paper_size_mm(paper_format)
                print(f"フォールバック: フォーマット名から推測 {paper_width}mm x {paper_height}mm")
            else:
                print(f"レイアウトから正常に取得: {paper_width}mm x {paper_height}mm")
            
            # プレビュー矩形を計算（取得したサイズを直接渡す）
            preview_rect = self.calculate_print_area(paper_width, paper_height)
            if preview_rect is None:
                QMessageBox.warning(self, "警告", "印刷範囲を計算できませんでした。")
                return
            
            # 新しいラバーバンドを作成
            self.preview_rubber_band = QgsRubberBand(self.iface.mapCanvas(), QgsWkbTypes.PolygonGeometry)
            
            # 用紙の向きに応じて色を設定
            if paper_width > paper_height:
                # 横向き用紙の場合は青色
                self.preview_rubber_band.setColor(QColor(0, 0, 255, 80))  # 半透明の青
                self.preview_rubber_band.setFillColor(QColor(0, 0, 255, 40))  # より薄い塗りつぶし
                print(f"横向き用紙プレビュー: {paper_width}mm x {paper_height}mm")
            else:
                # 縦向き用紙の場合は赤色
                self.preview_rubber_band.setColor(QColor(255, 0, 0, 80))  # 半透明の赤
                self.preview_rubber_band.setFillColor(QColor(255, 0, 0, 40))  # より薄い塗りつぶし
                print(f"縦向き用紙プレビュー: {paper_width}mm x {paper_height}mm")
                
            self.preview_rubber_band.setWidth(3)
            
            # 矩形を確実に閉じるために、reset()を呼んでから点を追加
            self.preview_rubber_band.reset(QgsWkbTypes.PolygonGeometry)
            
            print(f"矩形座標詳細:")
            print(f"  左下: ({preview_rect.xMinimum():.2f}, {preview_rect.yMinimum():.2f})")
            print(f"  右下: ({preview_rect.xMaximum():.2f}, {preview_rect.yMinimum():.2f})")
            print(f"  右上: ({preview_rect.xMaximum():.2f}, {preview_rect.yMaximum():.2f})")
            print(f"  左上: ({preview_rect.xMinimum():.2f}, {preview_rect.yMaximum():.2f})")
            
            # 矩形の四隅の点を追加（時計回り）
            self.preview_rubber_band.addPoint(QgsPointXY(preview_rect.xMinimum(), preview_rect.yMinimum()))
            self.preview_rubber_band.addPoint(QgsPointXY(preview_rect.xMaximum(), preview_rect.yMinimum()))
            self.preview_rubber_band.addPoint(QgsPointXY(preview_rect.xMaximum(), preview_rect.yMaximum()))
            self.preview_rubber_band.addPoint(QgsPointXY(preview_rect.xMinimum(), preview_rect.yMaximum()))
            self.preview_rubber_band.addPoint(QgsPointXY(preview_rect.xMinimum(), preview_rect.yMinimum()))  # 閉じる
            
            # ラバーバンドを表示
            self.preview_rubber_band.show()

            self.is_preview_active = True
            
            # ボタンテキストに用紙の向きとサイズを表示
            orientation = "横向き" if paper_width > paper_height else "縦向き"
            self.button_preview_area.setText(f"プレビュー非表示 ({orientation} {paper_width:.0f}x{paper_height:.0f}mm)")
            
            # マップキャンバスを強制的に更新してプレビューを確実に反映
            self.iface.mapCanvas().refresh()
            self.iface.mapCanvas().refreshAllLayers()
            
            print(f"プレビュー表示完了: {orientation} {paper_width:.0f}x{paper_height:.0f}mm")
            
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"プレビュー表示中にエラーが発生しました: {str(e)}")
            import traceback
            traceback.print_exc()

    def hide_print_area_preview(self):
        """印刷範囲プレビューを非表示"""
        try:
            if self.preview_rubber_band:
                print("既存のプレビューを削除中...")
                # ラバーバンドをマップキャンバスから完全に削除
                self.iface.mapCanvas().scene().removeItem(self.preview_rubber_band)
                self.preview_rubber_band = None
                print("プレビュー削除完了")
            
            self.is_preview_active = False
            self.button_preview_area.setText("印刷範囲プレビュー")
            
            # マップキャンバスを更新して変更を反映
            self.iface.mapCanvas().refresh()
            
        except Exception as e:
            print(f"プレビュー非表示エラー: {str(e)}")
            # エラーが発生してもフラグはリセット
            self.is_preview_active = False
            self.preview_rubber_band = None

    def update_preview_if_active(self):
        """プレビューがアクティブな場合、プレビューを更新"""
        if self.is_preview_active:
            self.show_print_area_preview()

    def on_canvas_scale_changed(self):
        """マップキャンバスのスケール変更時の処理"""
        # 現在のキャンバススケールを取得
        canvas_scale = round(self.iface.mapCanvas().scale())
        if canvas_scale > 0:
            # 最初のスケール選択肢（現在のキャンバススケール）を更新
            current_scale_text = f"1 : {canvas_scale}"
            if self.printScale.count() > 0:
                self.printScale.setItemText(0, current_scale_text)
        
        # プレビューが表示されている場合は更新
        if self.is_preview_active:
            self.show_print_area_preview()

    def on_paper_format_changed(self):
        """用紙フォーマット変更時の処理"""
        format_name = self.printFormat.currentText()
        print(f"用紙フォーマットが変更されました: {format_name}")
        
        # まずレイアウトから実際の用紙サイズを取得
        paper_width, paper_height = self.get_layout_page_size()
        
        # レイアウトから取得できない場合はフォーマット名から推測
        if paper_width is None or paper_height is None:
            paper_width, paper_height = self.get_paper_size_mm(format_name)
            print(f"フォーマット名から推測したサイズ: {paper_width}mm x {paper_height}mm")
        else:
            print(f"レイアウトから取得したサイズ: {paper_width}mm x {paper_height}mm")
        
        # プレビューが表示されている場合は即座に更新
        if self.is_preview_active:
            print(f"フォーマット変更によりプレビューを新しい用紙サイズで更新: {paper_width}mm x {paper_height}mm")
            # 少し遅延させてから更新（UIの変更が完了してから）
            from qgis.PyQt.QtCore import QTimer
            QTimer.singleShot(100, self.show_print_area_preview)
        
        # ユーザーに用紙サイズの変更を通知（デバッグ用）
        orientation = "横向き" if paper_width > paper_height else "縦向き"
        print(f"用紙設定確定: {orientation} {paper_width}mm x {paper_height}mm")

    def on_layout_changed(self):
        """レイアウト変更時の処理"""
        layout_index = self.layout.currentIndex()
        print(f"レイアウトが変更されました: インデックス {layout_index}")
        
        # レイアウトから新しい用紙サイズを強制的に取得
        paper_width, paper_height = self.get_layout_page_size(force_refresh=True)
        
        if paper_width and paper_height:
            orientation = "横向き" if paper_width > paper_height else "縦向き"
            print(f"新しいレイアウトサイズ: {orientation} {paper_width}mm x {paper_height}mm")
            
            # プレビューが表示されている場合は必ず更新
            if self.is_preview_active:
                print("レイアウト変更によりプレビューを強制更新")
                # 少し遅延させてからプレビューを更新（UIの変更が完了してから）
                from qgis.PyQt.QtCore import QTimer
                QTimer.singleShot(200, lambda: self.force_update_preview(paper_width, paper_height))
            else:
                print("プレビューは非表示ですが、次回表示時に新しいレイアウトサイズが反映されます")
                # プレビューボタンのテキストを更新して新しいサイズを示す
                self.button_preview_area.setText(f"印刷範囲プレビュー ({orientation} {paper_width:.0f}x{paper_height:.0f}mm)")
        else:
            print("警告: レイアウトからページサイズを取得できませんでした")
            
    def force_update_preview(self, paper_width, paper_height):
        """プレビューを強制的に更新（サイズを指定して）"""
        try:
            print(f"プレビューを強制更新: {paper_width}mm x {paper_height}mm")
            
            # 既存のプレビューを完全に削除
            self.hide_print_area_preview()
            
            # 少し待ってからプレビューを再表示
            from qgis.PyQt.QtCore import QTimer
            QTimer.singleShot(50, self.show_print_area_preview)
            
        except Exception as e:
            print(f"プレビュー強制更新エラー: {str(e)}")
            import traceback
            traceback.print_exc()

    def calculate_print_area(self, paper_width=None, paper_height=None):
        """現在の設定に基づいて印刷範囲を計算"""
        try:
            # 現在のスケールを取得
            current_scale_index = self.printScale.currentIndex()
            if current_scale_index == 1:  # ユーザー定義
                scale = self.userScale.value()
            else:
                scale_text = self.printScale.currentText()
                scale = float(scale_text.replace("1 : ", "").replace(",", ""))

            print(f"使用するスケール: 1:{scale}")

            # サイズが引数で渡されていない場合のみレイアウトから取得
            if paper_width is None or paper_height is None:
                print("引数でサイズが渡されていないため、レイアウトから取得します")
                paper_width, paper_height = self.get_layout_page_size()
                
                if paper_width is None or paper_height is None:
                    print("レイアウトからページサイズを取得できません。フォーマット名から推測します。")
                    paper_format = self.printFormat.currentText()
                    paper_width, paper_height = self.get_paper_size_mm(paper_format)
                    print(f"フォーマット名 '{paper_format}' から推測したサイズ: {paper_width}mm x {paper_height}mm")
                else:
                    print(f"レイアウトから取得したページサイズ: {paper_width}mm x {paper_height}mm")
            else:
                print(f"引数で渡されたページサイズを使用: {paper_width}mm x {paper_height}mm")
                
            if paper_width is None or paper_height is None:
                print("用紙サイズを取得できませんでした")
                return None

            # マップキャンバスの中心点を取得
            canvas = self.iface.mapCanvas()
            center = canvas.center()
            
            # 印刷範囲をメートル単位で計算
            # 1mm = scale / 1000 メートル
            width_meters = (paper_width * scale) / 1000
            height_meters = (paper_height * scale) / 1000
            
            print(f"計算された印刷範囲サイズ: {width_meters:.2f}m x {height_meters:.2f}m")
            
            # 用紙の向きを考慮した矩形作成
            if paper_width > paper_height:
                print(f"横向き用紙として計算: {paper_width}mm x {paper_height}mm")
            else:
                print(f"縦向き用紙として計算: {paper_width}mm x {paper_height}mm")
            
            # 矩形を作成（中心点を基準）
            x_min = center.x() - width_meters / 2
            x_max = center.x() + width_meters / 2
            y_min = center.y() - height_meters / 2
            y_max = center.y() + height_meters / 2
            
            print(f"プレビュー矩形範囲: ({x_min:.2f}, {y_min:.2f}) to ({x_max:.2f}, {y_max:.2f})")
            
            return QgsRectangle(x_min, y_min, x_max, y_max)
            
        except Exception as e:
            print(f"印刷範囲計算エラー: {str(e)}")
            return None

    def get_layout_page_size(self, force_refresh=False):
        """現在選択されているレイアウトからページサイズを取得（mm単位）"""
        try:
            # 現在選択されているレイアウトインデックスを取得
            layout_index = self.layout.currentIndex()
            
            # QGISのプロジェクトからレイアウトマネージャーを取得
            project = QgsProject.instance()
            manager = project.layoutManager()
            layouts = manager.printLayouts()
            
            print(f"利用可能なレイアウト数: {len(layouts)}")
            print(f"選択されたレイアウトインデックス: {layout_index}")
            
            if layout_index < 0 or layout_index >= len(layouts):
                print(f"無効なレイアウトインデックス: {layout_index}, 利用可能なレイアウト数: {len(layouts)}")
                return None, None
            
            # 選択されたレイアウトを取得
            selected_layout = layouts[layout_index]
            print(f"選択されたレイアウト名: '{selected_layout.name()}'")
            
            # 強制更新フラグがある場合は詳細情報を出力
            if force_refresh:
                print(f"レイアウト強制更新: {selected_layout.name()}")
            
            # レイアウトの最初のページからページサイズを取得
            page_collection = selected_layout.pageCollection()
            page_count = page_collection.pageCount()
            print(f"レイアウト内のページ数: {page_count}")
            
            if page_count == 0:
                print("レイアウトにページがありません")
                return None, None
            
            page = page_collection.page(0)  # 最初のページを取得
            page_size = page.pageSize()
            
            # QgsLayoutSizeからmm単位の幅と高さを取得
            width_mm = page_size.width()
            height_mm = page_size.height()
            
            print(f"ページサイズ取得成功: {width_mm}mm x {height_mm}mm (レイアウト '{selected_layout.name()}')")
            
            # サイズの妥当性をチェック
            if width_mm <= 0 or height_mm <= 0:
                print(f"無効なページサイズ: {width_mm}mm x {height_mm}mm")
                return None, None
            
            return width_mm, height_mm
            
        except Exception as e:
            print(f"レイアウトページサイズ取得エラー: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, None

    def get_paper_size_mm(self, format_name):
        """用紙サイズ名から幅と高さ（mm）を取得"""
        # 一般的な用紙サイズのマッピング（縦向き基準）
        paper_sizes = {
            "A4": (210, 297),
            "A3": (297, 420),
            "A2": (420, 594),
            "A1": (594, 841),
            "A0": (841, 1189),
            "B4": (250, 353),
            "B3": (353, 500),
            "B2": (500, 707),
            "B1": (707, 1000),
            "B0": (1000, 1414),
            "Letter": (216, 279),
            "Legal": (216, 356),
            "Tabloid": (279, 432),
        }
        
        print(f"用紙フォーマット: {format_name}")
        
        # 横向きの判定（より詳細な判定）
        is_landscape = False
        if any(keyword in format_name for keyword in ["横", "Landscape", "landscape", "LANDSCAPE"]):
            is_landscape = True
        
        # ベースとなる用紙サイズを特定
        base_format = None
        for key in paper_sizes.keys():
            if key in format_name:
                base_format = key
                break
        
        if base_format:
            width, height = paper_sizes[base_format]
            if is_landscape:
                # 横向きの場合は幅と高さを入れ替える
                print(f"横向き: {base_format} -> {height}mm x {width}mm")
                return height, width
            else:
                # 縦向きの場合はそのまま
                print(f"縦向き: {base_format} -> {width}mm x {height}mm")
                return width, height
        
        # デフォルトはA4縦向き
        print("デフォルトA4縦向きを使用")
        return paper_sizes.get("A4", (210, 297))

    def closeEvent(self, event):
        """ダイアログが閉じられるときにプレビューを削除し、接続を解除"""
        self.hide_print_area_preview()
        
        # マップキャンバスの接続を解除
        try:
            self.iface.mapCanvas().scaleChanged.disconnect(self.on_canvas_scale_changed)
        except:
            pass  # 既に切断されている場合は無視
            
        super().closeEvent(event)
