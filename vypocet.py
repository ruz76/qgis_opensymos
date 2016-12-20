#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        vypocet.py
# Purpose:     vypocet koncentraci znecistujicich latek v ovzdusi, 
#              vypocet promennych a parametru obsazenych v zakladni rovnici
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#-------------------------------------------------------------------------------

import math
import numpy as np
from scipy import integrate
from vysledky import Vysledky
from vysledek import Vysledek
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class Vypocet:
    
    def __init__(self):
        
        self.db_vysledky = Vysledky()
        self.tridni_konstanty = [
                            {"trida":1,"exp_p":0.33,
                             "a_y":0.1042, "b_y":0.8844, "a_z":0.5461,
                             "b_z":0.5076, "k_s":0.6, "k_m":184.0,
                             "epsilon_koef":0.05},
                            {"trida":2,"exp_p":0.25,
                             "a_y":0.1195, "b_y":0.8930, "a_z":0.4980,
                             "b_z":0.5797, "k_s":0.78, "k_m":200.0,
                             "epsilon_koef":0.1},
                            {"trida":3,"exp_p":0.18,
                             "a_y":0.1400, "b_y":0.8986, "a_z":0.4221,
                             "b_z":0.6564, "k_s":1.0, "k_m":236.0,
                             "epsilon_koef":0.20},
                            {"trida":4,"exp_p":0.14,
                             "a_y":0.1684, "b_y":0.9018, "a_z":0.3158,
                             "b_z":0.7549, "k_s":1.14, "k_m":300.0,
                             "epsilon_koef":0.30},
                            {"trida":5,"exp_p":0.1,
                             "a_y":0.2898, "b_y":0.8831, "a_z":0.1740,
                             "b_z":0.9729, "k_s":1.24, "k_m":411.0,
                             "epsilon_koef":0.50},
                            ]
        
#        "koeficienty odstranovani"
        ku1 = 1.39*(10**(-5))
        ku2 = 1.93*(10**(-6))
        ku3 = 1.59*(10**(-8))
        
        self.koef_odstranovani = {"sirovodik":ku1, "chlorovodik":ku1, 
                                  "peroxid_vodiku":ku1, "dimetyl_sulfid":ku1, 
                            "oxid_siricity":ku2, "oxid_dusnaty":ku2, 
                            "oxid_dusicity":ku2, "amoniak":ku2, "sirouhlik":ku2, 
                            "formaldehyd":ku2, "oxid_dusny":ku3, 
                            "oxid_uhelnaty":ku3, "oxid_uhlicity":ku3, 
                            "metan":ku3, "vyssi_uhlovodiky":ku3, 
                            "metyl_chlorid":ku3, "karbonyl_sulfid":ku3}
     

#    "metody pro vypocet parametru nutnych pro hlavni vypocet" 
    
    def vypocti_azimuty(self, refbody, zdroje):
        """vypocte azimut ve kterem se nachazi i-ty zdroj pri pohledu z 
        k-teho ref.bodu, vysledky uklada do matice"""
        
        azimuty = []
        
        for z in zdroje:
            radek_matice = []
            for r in refbody:
                
                xd = getattr(z, "x") - getattr(r, "x")
                yd = getattr(z, "y") - getattr(r, "y")
                
                if xd != 0 and yd != 0:
                    a = math.atan(xd/yd)
                    azimut = math.degrees(a)+(90*(2-np.sign(xd)*
                                                  (1+np.sign(yd))))
                    radek_matice.append(azimut)
                elif yd == 0:
                    azimut = 180 - (90*np.sign(xd))
                    radek_matice.append(azimut)
                elif xd == 0:
                    azimut = 90 - (90*np.sign(yd))
                    radek_matice.append(azimut)
            azimuty.append(radek_matice)
            
        return azimuty
     
    
    def vypocti_h_h1(self, zdroj, refbod, rychlost, exp_p, ks, km, 
                     epsilon_koef, max_vyska, x):
        "vypocet efektivni vysky zdroje s korekcemi"
        
#        "urceni beta koeficientu na zaklade teploty spalin"
        if getattr(zdroj, "teplota_spalin") >= 80:
            beta_koef = 1.0
        elif (getattr(zdroj, "teplota_spalin") > 30 
              and getattr(zdroj, "teplota_spalin") < 80):
            beta_koef = (getattr(zdroj, "teplota_spalin")- 30.0)/50.0
        else:
            beta_koef = 0
        
