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

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os
import qgis
import uuid
import tempfile
from shutil import copyfile
from qgis.core import *
from main import Main

from PyQt4 import QtGui, uic
import processing
from processing.tools.vector import VectorWriter


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'polygon_to_point.ui'))


class PolygonToPointsDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(PolygonToPointsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.pushButtonOutput.clicked.connect(self.selectOutputFile)

    def populateZdroje(self):
        #TODO osetrit zda ma vrstva potrebne vsechny atributy
        self.comboBoxLayers.clear()
        root_node = QgsProject.instance().layerTreeRoot()
        tree_layers = root_node.findLayers()
        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            if layer.type() != QgsMapLayer.PluginLayer:
                try:
                    if layer.type() == QgsMapLayer.VectorLayer:
                        if layer.wkbType() == QGis.WKBPolygon or layer.wkbType() == QGis.WKBMultiPolygon:
                            fields = layer.pendingFields()
                            zdroj = False
                            for field in fields:
                                if field.name() == 'mnozstvi':
                                    zdroj = True
                            if zdroj:
                                self.comboBoxLayers.addItem(layer.name())
                except:
                    pass

    def selectOutputFile(self):
        self.fileDialog = QtGui.QFileDialog(self)
        self.lineEditOutput.setText(self.fileDialog.getSaveFileName())

    def convert(self, layerPolygon):
        path = self.lineEditOutput.text()
        if path[-3:] == 'shp':
            path = path[:-4]
        copyfile(os.path.join(os.path.dirname(__file__), "templates/sources.shp"), path + '.shp')
        copyfile(os.path.join(os.path.dirname(__file__), "templates/sources.shx"), path + '.shx')
        copyfile(os.path.join(os.path.dirname(__file__), "templates/sources.dbf"), path + '.dbf')
        copyfile(os.path.join(os.path.dirname(__file__), "templates/sources.prj"), path + '.prj')
        copyfile(os.path.join(os.path.dirname(__file__), "templates/sources.qpj"), path + '.qpj')
        layerPoint = QgsVectorLayer(path + '.shp', "sources_from_polygon", "ogr")
        providerPolygon = layerPolygon.dataProvider()
        providerPoint = layerPoint.dataProvider()
        # features = layer.selectedFeatures()
        features = providerPolygon.getFeatures()
        for fet in features:
            geom_count = 0
            geom = fet.geometry()
            bbox = fet.geometry().boundingBox()
            count_x = 10 * (bbox.width / bbox.height)
            count_y = 10 * (bbox.height / bbox.width)
            for x in range(0, count_x):
                for y in range(0, count_y):
                    x_coord = bbox.xMinimum() + ((bbox.width() / count_x) * x)
                    y_coord = bbox.yMinimum() + ((bbox.height() / count_y) * y)
                    pt = QgsGeometry.fromPoint(QgsPoint(float(x_coord),float(y_coord)))
                    if geom.contains(pt):
                        geom_count += 1
            for x in range(0, count_x):
                for y in range(0, count_y):
                    x_coord = bbox.xMinimum() + ((bbox.width() / count_x) * x)
                    y_coord = bbox.yMinimum() + ((bbox.height() / count_y) * y)
                    pt = QgsGeometry.fromPoint(QgsPoint(float(x_coord),float(y_coord)))
                    if geom.contains(pt):
                        fetPoint = QgsFeature()
                        fetPoint.setGeometry(pt)
                        fetPoint.setAttributes([fet["name"], float(fet["mnozstvi"]) / float(geom_count), fet["vyska"], fet["teplota"], fet["prumer"],
                             fet["rychlost"], fet["vyuziti"], float(fet["objem"]) / float(geom_count)])
                        providerPoint.addFeatures([fetPoint])
        layerPoint.commitChanges()
        QgsMapLayerRegistry.instance().addMapLayer(layerPoint)


    def accept(self):
        if self.lineEditOutput.text() != '':
            #TODO
            #http://portal.cenia.cz/irz/unikyPrenosy.jsp?Rok=2015&UnikOvzdusi=1&Typ=bezny&Mnozstvi=*&MetodaC=1&MetodaM=1&MetodaE=1&LatkaNazev=*&Ohlasovatel=&OhlasovatelTyp=subjektNazev&EPRTR=*&NACE=*&Lokalita=cr&Adresa=&Kraj=*&CZNUTS=*&SeskupitDle=subjektu&Razeni=vzestupne&OKEC=*
            layers = QgsMapLayerRegistry.instance().mapLayersByName(self.comboBoxLayers.currentText())
            layer = ''
            if not layers:
                self.showMessage(u"Nebyla nalezena vstupní vrstva. Není možno provést konverzi.")
                return
            else:
                layer = layers[0]
            if layer == '':
                self.showMessage(u"Nebyla nalezena vstupní vrstva. Není možno provést konverzi.")
                return
            else:
                self.convert(layer)
        else:
            self.showMessage(u"Nebyla vybrána výstupní vrstva. Není možno provést konverzi.")

    def showMessage(self, message):                    
        msgBox = QtGui.QMessageBox(self);
        msgBox.setText(message);
        msgBox.open();
