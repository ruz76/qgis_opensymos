#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        vetrna_ruzice.py
# Purpose:     nacte vetrnou ruzici z xml a prepocte na podrobnou ruzici
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#-------------------------------------------------------------------------------

import sys
import xml.etree.ElementTree as ET

class VetrnaRuzice:
    
    def __init__(self):
        
        self.vetrna_ruzice_podrobna = []
    
    def vytvor_ruzici(self, soubor):
        
        try:
            root = ET.parse(soubor)
        except IOError:
            print "Soubor s vetrnou ruzici neexistuje"
            print "Program ukoncen"
            sys.exit()
        
        tridy = root.findall("trida_stability")
        if len(tridy) == 0:
            print "Ve vstupnim souboru s vetrnou ruzici nebyly nalezeny", 
            "zadne zaznamy"
            print "Program ukoncen"
            sys.exit() 
            
        cetnosti_prepoctene = []
        vetrna_ruzice_prepoctena = []
        
        for trida in tridy:
            bezvetri = trida.find("bezvetri")
            bezvetri_cetnost = float(bezvetri.attrib["value"])
            rychlosti = trida.findall("rychlost")
            cetnosti_r1 = []
            for rychlost in rychlosti:
                rychlost_value = float(rychlost.attrib["value"])
                cetnosti = rychlost.find("cetnosti")
                cetnosti_temp = [cetnosti.attrib["s"],cetnosti.attrib["sv"],
                                    cetnosti.attrib["v"],cetnosti.attrib["jv"],
                                    cetnosti.attrib["j"],cetnosti.attrib["jz"],
                                    cetnosti.attrib["z"],cetnosti.attrib["sz"]
                                    ]
                cetnosti_hodnoty = [float(i) for i in cetnosti_temp]
                if rychlost_value == 1.7:
                    cetnosti_r1 = cetnosti_hodnoty
                vetrna_ruzice_prepoctena.append(cetnosti_hodnoty)
                
            
            if bezvetri_cetnost != 0.0:
                suma = sum(cetnosti_r1)
                if suma != 0.0:
                    cetnosti_prepoctene_radek = []
                    for c in cetnosti_r1:
                        vaha = c/suma
                        cetnost_prepoctena = vaha*bezvetri_cetnost
                        cetnosti_prepoctene_radek.append(cetnost_prepoctena + c) 
            else:
                cetnosti_prepoctene_radek = cetnosti_r1
            cetnosti_prepoctene.append(cetnosti_prepoctene_radek)
        
        vetrna_ruzice_prepoctena[0] = cetnosti_prepoctene[0]
        vetrna_ruzice_prepoctena[3] = cetnosti_prepoctene[1]
        vetrna_ruzice_prepoctena[6] = cetnosti_prepoctene[2]
        vetrna_ruzice_prepoctena[9] = cetnosti_prepoctene[3]
        vetrna_ruzice_prepoctena[12] = cetnosti_prepoctene[4]
        
        indexy = [1, 1, 3, 11]
        for i in indexy:
            vetrna_ruzice_prepoctena.pop(i)
        
        fi_list = [0, 45, 90, 135, 180, 225, 270, 315]
        suma = 0.0
        for i in range(0, 11):
            radek = []
            for j in range(0, 360):
                if j < 315:
                    for fi in range(0, 8):
                        if j >= fi_list[fi] and j < fi_list[fi+1]: 
                            fi_1 = fi_list[fi]
                            cetnost_fi_1 = vetrna_ruzice_prepoctena[i][fi]
                            cetnost_fi_2 = vetrna_ruzice_prepoctena[i][fi+1]
                else:
                    fi_1 = fi_list[fi]
                    cetnost_fi_1 = vetrna_ruzice_prepoctena[i][7]
                    cetnost_fi_2 = vetrna_ruzice_prepoctena[i][0]
                     
                cetnost_fi = ((1.0/4500.0)*(cetnost_fi_1+((j-fi_1)/45.0)*
                                            (cetnost_fi_2-cetnost_fi_1)))  
                radek.append(cetnost_fi)
                suma += cetnost_fi            
            self.vetrna_ruzice_podrobna.append(radek)
              
    def get_vetrna_ruzice(self):
        return self.vetrna_ruzice_podrobna


def main():
    pass

if __name__ == '__main__':
    main()        
