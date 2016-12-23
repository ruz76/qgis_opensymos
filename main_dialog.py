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
        self.btnRuzice.clicked.connect(self.selectRuziceFile)
        self.btnCalculate.clicked.connect(self.calculate)
        self.btnUlozit.clicked.connect(self.selectConfigFileSave)
        self.btnNacist.clicked.connect(self.selectConfigFileOpen)
    def selectZdrojFile(self):
        self.fileDialog = QtGui.QFileDialog(self)
        self.txtZdroj.setText(self.fileDialog.getOpenFileName())
    def selectRuziceFile(self):
        self.fileDialog = QtGui.QFileDialog(self)
        self.txtRuzice.setText(self.fileDialog.getOpenFileName())
    def selectConfigFileSave(self):
        self.fileDialog = QtGui.QFileDialog(self)
        path = self.fileDialog.getSaveFileName()
        if path != '':
            f = open(path, 'w')        
            f.write(str(self.cmbLatka.currentIndex())+'\n')
            f.write(str(self.cmbTypVypoctu.currentIndex())+'\n')
            f.write(self.txtZdroj.text()+'\n')        
            f.write(str(self.cmbTeren.currentIndex())+'\n')        
            f.write(self.txtTeren2.text()+'\n')                
            f.write(str(self.cmbReceptory.currentIndex())+'\n')
            f.write(self.txtReceptoryVyska.text()+'\n')
            f.write(self.txtRuzice.text()+'\n')
            f.write(self.txtLimit.text()+'\n')
            f.close()
    def selectConfigFileOpen(self):
        self.fileDialog = QtGui.QFileDialog(self)
        path = self.fileDialog.getOpenFileName()
        if path != '':
            f = open(path, 'r')        
            self.cmbLatka.setCurrentIndex(int(f.readline()))
            self.cmbTypVypoctu.setCurrentIndex(int(f.readline()))
            self.txtZdroj.setText(f.readline().strip('\n\r'))        
            self.cmbTeren.setCurrentIndex(int(f.readline()))
            self.txtTeren2.setText(f.readline().strip('\n\r'))
            self.cmbReceptory.setCurrentIndex(int(f.readline()))
            self.txtReceptoryVyska.setText(f.readline().strip('\n\r'))
            self.txtRuzice.setText(f.readline().strip('\n\r'))
            self.txtLimit.setText(f.readline().strip('\n\r'))                
            f.close()
    def init_param(self):
        self.wd = '/tmp/' #tempfile.gettempdir()
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
    def populateTeren(self):
        root_node = QgsProject.instance().layerTreeRoot()
        tree_layers = root_node.findLayers()
        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            if layer.type() != QgsMapLayer.PluginLayer:
                try:
                    if layer.type() == QgsMapLayer.RasterLayer:
                        self.cmbTeren.addItem(layer.name())
                except:
                    pass
    def calculate(self):
        self.main = Main()
        if self.txtZdroj.text() == '':
            #TODO
            #http://portal.cenia.cz/irz/unikyPrenosy.jsp?Rok=2015&UnikOvzdusi=1&Typ=bezny&Mnozstvi=*&MetodaC=1&MetodaM=1&MetodaE=1&LatkaNazev=*&Ohlasovatel=&OhlasovatelTyp=subjektNazev&EPRTR=*&NACE=*&Lokalita=cr&Adresa=&Kraj=*&CZNUTS=*&SeskupitDle=subjektu&Razeni=vzestupne&OKEC=*
            self.showMessage(u"Nebyl vybrán soubor se zdroji. Není možno počítat.")
            return
        else:                    
            self.main.inicializuj_zdroje(self.txtZdroj.text())
        layers = QgsMapLayerRegistry.instance().mapLayersByName(self.cmbReceptory.currentText()) 
        layer = ''
        if not layers:
            self.showMessage(u"Nebyla nalezena vrstva s receptory. Není možno počítat.")
            return
        else:
            layer = layers[0]
        if layer == '':
            self.showMessage(u"Nebyla vybrána vrstva s receptory. Není možno počítat.")
            return
        else:
            self.main.inicializuj_ref_body(layer)
        fixed_h = None
        layers = QgsMapLayerRegistry.instance().mapLayersByName(self.cmbTeren.currentText()) 
        layer = ''
        if not layers:
            if self.txtTeren2.text() == '':
                self.showMessage(u"Nebyl vybrán terén ani nastavena fixní výška. Není možno počítat.")
                return
            else:
                fixed_h = float(self.txtTeren2.text())                                
        else:
            layer = layers[0]
        if layer == '':
            self.showMessage(u"Nebyla nalezena vrstva s terénem. Není možno počítat.")
            return
        else:
            self.main.inicializuj_teren(layer.source())
        if self.cmbTypVypoctu.currentIndex() == 1 or self.cmbTypVypoctu.currentIndex() == 2:
            if self.txtRuzice.text() == '':
                self.showMessage(u"Nebyla vybrána větrná růžice. Není možno počítat.")
                return
            else:
                self.main.inicializuj_vetrnou_ruzici(self.txtRuzice.text())
        if self.cmbTypVypoctu.currentIndex() == 2:
            if self.txtLimit.text() == '':
                self.showMessage(u"Nebyl nastaven limit Není možno počítat.")
                return
        self.main.vypocti(self.txtStatus, self.progressBar, self.cmbLatka.currentText(), self.cmbTypVypoctu.currentIndex() + 1, float(self.txtLimit.text()), float(self.txtReceptoryVyska.text()), fixed_h)            
        typ_zkr = ''
        if self.cmbTypVypoctu.currentIndex() == 0:
            typ_zkr = 'max'
        if self.cmbTypVypoctu.currentIndex() == 1:
            typ_zkr = 'prum'
        if self.cmbTypVypoctu.currentIndex() == 2:
            typ_zkr = 'limit'
        x = self.cmbLatka.currentText() + "_" + typ_zkr + "_" + str(uuid.uuid1())        
        x = x.replace("-", "_")
        #shppath = os.path.join(os.path.dirname(__file__), "vysledky/" + x + ".shp")
        #TODO Nastavit temp dir
        print str(tempfile.gettempdir())
        shppath = os.path.join(tempfile.gettempdir(), x + ".shp")
        self.main.export(self.cmbTypVypoctu.currentIndex() + 1,"shp",shppath)
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
    def showMessage(self, message):                    
        msgBox = QtGui.QMessageBox(self);
        msgBox.setText(message);
        msgBox.open();
