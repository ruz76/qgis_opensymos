# -*- coding: utf-8 -*-
"""
/***************************************************************************
    Open Symos
			A QGIS plugin
 Calculates pollutants concentration according to SYMOS methodology.
 This plugin was developed by Jan Ruzicka and Katerina Ruzickova.
 The plugin is baed on Open Symos software developed by Karel Psota.
                             -------------------
        begin                : 2016-12-19
        copyright            : (C) 2016 by Jan Ruzicka, Katerina Ruzickova
        email                : jan.ruzicka.vsb@gmail.com, katerina.ruzickova@vsb.cz

 ***************************************************************************/
"""


def name():
    return "Open Symos"


def description():
    return "Calculates pollutants concentration according to SYMOS methodology"


def version():
    return "Version 0.0.1"


def icon():
    return "opensymos.png"


def qgisMinimumVersion():
    return "2.0"

def author():
    return "Jan Ruzicka, Katerina Ruzickova"

def email():
    return "jan.ruzicka.vsb@gmail.com"

def classFactory(iface):
    from opensymos import OpenSYMOS
    return OpenSYMOS(iface)
