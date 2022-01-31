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

def findURLs(string): 
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)       
    return [x[0] for x in url] 
    
def replace_URLs_RN(string):
    URLs=findURLs(string)
    cont=0
    equil={}
    for URL in URLs:
        cont+=1
        #cadena="www.web"+str(cont)+".com"
        cadena=str(round(random()*10000000000))
        equil[cadena]=URL
        string=string.replace(URL,cadena,1)
    return(string,equil)
    
def restore_URLs_RN(string,equils):
    for equi in equils:
        string=string.replace(equi,equils[equi],1)
    return(string)

def replace_URLs(string,code="@URL@"):
    URLs=findURLs(string)
    cont=0
    for URL in URLs:
        string=string.replace(URL,code)
    return(string)
    
def restore_URLs(SLstring,TLstring,code="@URL@"):
    URLs=findURLs(SLstring)
    for URL in URLs:
        TLstring=TLstring.replace(code,URL,1)
    return(TLstring)

if __name__ == "__main__":
    for line in sys.stdin:
        line=line.strip()
        line=replace_URLs(line)
        print(line)
