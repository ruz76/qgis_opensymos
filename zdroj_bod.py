#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        zdroj_bod.py
# Purpose:     bodovy zdroj
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#-------------------------------------------------------------------------------

class ZdrojBod:
    
    def __init__(self, idz, x, y, mnozstvi_latky, vyska_komina, teplota_spalin, 
                 prumer_komina, rychlost_spalin, rel_rocni_vyuziti, 
                 objem_spalin, prach=None ):
        
        self.idz = idz
        self.x = float(x)
        self.y = float(y)
        self.mnozstvi_latky = float(mnozstvi_latky)
        self.vyska_komina = float(vyska_komina)
        self.teplota_spalin = float(teplota_spalin)
        self.prumer_komina = float(prumer_komina)
        self.rychlost_spalin = float(rychlost_spalin)
        self.objem_spalin = float(objem_spalin)
        self.rel_rocni_vyuziti = float(rel_rocni_vyuziti)
        self.prach = prach
    
    
    def set_z(self, z):
        self.z = float(z)
        
    def get_z(self):
        return self.z
    
        
def main():
    pass

if __name__ == '__main__':
    main()
