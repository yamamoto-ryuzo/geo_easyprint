@echo off
REM QGISプラグイン用翻訳ファイルコンパイル
REM Translation file compilation for QGIS plugin

echo Compiling translation files...

cd /d "%~dp0"

if exist "i18n\easyprint_ja.ts" (
    echo Compiling Japanese translation...
    lrelease "i18n\easyprint_ja.ts" -qm "i18n\easyprint_ja.qm"
)

if exist "i18n\easyprint_en.ts" (
    echo Compiling English translation...
    lrelease "i18n\easyprint_en.ts" -qm "i18n\easyprint_en.qm"
)

echo Translation compilation completed!
pause
