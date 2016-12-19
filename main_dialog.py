# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BabaDialog
                                 A QGIS plugin
 Baba
                             -------------------
        begin                : 2016-12-19
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Baba
        email                : baba@baba.cz
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
from qgis.core import *
from main import Main

from PyQt4 import QtGui, uic

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'main_dialog_base.ui'))


class MainDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(MainDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.init_param()
        self.setupUi(self)
        self.btnZdroj.clicked.connect(self.selectZdrojFile)
        self.btnTeren.clicked.connect(self.selectTerenFile)
        self.btnRuzice.clicked.connect(self.selectRuziceFile)
        self.btnCalculate.clicked.connect(self.calculate)
    def selectZdrojFile(self):
        self.fileDialog = QtGui.QFileDialog(self)
        self.txtZdroj.setText(self.fileDialog.getOpenFileName())
    def selectTerenFile(self):
        self.fileDialog = QtGui.QFileDialog(self)
        self.txtTeren.setText(self.fileDialog.getOpenFileName())		
    def selectRuziceFile(self):
        self.fileDialog = QtGui.QFileDialog(self)
        self.txtRuzice.setText(self.fileDialog.getOpenFileName())				
    def init_param(self):
        self.main = Main()
        self.zdroje = None
        self.teren = None
        self.ref_body = None
        self.vetrna_ruzice = None
        self.vyska_body = None
        self.imise_limit = None
        self.vyska_l = 0.0
        self.typ_vypocet_select = None
        self.latka_prom_select = None
    def populateReceptory(self):
        root_node = QgsProject.instance().layerTreeRoot()
        tree_layers = root_node.findLayers()
        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            if layer.type() != QgsMapLayer.PluginLayer:
                try:
                    if layer.type() == QgsMapLayer.VectorLayer:
                        self.cmbReceptory.addItem(layer.name())
                except:
                    pass
    def calculate(self):					
		self.main.inicializuj_zdroje(self.txtZdroj.text())
		layer = QgsMapLayerRegistry.instance().mapLayersByName(self.cmbReceptory.currentText())[0]
		self.main.inicializuj_ref_body(layer)
		self.main.inicializuj_teren(self.txtTeren.text())
		self.main.vypocti(self.cmbLatka.currentText(), 1, self.imise_limit, self.vyska_l, self.vyska_body)					
		x = self.cmbLatka.currentText() + "_" + str(uuid.uuid1())		
		x = x.replace("-", "_")
		#shppath = os.path.join(os.path.dirname(__file__), "vysledky/" + x + ".shp")
		shppath = "/tmp/" + x + ".shp"
		self.main.export(1,"shp",shppath)
		layer = QgsVectorLayer(shppath, x, "ogr")
		if not layer.isValid():
			print "Layer failed to load!"
		else:
			QgsMapLayerRegistry.instance().addMapLayer(layer)
    def getReceptory(self):					
        layer = QgsMapLayerRegistry.instance().mapLayersByName(self.cmbReceptory.currentText())[0]
        iter = layer.getFeatures()
        for feature in iter:
			geom = feature.geometry()
			print geom.asPoint().x()
			print geom.asPoint().y()
			print "Feature ID %d: " % feature.id()