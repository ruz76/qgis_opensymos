#-*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        ref_bod.py
# Purpose:     referencni bod
#
# Author:      Karel Psota
#
# Created:     28.04.2011
# Copyright:   (c) Karel Psota 2011
# Licence:     Simplified BSD License
#------------------------------------------------------------------------------- 

class ReferencniBod():

    def __init__(self,idr,x,y):
        self.idr = idr
        self.x = float(x)
        self.y = float(y)
               
    def set_z(self, z):
        self.z = float(z)
        

def main():
    pass

if __name__ == '__main__':
    main()