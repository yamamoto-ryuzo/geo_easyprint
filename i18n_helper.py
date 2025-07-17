#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
国際化対応のためのヘルパー関数
"""

import os
from pathlib import Path

from qgis.PyQt.QtCore import QCoreApplication, QTranslator, QLocale, QSettings
from qgis.core import QgsApplication, QgsMessageLog, Qgis


def tr(text):
    """
    翻訳用の関数
    """
    return QCoreApplication.translate("EasyPrint", text)


class I18nHelper:
    def __init__(self):
        self.translator = None
        self.locale = None
        
    def setup_translation(self, plugin_dir):
        """
        翻訳の設定を行う
        QGISの設定から言語を自動取得
        """
        # QGISの設定からロケールを取得
        detected_locale = self._get_qgis_locale()
        
        # ログ出力（シンプル化）
        self._log_message(f"Detected locale: {detected_locale}")
        
        # 日本語以外の場合は英語にフォールバック
        locale_name = 'ja' if detected_locale.startswith('ja') else 'en'
            
        # 翻訳ファイルのパスを構築
        qm_file = Path(plugin_dir) / 'i18n' / f'easyprint_{locale_name}.qm'
        
        self._log_message(f"Using locale: {locale_name}, Translation file: {qm_file}")
        
        if qm_file.exists():
            self.translator = QTranslator()
            if self.translator.load(str(qm_file)):
                QCoreApplication.installTranslator(self.translator)
                self.locale = locale_name
                self._log_message(f"Translation loaded successfully for locale: {locale_name}")
                return True
        
        # 翻訳ファイルが見つからない場合は日本語をデフォルトとする
        self.locale = 'ja'
        self._log_message("Translation file not found, using default Japanese locale", level=Qgis.Warning)
        return False
        
    def _get_qgis_locale(self):
        """
        QGISの設定からロケールを取得（簡素化版）
        """
        settings = QSettings()
        
        # QGIS設定のoverride locale
        if settings.value('locale/overrideFlag', False, type=bool):
            user_locale = settings.value('locale/userLocale', '', type=str)
            if user_locale:
                return user_locale
        
        # QGISアプリケーションから取得
        try:
            qgis_app = QgsApplication.instance()
            if qgis_app:
                qgis_locale = qgis_app.locale()
                if qgis_locale:
                    return qgis_locale
        except:
            pass
        
        # システムのロケール
        return QLocale.system().name()
        
    def _log_message(self, message, level=None):
        """
        ログメッセージを出力（簡素化版）
        """
        if level is None:
            level = Qgis.Info
            
        try:
            QgsMessageLog.logMessage(f"EasyPrint: {message}", "EasyPrint", level)
        except:
            # フォールバック：コンソールに出力
            print(f"EasyPrint: {message}")
        
    def get_current_locale(self):
        """現在のロケールを取得"""
        return self.locale or 'ja'
        
    def is_japanese(self):
        """現在の言語が日本語かどうかを判定"""
        return self.get_current_locale().startswith('ja')
        
    def is_english(self):
        """現在の言語が英語かどうかを判定"""
        return self.get_current_locale().startswith('en')
        
    def cleanup(self):
        """翻訳リソースのクリーンアップ"""
        if self.translator:
            QCoreApplication.removeTranslator(self.translator)
            self.translator = None
