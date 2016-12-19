#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        db_ref_body.py
# Purpose:     kolekce referencnich bodu, generovani pravidelne site bodu
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#-------------------------------------------------------------------------------

import sys
import xml.etree.ElementTree as ET
from ref_bod import ReferencniBod

class ReferencniBody:

    def __init__(self):
        self.ref_body = []
 
 
    def vytvor_db(self,layer):
        "nacte referencnich bodu z XML souboru a ulozi je do listu"     
        iter = layer.getFeatures()
        for feature in iter:
            geom = feature.geometry()
            print "Feature ID %d: " % feature.id()
            r = ReferencniBod(feature.id(),geom.asPoint().x(),geom.asPoint().y())
            self.ref_body.append(r)
            
    
    def set_z_refbody(self, teren):
        "nastavi z-sourandnici pro ref.body"
        
        self.teren = teren
        ref_body_copy = []
        ref_body_copy.extend(self.ref_body)
        del self.ref_body[0:len(self.ref_body)]
    
        for rb in ref_body_copy:
            z = teren.get_z_bodu(getattr(rb, "x"), getattr(rb, "y"))
            if z != -99:
                rb.set_z(z)
                self.ref_body.append(rb)
            else :
                print "\nReferencni bod",getattr(rb, "x"), getattr(rb, "y"),"lezi mimo",
                print "rozsah terenu, bude vynechan z vypoctu \n"
        
    
    def set_z_refbody_custom(self,z):
        
        for rb in self.ref_body:
            rb.set_z(z)
            
    def generuj_sit(self, topleft_x, topleft_y, lowerright_x, lowerright_y, 
                    krok):
        "generator pravidelne site ref. bodu"
        
        pocet_sloupcu = abs(int((topleft_x - lowerright_x)/krok))
        pocet_radku = abs(int((lowerright_y - topleft_y)/krok))
        y = topleft_y
        idr = 0
    
        for m in range(pocet_radku):
            x = topleft_x
            for n in range(pocet_sloupcu):
                ref_bod = ReferencniBod(idr, x, y)
                self.ref_body.append(ref_bod)
                x += krok
                idr += idr
            y -= krok
        
        if len(self.ref_body) != 0:
            print "Sit byla uspesne vygenerovana"
        else:
            print("Nastala chyba pri generovani site, zkontrolujte zadane" +  
            "souradnice") 
    
    
    def get_ref_body(self):
        "vrati vsechny ref. body jako seznam objektu"
        
        return self.ref_body
 
 
    def print_ref_body(self):
        "vytiskne souradnice x,y,z refbodu"
        
        print "Referencni body:"
        for rb in self.ref_body:
            print getattr(rb, "x"), getattr(rb, "y"), getattr(rb, "z")


def main():
    pass

if __name__ == '__main__':
    main()

