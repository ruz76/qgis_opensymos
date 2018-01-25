#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        db_zdroje_bod.py
# Purpose:     kolekce bodovych zdroju, generovani pravidelne site bodu
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#-------------------------------------------------------------------------------

import sys
import xml.etree.ElementTree as ET
from zdroj_bod import ZdrojBod

class ZdrojeBod:
    
    def __init__(self):
        
        self.zdroje = []

    def vytvor_db_vrstva(self, layer):
        "nacte udaje o zdrojich z vrstvy qgis a ulozi je do listu"
        iter = layer.getFeatures()
        for feature in iter:
            geom = feature.geometry()
            zdroj = ZdrojBod(feature.id(), geom.asPoint().x(), geom.asPoint().y(),
                                 feature["mnozstvi"], feature["vyska"],
                                 feature["teplota"], feature["prumer"],
                                 feature["rychlost"],
                                 feature["vyuziti"],
                                 feature["objem"])
            self.zdroje.append(zdroj)
    
    def vytvor_db(self,soubor):
        "nacte udaje o zdrojich z XML souboru a ulozi je do listu"
        
        try:
            root = ET.parse(soubor)
        except IOError:
            print "Soubor se zdroji neexistuje"
            print "Program ukoncen"
            sys.exit()
            
        zdroje = root.findall("zdroj")
        if len(zdroje) == 0:
            print "Ve vstupnim souboru se zdroji nebyly nalezeny zadne zaznamy"
            print "Program ukoncen"
            sys.exit() 
            
        for z in zdroje:
            prach = z.find("prach")
            prach_all = []
            if prach != None:
                prach_frakce = prach.findall("frakce")
                for p in prach_frakce:
                    frakce = []
                    prumer = float(p.attrib["prumer"])
                    hustota = float(p.attrib["hustota"])
                    zastoupeni = float(p.attrib["zastoupeni"])
                    frakce.append(prumer)
                    frakce.append(hustota)
                    frakce.append(zastoupeni)
                    prach_all.append(frakce)
                
                zdroj = ZdrojBod(z.attrib["id"],z.attrib["x"],z.attrib["y"],
                            z.attrib["mnozstvi_latky"],z.attrib["vyska_komina"],
                            z.attrib["teplota_spalin"],z.attrib["prumer_komina"],
                            z.attrib["rychlost_spalin"],
                            z.attrib["relativni_rocni_vyuziti"],
                            z.attrib["objem_spalin"],prach_all)
            else:        
                zdroj = ZdrojBod(z.attrib["id"],z.attrib["x"],z.attrib["y"],
                            z.attrib["mnozstvi_latky"],z.attrib["vyska_komina"],
                            z.attrib["teplota_spalin"],z.attrib["prumer_komina"],
                            z.attrib["rychlost_spalin"],
                            z.attrib["relativni_rocni_vyuziti"],
                            z.attrib["objem_spalin"])
            
            self.zdroje.append(zdroj)
            
            
    def set_z_zdroje(self, teren):
        "nastavi z-sourandnici pro zdroje"
        
        self.teren = teren
        zdroje_copy = []
        zdroje_copy.extend(self.zdroje)
        del self.zdroje[0:len(self.zdroje)]
        for zd in zdroje_copy:
            z = teren.get_z_bodu(getattr(zd, "x"), getattr(zd, "y"),)
            if z != -99:
                zd.set_z(z)
                self.zdroje.append(zd)
            else:
                print "\nBodovy zdroj",getattr(zd, "x"), getattr(zd, "y"),"lezi mimo",
                print "rozsah terenu, bude vynechan z vypoctu \n"
    
    
    def set_z_zdroje_custom(self,z):
        "nastaveni stejne z-souradnice pro vsechny body"
        
        for zd in self.zdroje:
            zd.set_z(z)
        

    def get_zdroje(self):
        "vrati vsechny zdroje jako seznam objektu"
        
        return self.zdroje
    
    
    def print_zdroje(self):
        "vytiskne souradnice x,y,z zdroje"
        
        print "ZdrojeBod:"
        for zd in self.zdroje:
            print getattr(zd, "x"), getattr(zd, "y"), getattr(zd, "z")
     

def main():
    pass

if __name__ == '__main__':
    main()       
