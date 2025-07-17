# バージョンアップ履歴 / Version History
    VA.B.C  例（V1.2.3　　A=1、B=2,C=3）  
     A:QGISのバージョンアップに伴う、本体の修正  
     B:UIの変更（プラグインの追加等含む）、本体の機能追加  
     C:プロファイル・プラグイン、本体の修正  
     
20250717　V3.0.1　国際化対応追加（英語・日本語）、デフォルト言語は日本語
  - QGISの設定からロケールを自動取得
  - QGIS設定の優先順位に従った言語選択
  - デバッグ情報をQGISメッセージログに出力
  - PyQt4からPyQt5への移行とコード簡素化
  - 不要なPyQt4関数（_fromUtf8、_translate等）の削除
  - 新しいシグナル/スロット接続方式の採用
20250316　V3.0.0　QGIS3.42　に対応  
20241201　V2.0.2　公式プラグイン登録  
20241109　V2.0.1　GIS3.38以前　にも対応  
20241109　V2.0.0　GIS3.4　に対応  
公開初版　　　 V1.0.0　QGIS　3.38　対応版

## 国際化対応について / About Internationalization

このプラグインは日本語と英語に対応しています。  
This plugin supports both Japanese and English.

- デフォルト言語: 日本語 / Default language: Japanese
- サポート言語: 日本語、英語 / Supported languages: Japanese, English

システムの言語設定に応じて自動的に言語が切り替わります。  
The language switches automatically based on your system language settings.