#        "urceni rychlosti vetru ve vysce koruny komina"
        if getattr(zdroj, "vyska_komina") <= 10:
            u_h = rychlost
        elif (getattr(zdroj, "vyska_komina") > 10 
              and getattr(zdroj, "vyska_komina") < 200):
            u_h = (rychlost * 
                   (getattr(zdroj, "vyska_komina")/10.0)**exp_p)
        else:
            u_h = rychlost * (20.0**exp_p)
            
#        "urceni tepelne vydatnosti - tv"
        
        q = ((10.0**(-3.0)) * getattr(zdroj, "objem_spalin") * 1.371 * 
              (getattr(zdroj, "teplota_spalin") - 0)) 
        
#        "urceni A a B konstant"
        if q >= 20:
            a_konst = 30.0
            b_konst = 0.7
        else:
            a_konst = 90.0
            b_konst = (1.0/3.0)
        
#        "urceni prevyseni vlecky"
        if x < km*math.sqrt(q):
            prevyseni_vlecky = ( ( ( (1-beta_koef)*
                                ( (1.5*getattr(zdroj,"rychlost_spalin")*
                                getattr(zdroj,"prumer_komina"))/u_h ) ) +
                                ( beta_koef*((ks*a_konst*(q**b_konst))/u_h)) ) 
                                *(( x/(km*math.sqrt(q)) )**(2.0/3.0)) )
        else:
            prevyseni_vlecky = ( ( ( (1-beta_koef)*
                                ( (1.5*getattr(zdroj,"rychlost_spalin")*
                                getattr(zdroj,"prumer_komina"))/u_h ) ) +
                                ( beta_koef*((ks*a_konst*(q**b_konst))/u_h))) )
    
#        "urceni efektivni vysky zdroje bez korekci"
        h = getattr(zdroj, "vyska_komina") + prevyseni_vlecky
        
