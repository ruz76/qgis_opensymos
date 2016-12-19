#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        db_vysledky.py
# Purpose:     kolekce vysledku, export vysledku do shp a gml
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#-------------------------------------------------------------------------------

import os
import ogr
import xml.etree.ElementTree as ET
from xml.dom import minidom

class Vysledky:
    
    def __init__(self):
        self.vysledky = []
        
    def zapis_vysledek(self, vysledek):
        """uklada vypoctene hodnoty koncentraci spolu se souradnicemi 
        ref. bodu jako objekt do listu"""
        self.vysledek = vysledek 
        self.vysledky.append(vysledek)
     
     
    def get_vysledky(self):
        """vrati vsechny vysledky (list objektu Vysledek)"""
        
        return self.vysledky

                
    def vypis_vysledky(self,typ_vysledky):
        
        for v in self.vysledky:
            if typ_vysledky == 1:
                print "Maximalni kratkodoba koncentrace v referencnim bode:"
                print "id: ", getattr(v, "idv")
                print "x: ",getattr(v, "x"),"y: ",getattr(v, "y")
                print ("koncentrace: ", getattr(v, "c_max_tridy"), 
                       getattr(v, "c_max_total"))
            
            elif typ_vysledky == 2:
                print "-------------------------------------------------------"
                print "Prumerna dlouhodoba koncentrace v referencnim bode:"
                print "id: ", getattr(v, "idv")
                print "x: ",getattr(v, "x"),"y: ",getattr(v, "y")
                print "koncentrace: ",getattr(v, "c_prum"),
            else:
                print "-------------------------------------------------------"
                print "Doba prekroceni koncentraci v referencnim bode:"
                print "id: ",getattr(v, "idv")
                print "x: ",getattr(v, "x"),"y: ",getattr(v, "y")
                print "doba prekroceni: ",getattr(v, "doba"),
    
               
    def export(self, typ_vysledky, typ_export, soubor):
        "export vysledku do shp nebo gml"
        
        if len(self.vysledky) != 0: 
            if typ_export == "shp":
                driver = ogr.GetDriverByName('Esri Shapefile')
            elif typ_export == "gml":
                driver = ogr.GetDriverByName('GML')
        
            ds = driver.CreateDataSource(soubor)
            layer = ds.CreateLayer('refbody', geom_type=ogr.wkbPoint)
            
            field_id = ogr.FieldDefn('id', ogr.OFTInteger)
            layer.CreateField(field_id)
            
            if typ_vysledky == 1:
                field_tr1_r1 = ogr.FieldDefn('c_tr1_r1', ogr.OFTReal)
                layer.CreateField(field_tr1_r1)
                field_tr2_r1 = ogr.FieldDefn('c_tr2_r1', ogr.OFTReal)
                layer.CreateField(field_tr2_r1)
                field_tr2_r2 = ogr.FieldDefn('c_tr2_r2', ogr.OFTReal)
                layer.CreateField(field_tr2_r2)
                field_tr3_r1 = ogr.FieldDefn('c_tr3_r1', ogr.OFTReal)
                layer.CreateField(field_tr3_r1)
                field_tr3_r2 = ogr.FieldDefn('c_tr3_r2', ogr.OFTReal)
                layer.CreateField(field_tr3_r2)
                field_tr3_r3 = ogr.FieldDefn('c_tr3_r3', ogr.OFTReal)
                layer.CreateField(field_tr3_r3)
                field_tr4_r1 = ogr.FieldDefn('c_tr4_r1', ogr.OFTReal)
                layer.CreateField(field_tr4_r1)
                field_tr4_r2 = ogr.FieldDefn('c_tr4_r2', ogr.OFTReal)
                layer.CreateField(field_tr4_r2)
                field_tr4_r3 = ogr.FieldDefn('c_tr4_r3', ogr.OFTReal)
                layer.CreateField(field_tr4_r3)
                field_tr5_r1 = ogr.FieldDefn('c_tr5_r1', ogr.OFTReal)
                layer.CreateField(field_tr5_r1)
                field_tr5_r2 = ogr.FieldDefn('c_tr5_r2', ogr.OFTReal)
                layer.CreateField(field_tr5_r2)
                field_c_max = ogr.FieldDefn('c_max', ogr.OFTReal)
                layer.CreateField(field_c_max)
            
            elif typ_vysledky == 2:
                field_koncentrace = ogr.FieldDefn('c_prum', ogr.OFTReal)
                layer.CreateField(field_koncentrace)
                
            elif typ_vysledky == 3:
                field_doba = ogr.FieldDefn('doba', ogr.OFTReal)
                layer.CreateField(field_doba)
            
            for v in self.vysledky:
                
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(getattr(v, "x"), getattr(v, "y"))
                featureDefn = layer.GetLayerDefn()
                feature = ogr.Feature(featureDefn)
                feature.SetGeometry(point)
                feature.SetField('id', getattr(v, "idv"),)
                if typ_vysledky == 1:
                    c_max_tridy = getattr(v, "c_max_tridy")
                    c_max_total = getattr(v, "c_max_total")
                    feature.SetField('c_tr1_r1', c_max_tridy[0][0])
                    feature.SetField('c_tr2_r1', c_max_tridy[1][0])
                    feature.SetField('c_tr2_r2', c_max_tridy[2][0])
                    feature.SetField('c_tr3_r1', c_max_tridy[3][0])
                    feature.SetField('c_tr3_r2', c_max_tridy[4][0])
                    feature.SetField('c_tr3_r3', c_max_tridy[5][0])
                    feature.SetField('c_tr4_r1', c_max_tridy[6][0])
                    feature.SetField('c_tr4_r2', c_max_tridy[7][0])
                    feature.SetField('c_tr4_r3', c_max_tridy[8][0])
                    feature.SetField('c_tr5_r1', c_max_tridy[9][0])
                    feature.SetField('c_tr5_r2', c_max_tridy[10][0])
                    feature.SetField('c_max', c_max_total[0])
                elif typ_vysledky== 2:
                    feature.SetField('c_prum', getattr(v, "c_prum"))
                elif typ_vysledky == 3:
                    feature.SetField('doba', getattr(v, "doba"))
                layer.CreateFeature(feature)
                point.Destroy()
            feature.Destroy()
            ds.Destroy()
            print "Vysledky byly exportovany do:",os.path.abspath(soubor)
        
        else:
            print "Soubor nelze vytvorit, nejsou vysledky"


def main():
    pass

if __name__ == '__main__':
    main()
            
        
