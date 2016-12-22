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

# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from main_dialog import MainDialog

import os.path

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
        self.calculate_btn = QAction(QIcon(os.path.join(os.path.dirname(__file__), "opensymos.png")), "Calculate with SYMOS",  self.iface.mainWindow())
        QObject.connect(self.calculate_btn, SIGNAL("triggered()"), self.calculate)
        self.toolbar.addActions([self.calculate_btn])

        # Create action that will start plugin configuration
        self.action = QAction(QIcon(os.path.join(os.path.dirname(__file__), "opensymos.png")), u"Calculate with SYMOS", self.iface.mainWindow())
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
        locale = ""
        self.dlg.populateReceptory()
        #self.dlg.cmbReceptory.addItem("AAA")
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            print self.dlg.cmbLatka.currentText()
        #okno = Tk()
        #gui = Gui(okno)
        #okno.mainloop()