#        "urceni efektivni vysky zdroje s korekcemi"
        zm = max_vyska - (getattr(zdroj, "z")+getattr(zdroj, "vyska_komina"))
        
        if zm > (1-epsilon_koef)*h:
            h_1 = zm + (epsilon_koef * h)
        else:
            h_1 = h

        return h,h_1
        
        
    def vypocti_uh1(self, h_1, tridni_rychlost, exp_p):
        "urceni rychlosti vetru v efektivni vysce komina"
        
        if h_1 <= 10:
            u_h1 = tridni_rychlost
        elif (h_1 > 10 
              and h_1 < 200):
            u_h1 = tridni_rychlost * ((h_1/10.0)**exp_p)
        else:
            u_h1 = tridni_rychlost * (20.0**exp_p)
        
        return u_h1
            
    
    def vypocti_kh(self, trida, rychlost, h1, zdroj, refbod):
        """vypocet zeslabeni vlivu nizkych zdroju na znecisteni ovzdusi 
        na horach"""
        
        if getattr(refbod, "z") > (getattr(zdroj, "z")+h1):
            kh = 1 - (self.vypocti_f_z((getattr(zdroj, "z")+h1), 
                    trida, rychlost) - self.vypocti_f_z(getattr(refbod, "z"), 
                                            trida, rychlost))           
        else:
            kh = 1
        
        return kh
        
        
    def vypocti_f_z(self, z, trida, rychlost):
        "vrati f'(z) koeficient pro zvolenou nadm. vysku"
        
        if trida == 1 or trida == 2:
            f_z = 2.247 * self.vypocti_fz(z)
        elif trida == 3:
            if rychlost <= 2.5:
                f_z = 1.170 * self.vypocti_fz(z)
            elif rychlost >= 2.5 and rychlost < 7.5:
                f_z = 1.170 * self.vypocti_fz(z) * (1-((rychlost-2.5)/5.0))
            else:
                f_z = 0.0
        else:
            f_z = 0.0
        
        return f_z
            
    
    def vypocti_fz(self, z):
        "vrati odpovidajici f(z) koeficient pro zvolenou nadm. vysku"
        
        nadm_vysky = [350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 
                      900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300, 1350, 
                      1400, 1450, 1500, 1550, 1600]
        fz_all = [0.445, 0.444, 0.432, 0.401, 0.360, 0.325, 0.292, 0.261, 0.233, 
                  0.213, 0.189, 0.177, 0.157, 0.140, 0.125, 0.111, 0.092, 0.078, 
                  0.061, 0.049, 0.034, 0.025, 0.015, 0.007, 0.001, 0.0]
        rozdily = []
        
        for n in nadm_vysky:
            rozdil = abs(n - z)
            rozdily.append(rozdil)
        fz = fz_all[rozdily.index(min(rozdily))]
        
        return fz
     
  
    def vypocti_vertikal_sourad(self, refbod, zdroj, h1, l):
        
        z_r = getattr(refbod, "z")
        z_z = getattr(zdroj, "z")
        z = z_r - z_z
        list_z = []
        
        if (z + l) <= h1:
            z_ = z + l
            z__ = abs(z) + l
            z___ = z - l
            list_z.append(z_)
            list_z.append(z__)
            list_z.append(z___)
        else:
            z_ = h1
            z__ = abs(z) + h1 - z
            z___ = 2.0 * z - h1
            list_z.append(z_)
            list_z.append(z__)
            list_z.append(z___)
            
        return list_z
      
      
    def vypocti_theta(self, x, profil, hrana_pixel, refbod, zdroj):
        "vypocte koeficient vlivu terenu"
    
        z_r = getattr(refbod, "z")
        z_z = getattr(zdroj, "z")
        if z_r > z_z:
            profil_korekce = []
            for vyska in profil:
                if vyska > z_r:
                    vyska = z_r
                elif vyska < z_z:
                    vyska = z_z
                else:
                    vyska = vyska
                profil_korekce.append(float(vyska-z_z))
            krok_dmt = []
            i = 0
            for i in range(len(profil)):
                i += hrana_pixel
                krok_dmt.append(float(i))

            obsah_krivka = integrate.simps(profil_korekce, krok_dmt)
            theta = (1/(x*(z_r - z_z)))*obsah_krivka
            if theta < 0:
                theta = 0
            
        else:
            theta = 0.0
        
        return theta
        
         
    def vypocti_prach(self,prach,x_l,u_h1,z_,z__,z___,h1,sigma_z,theta):
        
        ro = 1.3
        v = (15*(10**(-6)))
        g = 9.81
        c_2 = 0.8
        c_3 = 0.6
        prach_suma = 0
        
        for p in prach:
            prumer = p[0]*(10**(-6))
            hustota = p[1]
            alfa_p = p[2]
            
            v_gi = ( (-(3*math.pi*v)/(2*c_3*prumer)) + 
                     math.sqrt((((3*math.pi*v)/(2*c_3*prumer))**2)+
                               ((c_2*hustota*g*prumer)/(c_3*ro))) )

            h_gi = (x_l*v_gi)/u_h1
            
            prach_suma += (alfa_p/100.0)*(( math.exp(-(((z_ - (h1-h_gi))**2)/
                           (2*(sigma_z**2))) )) + ( (1.0-theta) * 
                           math.exp( -(((z__ + h1+h_gi)**2)/
                           (2*(sigma_z**2))) )) + 
                           (theta*math.exp( -(((z___ + (h1+h_gi))
                           **2)/2*(sigma_z**2)))))
            
        return prach_suma
     
     
    def get_typ_latky(self, latka):
        
        plyny = ["sirovodik", "chlorovodik", "peroxid_vodiku", "dimetyl_sulfid", 
                 "oxid_siricity", "oxid_dusnaty", "oxid_dusicity", "amoniak", 
                 "sirouhlik", "formaldehyd", "oxid_dusny", "oxid_uhelnaty", 
                 "oxid_uhlicity", "metan", "vyssi_uhlovodiky", "metyl_chlorid", 
                 "karbonyl_sulfid"]
        
        if plyny.count(latka)!= 0:
            typ_latky = "plyn"
        else:
            typ_latky = "prach"

        return typ_latky
    
    
#    "hlavni metoda - vypocet znecisteni"
        
    def vypocti_koncentraci(self, status, progress, typ_vypocet, latka, refbody, zdroje, 
                            teren, vetrna_ruzice, 
                            imise_limit, vyska_l, vyska_body):
        
        refbody_local = refbody.get_ref_body()
        zdroje_local = sorted(zdroje.get_zdroje(), 
                        key=lambda zdroj:getattr(zdroj, "rel_rocni_vyuziti"), 
                        reverse=True)
        
        if typ_vypocet == 2 or typ_vypocet == 3: 
            vetrna_ruzice_local = vetrna_ruzice.get_vetrna_ruzice()
            
        typ_latka = self.get_typ_latky(latka)
        
        azimuty = self.vypocti_azimuty(refbody_local, zdroje_local)
        if teren != None:
            vysky = teren.vypocti_vysky(refbody_local, zdroje_local)
            profily = vysky[0]
            max_vysky = vysky[1]
            hrana_pixel = teren.get_hrana_pixel()
        progress.setMinimum(0)
        progress.setMaximum(len(refbody_local)-1)
        for k in range(len(refbody_local)): 
