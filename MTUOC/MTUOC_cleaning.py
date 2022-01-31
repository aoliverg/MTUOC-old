#    MTUOC_cleaning
#    Copyright (C) 2020  Antoni Oliver
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import codecs

def clean(line1,line2,lowerlimit,upperlimit):
    cleaned=True
    nc1=len(line1.split(" "))
    nc2=len(line2.split(" "))
    if not nc1<lowerlimit and not nc2<lowerlimit and not nc1>upperlimit and not nc2>upperlimit:
        cleaned=False
        
    return(cleaned)

def print_help():
    print("MTUOC Cleaning: deletes segments with more than the given number of tokens (in the example: corpus is the rootname, source language en, target language es, lower limit 1 token, upper limit 80 tokens, ). Input file should be tokenized.")
    print("      python3 MTUOC_cleaning.py corpus en es 1 80")
    sys.exit()
    

if __name__ == "__main__":
    if sys.argv[1]=="-h" or sys.argv[1]=="--help":
        print_help()
    rootname=sys.argv[1]
    sl=sys.argv[2]
    tl=sys.argv[3]
    lowerlimit=int(sys.argv[4])
    upperlimit=int(sys.argv[5])
    if rootname.endswith("."):
        nentrada1=rootname+sl
        nentrada2=rootname+tl
        nsortida1=rootname+"clean."+sl
        nsortida2=rootname+"clean."+tl
    else:
        nentrada1=rootname+"."+sl
        nentrada2=rootname+"."+tl
        nsortida1=rootname+".clean."+sl
        nsortida2=rootname+".clean."+tl
        
    entrada1=codecs.open(nentrada1,"r",encoding="utf-8")
    entrada2=codecs.open(nentrada2,"r",encoding="utf-8")
    
    sortida1=codecs.open(nsortida1,"w",encoding="utf-8")
    sortida2=codecs.open(nsortida2,"w",encoding="utf-8")
    cont=0
    while 1:
        cont+=1
        line1=entrada1.readline()
        if not line1:
            break
        line2=entrada2.readline()
        line1=line1.strip()
        line2=line2.strip()
        cleaned=clean(line1,line2,lowerlimit,upperlimit)
        if not cleaned:
            sortida1.write(line1+"\n")
            sortida2.write(line2+"\n")
        
        
            
        
            
        
        
