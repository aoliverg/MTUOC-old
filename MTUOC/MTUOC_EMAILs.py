#    MTUOC_URLs
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

import re
import sys
from random import seed
from random import random

def findEMAILs(string): 
    email=re.findall('\S+@\S+', string)   
    return email
    
def replace_EMAILs_RN(string):
    seed(1)
    EMAILs=findEMAILs(string)
    cont=0
    equil={}
    for EMAIL in EMAILs:
        cont+=1
        #cadena=str(cont)+"@email"+str(cont)+".com"
        cadena=str(round(random()*10000000000))
        equil[cadena]=EMAIL
        string=string.replace(EMAIL,cadena,1)
    return(string,equil)
    
def restore_EMAILs_RN(string,equils):
    for equi in equils:
        string=string.replace(equi,equils[equi],1)
    return(string)
    
def replace_EMAILs(string,code="@EMAIL@"):
    EMAILs=findEMAILs(string)
    cont=0
    for EMAIL in EMAILs:
        string=string.replace(EMAIL,code)
    return(string)
    
def restore_EMAILs(SLstring,TLstring,code="@EMAIL@"):
    EMAILs=findEMAILs(SLstring)
    for EMAIL in EMAILs:
        TLstring=TLstring.replace(code,EMAIL,1)
    return(TLstring)
    
if __name__ == "__main__":
    for line in sys.stdin:
        line=line.strip()
        line=replace_EMAILs(line)
        print(line)