#            pro kazdy ref.bod
            progress.setValue(k)
            QCoreApplication.processEvents()
            r = refbody_local[k]
            doby_tridy = []
            c_tridy = []
            c_tridy_vyber = []
            
            for j in range(len(self.tridni_konstanty)):
#                pro kazdou rozptylovou podminku j (rychlost a smer vetru)
                trida_stability = self.tridni_konstanty[j]["trida"]
                exp_p = self.tridni_konstanty[j]["exp_p"]    
                a_y = self.tridni_konstanty[j]["a_y"]
                b_y = self.tridni_konstanty[j]["b_y"]
                a_z = self.tridni_konstanty[j]["a_z"]
                b_z = self.tridni_konstanty[j]["b_z"]

                if typ_vypocet == 1:
                
                    if self.tridni_konstanty[j]["trida"] == 1:
                        rychlosti_vetru = [1.5,1.6,1.7,1.8,1.9,2.0]
                    elif self.tridni_konstanty[j]["trida"] == 2:
                        rychlosti_vetru = [1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,
                                           2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.2,3.4,
                                           3.6,3.8,4.0,4.2,4.4,4.6,4.8,5.0]
                    elif self.tridni_konstanty[j]["trida"] == 3:
                        rychlosti_vetru = [1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,
                                           2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.2,3.4,
                                           3.6,3.8,4.0,4.2,4.4,4.6,4.8,5.0,5.2,
                                           5.4,5.6,5.8,6.0,6.2,6.4,6.6,6.8,7.0,
                                           7.5,8.0,8.5,9.0,9.5,10.0,10.5,11.0,
                                           11.5,12.0,12.5,13.0,13.5,14.0,14.5,
                                           15.0]
                    elif self.tridni_konstanty[j]["trida"] == 4:
                        rychlosti_vetru = [1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,
                                           2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.2,3.4,
                                           3.6,3.8,4.0,4.2,4.4,4.6,4.8,5.0,5.2,
                                           5.4,5.6,5.8,6.0,6.2,6.4,6.6,6.8,7.0,
                                           7.5,8.0,8.5,9.0,9.5,10.0,10.5,11.0,
                                           11.5,12.0,12.5,13.0,13.5,14.0,14.5,
                                           15.0]
                    elif self.tridni_konstanty[j]["trida"] == 5:
                        rychlosti_vetru = [1.5,1.6,1.7,1.8,1.9,2.0,2.1,2.2,2.3,
                                           2.4,2.5,2.6,2.7,2.8,2.9,3.0,3.2,3.4,
                                           3.6,3.8,4.0,4.2,4.4,4.6,4.8,5.0]
                
                else:
                    if self.tridni_konstanty[j]["trida"] == 1:
                        rychlosti_vetru = [1.7]
                    elif self.tridni_konstanty[j]["trida"] == 2:
                        rychlosti_vetru = [1.7,5.0]
                    elif self.tridni_konstanty[j]["trida"] == 3:
                        rychlosti_vetru = [1.7,5.0,11.0]
                    elif self.tridni_konstanty[j]["trida"] == 4:
                        rychlosti_vetru = [1.7,5.0,11.0]
                    elif self.tridni_konstanty[j]["trida"] == 5:
                        rychlosti_vetru = [1.7,5.0]
                
                c_rychlosti = []
                doby_rychlosti = []
                
                for rychlost in rychlosti_vetru:
                    
                    c_smery = []
                    doby_smery = []
                    
                    for fi in range(0, 360):
    #                    pro kazdy smer vetru
                        c_fi_j = 0
                        t_r_fi_j = 0
                        if typ_vypocet == 2 or typ_vypocet == 3:
                            if rychlost < 2.5:
                                if trida_stability == 1:
                                    f_fi_j = vetrna_ruzice_local[0][fi]
                                elif trida_stability == 2:
                                    f_fi_j = vetrna_ruzice_local[1][fi]
                                elif trida_stability == 3:
                                    f_fi_j = vetrna_ruzice_local[3][fi]
                                elif trida_stability == 4:
                                    f_fi_j = vetrna_ruzice_local[6][fi]
                                elif trida_stability == 5:
                                    f_fi_j = vetrna_ruzice_local[9][fi]
                            elif rychlost >= 2.5 and rychlost < 7.5:
                                if trida_stability == 2:
                                    f_fi_j = vetrna_ruzice_local[2][fi]
                                elif trida_stability == 3:
                                    f_fi_j = vetrna_ruzice_local[4][fi]
                                elif trida_stability == 4:
                                    f_fi_j = vetrna_ruzice_local[7][fi]
                                elif trida_stability == 5:
                                    f_fi_j = vetrna_ruzice_local[10][fi]
                            elif rychlost >= 7.5:
                                if trida_stability == 3:
                                    f_fi_j = vetrna_ruzice_local[5][fi]
                                elif trida_stability == 4:
                                    f_fi_j = vetrna_ruzice_local[8][fi] 
                        
                        for i in range(len(zdroje_local)):
