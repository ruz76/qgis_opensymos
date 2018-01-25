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
        copyright            : (C) 2016 by Jan Ruzicka, Katerina Ruzickova, Radek Furmanek, Ondrej Kolodziej
        email                : jan.ruzicka.vsb@gmail.com, katerina.ruzickova@vsb.cz

 ***************************************************************************/
"""

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from main_dialog import MainDialog
from line_to_points_dialog import LineToPointsDialog
from polygon_to_points_dialog import PolygonToPointsDialog

import os.path
import urllib2
import zipfile
import tempfile

class OpenSYMOS:

    def __init__(self, iface):
        # Save reference to the QGIS interface + canvas
        self.iface = iface
        self.canvas = iface.mapCanvas()
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'opensymos_{}.qm'.format(locale))

        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create various class references
        self.marker = None
        self.completer = None
        self.previous_searches = []

    def initGui(self):
        # Create toolbar
        self.toolbar = self.iface.addToolBar("Open Symos Toolbar")
        self.toolbar.setObjectName("Open Symos Toolbar")
        self.toolbar_search = QLineEdit()
        self.toolbar_search.setMaximumWidth(100)
        self.toolbar_search.setAlignment(Qt.AlignLeft)
        self.toolbar_search.setPlaceholderText(u"Location ...")
        self.toolbar.addWidget(self.toolbar_search)
        self.toolbar_search.returnPressed.connect(self.calculate)
        self.calculate_btn = QAction(QIcon(os.path.join(os.path.dirname(__file__), "opensymos.png")), u"Počítat dle SYMOS",  self.iface.mainWindow())
        QObject.connect(self.calculate_btn, SIGNAL("triggered()"), self.calculate)
        self.show_project_btn = QAction(QIcon(os.path.join(os.path.dirname(__file__), "project.png")), u"Načíst ukázkový project", self.iface.mainWindow())
        QObject.connect(self.show_project_btn, SIGNAL("triggered()"), self.load_project)
        self.load_dem_btn = QAction(QIcon(os.path.join(os.path.dirname(__file__), "dem.png")), u"Načíst DEM", self.iface.mainWindow())
        QObject.connect(self.load_dem_btn, SIGNAL("triggered()"), self.load_dem)
        self.convert_line_to_points_btn = QAction(QIcon(os.path.join(os.path.dirname(__file__), "line_to_point.png")), u"Převést linie na body", self.iface.mainWindow())
        QObject.connect(self.convert_line_to_points_btn, SIGNAL("triggered()"), self.convert_line_to_points)
        self.convert_polygon_to_points_btn = QAction(QIcon(os.path.join(os.path.dirname(__file__), "polygon_to_point.png")), u"Převést polygony na body", self.iface.mainWindow())
        QObject.connect(self.convert_polygon_to_points_btn, SIGNAL("triggered()"), self.convert_polygon_to_points)
        self.toolbar.addActions([self.calculate_btn, self.show_project_btn, self.load_dem_btn, self.convert_line_to_points_btn, self.convert_polygon_to_points_btn])

        # Create action that will start plugin configuration
        self.action = QAction(QIcon(os.path.join(os.path.dirname(__file__), "opensymos.png")), u"Počítat dle SYMOS", self.iface.mainWindow())
        # connect the action to the run method
        self.action.triggered.connect(self.toolbar.show)

        # Add toolbar button and menu item
        self.iface.addPluginToMenu(u"&Open Symos", self.action)
		
        self.dlg = MainDialog()

    def unload(self):
		# Remove the plugin menu item and toolbar
        self.iface.removePluginMenu(u"&Open Symos", self.action)
        del self.toolbar

    def calculate(self):
        self.dlg.populateTeren()
        self.dlg.populateReceptory()
        self.dlg.populateZdroje()
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

    def convert_line_to_points(self):
        self.dlg_convert_line_to_points = LineToPointsDialog()
        self.dlg_convert_line_to_points.populateZdroje()
        self.dlg_convert_line_to_points.show()
        # Run the dialog event loop
        result = self.dlg_convert_line_to_points.exec_()

    def convert_polygon_to_points(self):
        self.dlg_convert_polygon_to_points = PolygonToPointsDialog()
        self.dlg_convert_polygon_to_points.populateZdroje()
        self.dlg_convert_polygon_to_points.show()
        # Run the dialog event loop
        result = self.dlg_convert_polygon_to_points.exec_()

    def load_project(self):
        project = QgsProject.instance()
        project.read(QFileInfo(os.path.dirname(__file__) + '/sample_data/project.qgs'))

    def load_dem(self):
        msg = u"Zvolili jste stažení DEM. To může chvíli trvat. Chcete opravdu pokračovat??"
        usercontinue = QMessageBox.question(self.iface.mainWindow(), u"Stažení DEM", msg, QMessageBox.Yes,
                                       QMessageBox.No)
        if usercontinue == QMessageBox.Yes:
            self.download_dem()
        else:
            pass

    def download_dem(self):
        # Used from ZoomToPostcode QGIS plugin
        dem_path = os.path.join(os.path.dirname(__file__), 'data/cr-gtiff-jtsk/dem_srtm.tif')
        if not os.path.exists(dem_path):
            url = "http://gisak.vsb.cz/geodata/cr-gtiff-jtsk-0.3.3.zip"
            os.umask(0002)
            try:
                req = urllib2.urlopen(url)
                total_size = int(req.info().getheader('Content-Length').strip())
                downloaded = 0
                CHUNK = 256 * 10240
                pbar = QProgressBar()
                pbar.setMinimum(0)
                pbar.setMaximum(total_size)
                zip_temp = tempfile.NamedTemporaryFile(mode='w+b', suffix='.zip', delete=False)
                zip_temp_n = zip_temp.name
                zip_temp.seek(0)
                with open(zip_temp_n, 'wb') as fp:
                    while True:
                        pbar.show()
                        chunk = req.read(CHUNK)
                        downloaded += len(chunk)
                        pbar.setValue(downloaded)
                        if not chunk:
                            break
                        fp.write(chunk)
                dem_zip = zipfile.ZipFile(zip_temp)
                dem_path = os.path.join(os.path.dirname(__file__), 'data')
                dem_zip.extractall(dem_path)
                zip_temp.close()
                self.addRasterLayer(os.path.join(os.path.dirname(__file__), 'data/cr-gtiff-jtsk/dem_srtm.tif'), "DEM_SRTM")
                self.addRasterLayer(os.path.join(os.path.dirname(__file__), 'data/cr-gtiff-jtsk/dem_gtopo30.tif'), "DEM_GTOPO30")
            except URLError:
                QMessageBox.information(self.iface.mainWindow(), "HTTP Error", "Nepodařilo se stáhnout DEM")
        else:
            self.addRasterLayer(os.path.join(os.path.dirname(__file__), 'data/cr-gtiff-jtsk/dem_srtm.tif'), "DEM_SRTM")
            self.addRasterLayer(os.path.join(os.path.dirname(__file__), 'data/cr-gtiff-jtsk/dem_gtopo30.tif'), "DEM_GTOPO30")

    def addRasterLayer(self, path, label):
        raster = QgsRasterLayer(path, label, "gdal")
        if not raster.isValid():
            QgsMessageLog.logMessage("Layer " + path + " failed to load!", "Open SYMOS")
        else:
##            crs = QgsCoordinateReferenceSystem("EPSG:4326")
            QgsMapLayerRegistry.instance().addMapLayer(raster)