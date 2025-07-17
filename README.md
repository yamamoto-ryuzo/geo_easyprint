# プラグイン名 / Plugin Name

EasyPrint

## プラグイン説明 / Plugin Description

デフォルトの印刷の操作が複雑なので、簡略化させた印刷プラグイン  
とりあえず、誰もメンテされなくなったプラグインを最新の環境でも動くように改修中

This is a simplified printing plugin to reduce the complexity of default printing operations.  
Currently working on updating an unmaintained plugin to work with the latest environment.

## 国際化対応 / Internationalization

このプラグインは日本語と英語に対応しています。  
This plugin supports both Japanese and English.

- **デフォルト言語 / Default language**: 日本語 / Japanese
- **サポート言語 / Supported languages**: 日本語、英語 / Japanese, English

### 自動言語切り替え / Automatic Language Switching

プラグインは以下の優先順位で言語を自動選択します：  
The plugin automatically selects language in the following priority:

1. **QGIS設定のオーバーライドロケール** / QGIS override locale setting
2. **QGISアプリケーションの現在のロケール** / Current QGIS application locale
3. **QGISのグローバル設定** / QGIS global settings
4. **システムのロケール** / System locale
5. **環境変数** (`LANG`, `LANGUAGE`) / Environment variables

### 言語変更方法 / How to Change Language

QGISの設定から言語を変更できます：  
You can change the language from QGIS settings:

1. **QGIS** → **設定** → **オプション** → **一般** → **ロケール**
2. **QGIS** → **Settings** → **Options** → **General** → **Locale**

言語を変更後、QGISを再起動してください。  
Please restart QGIS after changing the language.

### 翻訳ファイルのコンパイル / Compiling Translation Files

翻訳ファイルをコンパイルするには、以下のコマンドを実行してください：  
To compile translation files, run the following commands:

```bash
# Windows
compile_translations.bat

# Python script
python compile_translations.py

# Manual compilation
lrelease i18n/easyprint_ja.ts -qm i18n/easyprint_ja.qm
lrelease i18n/easyprint_en.ts -qm i18n/easyprint_en.qm
```

## 設定

### 図郭選択

図郭の shp ファイルが存在する場合、プラグインに図郭番号を選択するためのコンボボックスが表示される。

**setting.py での設定方法**

- ZUKAKU_X_MARGIN
  - 図郭へのズーム時の横への空白
- ZUKAKU_Y_MARGIN = 100
  - 図郭へのズーム時の横への空白
- ZUKAKU_FILE_NAME
  - data フォルダ内の図郭ファイル名
- ZUKAKU_COLUMN_NAME = "ID"
  - 図郭番号の列名

## 依存しているプラグイン

なし

## 使い方

## フォルダ構成 / Folder Structure

```
./
├─data
├─i18n            # 国際化対応ファイル / Internationalization files
├─images
├─layouts
├─pictures
├─preferences
├─styles
└─tools
```

### data

図郭ファイルなどプラグインが使用するデータが格納されている。  
Contains data used by the plugin, such as map frame files.

### i18n

国際化対応のための翻訳ファイルが格納されている。  
Contains translation files for internationalization.

- `easyprint_ja.ts` - 日本語翻訳ファイル / Japanese translation file
- `easyprint_en.ts` - 英語翻訳ファイル / English translation file
- `easyprint_ja.qm` - コンパイル済み日本語ファイル / Compiled Japanese file
- `easyprint_en.qm` - コンパイル済み英語ファイル / Compiled English file

### i18n

国際化対応のファイルが格納されている。
初期のプラグインでは使用されていたが、現在は更新されていない。

### images

プラグインが使用するアイコンが格納されている。

### layouts

プリントコンポーザーで使用するテンプレートが格納されている。
現状は一種でメンテはされていない。

### pictures

プラグインで使用する画像が保存されている。
主な用途は、ユーザーが選択して追加する画像アイテムである。

### preferences

用紙のサイズや方向の設定情報が格納されている。

### styles

qml ファイルが格納されている。
何に使われているかは不明。

### tools

プラグインから起動するツール類が格納されている。
現状使用されているのは doCreateSimpleMap のみである。

## ファイルコンバート

### pyuic

```cmd
pyuic4 -x ui_test.ui -o ui_test.py
pyuic4.bat -x ui_test4.ui -o ui_test4.py
```

### pyrcc

```cmd
pyrcc4 -o resources.py resources.qrc
```
