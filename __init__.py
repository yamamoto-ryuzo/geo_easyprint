# -*- coding: utf-8 -*-


def name():
    return u"geo_easyprint"


def description():
    return u"デフォルトの印刷の操作が複雑なので、簡略化させた印刷プラグイン"


def version():
    return "Version 3.0.0"


def qgisMinimumVersion():
    return "3.0"


def icon():
    return "images/mActionFilePrint.png"


def classFactory(iface):
    from .easyprint import EasyPrint
    return EasyPrint(iface)
