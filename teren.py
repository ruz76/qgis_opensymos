#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        teren.py
# Purpose:     digitalni model terenu, vypocet nadmorske vysky na zadanych
#              souradnicich, vypocet profilu mezi dvema body, stanoveni 
#              max. vysky
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#------------------------------------------------------------------------------- 

import sys
import gdal
import numpy as np
import gdalconst

class Teren:

    def __init__(self, soubor):
        
        gdal.AllRegister()
        self.raster = gdal.Open(soubor,gdalconst.GA_ReadOnly)
        if self.raster != None:
            transform = self.raster.GetGeoTransform()
            self.radky = self.raster.RasterXSize
            self.sloupce = self.raster.RasterYSize
            self.raster_tlx = transform[0]
            self.raster_tly = transform[3]
            self.pixel_sirka = transform[1]
            self.pixel_vyska = transform[5]
            self.pixel_velikost = abs(self.pixel_sirka * self.pixel_vyska)
            self.band = self.raster.GetRasterBand(1)
        else:
            print "Soubor s terenem neexistuje"
            print "Program ukoncen"
            sys.exit()


    def get_z_bodu(self, x, y):
        "vrati z-souradnici pro bod na souradnicich y,x"

        try:
            x_pixel = int((x - self.raster_tlx)/self.pixel_sirka)
            y_pixel = int((y - self.raster_tly)/self.pixel_vyska)
            data = self.band.ReadAsArray(x_pixel, y_pixel, 1, 1)
            z = data[0, 0]
        except:
            z = -99
        
        return z

    def vypocti_vysky(self, refbody, zdroje):
        """vypocte profil vysek a urci maximalni vysku mezi i-tym zdrojem a 
        k-tym ref.bodem"""
        
        raster_matice = self.band.ReadAsArray(0, 0, self.radky, self.sloupce)
        max_vysky = []
        profily = []

        for z in zdroje:
            x_z = getattr(z,"x")
            y_z = getattr(z,"y")
            profily_radek = []
            max_vysky_radek = []

            for r in refbody:
                x_r = getattr(r,"x")
                y_r = getattr(r,"y")
                
                m_r = abs(int((self.raster_tly - y_r)/self.pixel_sirka))
                n_r = abs(int((self.raster_tlx - x_r)/self.pixel_sirka))
                m_z = abs(int((self.raster_tly - y_z)/self.pixel_sirka))
                n_z = abs(int((self.raster_tlx - x_z)/self.pixel_sirka))
                mn_r = [m_r,n_r]
                mn_z = [m_z,n_z]

                prvni_radek = min(mn_r[0], mn_z[0])
                posledni_radek = max(mn_r[0], mn_z[0])
                prvni_sloupec = min(mn_r[1], mn_z[1])
                posledni_sloupec = max(mn_r[1], mn_z[1])

    ##            vyber matici kde refbod a zdroj tvori krajni prvky
                matice = []
                for i in range(prvni_radek,posledni_radek+1):
                    matice_radek = []
                    for j in range(prvni_sloupec,posledni_sloupec+1):

                        matice_radek.append(raster_matice[i][j])
                    matice.append(matice_radek)

                if ((prvni_radek == mn_r[0] and prvni_sloupec == mn_z[1]) 
                    or (prvni_radek == mn_z[0] and prvni_sloupec == mn_r[1])):
                    matice.reverse()
                
                if m_r == m_z and n_r == n_z:
                    diag = [0]
                elif abs(m_r - m_z) == 1 or abs(n_r - n_z) == 1:
                    diag = [0]
                else:
#                    vypocti diagonalu 
                    if len(matice) == len(matice[0]):
#                        ctvercova matice
                        diag = list(np.diag(matice))
#                        obdelnikove matice
                    elif len(matice) > len(matice[0]):
                        krok_vertik = int(round(float(len(matice))/len(matice[0])))
                        diag = self.diag_obdelnik_mn(matice,krok_vertik)
                    else:
                        krok_horiz = int(round(float(len(matice[0]))/len(matice)))
                        diag = self.diag_obdelnik_nm(matice,krok_horiz)
                    
                profily_radek.append(diag)
                if len(diag)!= 1:
                    diag.pop(0)
                    diag.pop(len(diag)-1)
                max_vyska = max(diag)    
                max_vysky_radek.append(max_vyska)
                
            profily.append(profily_radek)
            max_vysky.append(max_vysky_radek)
        
        self.band = None
        self.raster = None
       
        return profily, max_vysky
    
    
    def diag_obdelnik_mn(self,matice,krok_v):
        """vrati hodnoty na priblizne uhlopricce v obdelnikove matici, 
        kde je vyssi pocet radku nez sloupcu"""
        
        diag = []
        m = 0
        for n in range(0,len(matice[0])):
            for i in range(0,krok_v):
                if len(matice)-m == 0:
                    break
                else:
                    vyska = matice[m][n]
                    diag.append(vyska)
                    m += 1
    
        return diag

    def diag_obdelnik_nm(self,matice,krok_h):
        """vrati hodnoty na priblizne uhlopricce v obdelnikove matici, 
        kde je vyssi pocet sloupcu nez radku"""
        
        diag = []
        n = 0
        for m in range(0,len(matice)):
            for i in range(0,krok_h):
                if len(matice[0])-n == 0:
                    break
                else:
                    vyska = matice[m][n]
                    diag.append(vyska)
                    n += 1
    
        return diag
    
    def get_hrana_pixel(self):
        return self.pixel_sirka


def main():
    pass

if __name__ == '__main__':
    main()   

    