#                            pro kazdy zdroj
                            z = zdroje_local[i]
                            azimut = azimuty[i][k]
                            if teren != None:
                                max_vyska = max_vysky[i][k]
                            else:
                                max_vyska = vyska_body
                            x = math.sqrt((((getattr(z, "x")-
                                             getattr(r, "x"))**2) + 
                                        ((getattr(z, "y") - 
                                          getattr(r, "y"))**2)) )
                            efekt_vyska_zdroje = self.vypocti_h_h1(z, 
                                r, rychlost, exp_p, 
                                self.tridni_konstanty[j]["k_s"], 
                                self.tridni_konstanty[j]["k_m"], 
                                self.tridni_konstanty[j]["epsilon_koef"], 
                                max_vyska, x)
                            h = efekt_vyska_zdroje[0]
                            h1 = efekt_vyska_zdroje[1]
                            azimut_korekce = azimut-((h1-10.0)/25.0)
                    
                            if h > 10:
                                fi_h = fi + ((h-10)/25.0)
                            else:
                                fi_h = fi
                            if fi_h > 360:
                                fi_h = fi_h - 360
                            
                            lambda_koef = abs(fi_h - azimut)
                                                           
                            if lambda_koef > 90 or lambda_koef < (-90):
                                lambda_koef_temp = 0
                            else:
                                lambda_koef_temp = lambda_koef
                            x_l = x*math.cos(math.radians(lambda_koef_temp))
                            y_l = x*math.sin(math.radians(lambda_koef_temp))
                            
                            if lambda_koef <= 20 or lambda_koef >= 340:
                                
                                if teren != None:
                                    profil = profily[i][k]
                                u_h1 = self.vypocti_uh1(h1, 
                                      rychlost, exp_p)
                                
                                if typ_latka == "prach":
                                    prach = getattr(z, "prach")
                                
                                m = getattr(z, "mnozstvi_latky")                       
                                sigma_y = a_y * (x_l**b_y)
                                sigma_z = a_z * (x_l**b_z) 
                                if typ_latka == "plyn":                                                
                                    ku = self.koef_odstranovani[latka]
                                kh = self.vypocti_kh(
                                     trida_stability, rychlost, h1, z, r)
                                list_z = self.vypocti_vertikal_sourad(r, z, h1, 
                                                                    vyska_l)
                                z_ = list_z[0]
                                z__ = list_z[1]
                                z___ = list_z[2]
                                vs = getattr(z, "objem_spalin")
                                if teren != None:
                                    theta = self.vypocti_theta(x, profil, 
                                                               hrana_pixel, r, 
                                                               z)
                                else:
                                    theta = 0
                                
                                if typ_vypocet == 2 or typ_vypocet == 3:
                                    alfa = getattr(z, "rel_rocni_vyuziti")     
                                
                                if typ_latka == "plyn":
                                    c_i_fi_j = ( ((10.0**6.0*m)/
                                    ((2*math.pi*sigma_y*sigma_z*u_h1)+vs)) * 
                                    math.exp( (-(y_l)**2)/(2*(sigma_y**2)) ) * 
                                    math.exp( (-ku)*(x_l/u_h1) ) * kh * 
                                    (( math.exp(-(((z_ - h1)**2)/
                                    (2*(sigma_z**2))) )) + ( (1.0-theta) * 
                                    math.exp( -(((z__ + h1)**2)/
                                    (2*(sigma_z**2))) )) + 
                                    (theta*math.exp( -(((z___ + h1)**2)/
                                    2*(sigma_z**2))))) )
                                elif typ_latka == "prach":   
                                    c_i_fi_j = ( ((10.0**6.0*m)/
                                    ((2*math.pi*sigma_y*sigma_z*u_h1)+vs)) * 
                                    math.exp( (-(y_l)**2)/(2*(sigma_y**2)) ) * 
                                    kh * self.vypocti_prach(prach, x_l, u_h1, 
                                                            z_, z__, z___, h1, 
                                                            sigma_z, theta) )
                                        
                                if typ_vypocet == 1:
                                    c_fi_j = c_fi_j + c_i_fi_j
                                elif typ_vypocet == 2:
                                    c_fi_j = c_fi_j + (c_i_fi_j*alfa)
                                elif typ_vypocet == 3:
                                    if c_fi_j > imise_limit:
                                        t_r_i_fi_j = alfa *f_fi_j
                                        t_r_fi_j = t_r_fi_j + t_r_i_fi_j 
                        
                        if typ_vypocet == 1:
                            c_fi_j_data = [round(c_fi_j,6),trida_stability,
                                           rychlost,fi]
                            c_smery.append(c_fi_j_data)
                        elif typ_vypocet == 2:
                            c_f_fi_j = c_fi_j * f_fi_j
                            c_smery.append(c_f_fi_j)
                        elif typ_vypocet == 3:
                            doby_smery.append(t_r_fi_j)
                            
                            
                    if typ_vypocet == 1:
                        c_rychlosti.append(max(c_smery))
                    elif typ_vypocet == 2:
                        c_rychlosti.append(sum(c_smery))
                    elif typ_vypocet == 3:
                        doby_rychlosti.append(sum(doby_smery))    
                    
                    if typ_vypocet == 1:
                        if trida_stability == 1 and rychlost == 1.7:
                            c_tridy_vyber.append(max(c_smery))
                        elif (trida_stability == 2 and rychlost == 1.7 or 
                              rychlost == 5.0):
                            c_tridy_vyber.append(max(c_smery))
                        elif (trida_stability == 3 and rychlost == 1.7 or 
                              rychlost == 5.0 or rychlost == 11.0):
                            c_tridy_vyber.append(max(c_smery))
                        elif (trida_stability == 4 and rychlost == 1.7 or 
                              rychlost == 5.0 or rychlost == 11.0):
                            c_tridy_vyber.append(max(c_smery))
                        elif (trida_stability == 5 and rychlost == 1.7 or 
                              rychlost == 5.0):
                            c_tridy_vyber.append(max(c_smery))
                    
                if typ_vypocet == 1:
                    c_tridy.append(max(c_rychlosti))
                elif typ_vypocet == 2:
                    c_tridy.append(sum(c_rychlosti))
                elif typ_vypocet == 3:
                    doby_tridy.append(sum(doby_rychlosti))
                    
            if typ_vypocet == 1:
                c_max_total = max(c_tridy)
            elif typ_vypocet == 2:
                c_prum = round(sum(c_tridy),6)
            elif typ_vypocet == 3:
                doba_prekroceni = 8760*sum(doby_tridy) 
            
            vysledek = Vysledek()
            if typ_vypocet == 1:
                vysledek.typ_max(k, getattr(r, "x"), getattr(r, "y"), 
                                 c_tridy_vyber, c_max_total)
            elif typ_vypocet == 2:
                vysledek.typ_prum(k, getattr(r, "x"), getattr(r, "y"), 
                                  c_prum)
            elif typ_vypocet == 3:
                vysledek.typ_doba(k, getattr(r, "x"), getattr(r, "y"), 
                                  round(doba_prekroceni,3))
            self.db_vysledky.zapis_vysledek(vysledek)
    
    
    def export(self, typ_vysledky, typ_export, soubor):
        self.db_vysledky.export(typ_vysledky, typ_export, soubor)
    
        
    def get_vysledky(self):
        return self.db_vysledky.get_vysledky()
    
    def vypis_vysledky(self,typ_vysledky):
        self.db_vysledky.vypis_vysledky(typ_vysledky)
        
    
    
def main():
    pass

if __name__ == '__main__':
    main()
   
