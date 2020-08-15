#    MTUOC_clean_parallel corpus
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

import codecs
import re
import sys
from xml.sax.saxutils import unescape
import html
import argparse
from langdetect import detect
from langdetect import detect_langs
from bs4 import BeautifulSoup
import re


def remove_tags(segment):
    #segmentnotags=re.sub('<[^/]+?>', " ",segment)
    #segmentnotags=re.sub('</.+?>', " ",segmentnotags)
    #segmentnotags=re.sub('<.+?/>', " ",segmentnotags)
    #segmentnotags=re.sub('\s+', ' ', segmentnotags).strip()
    segmentnotags=re.sub('<[^>]+>',' ',segment).strip()
    segmentnotags=re.sub(' +', ' ', segmentnotags)
    return(segmentnotags)

def norm_apos(segment):
    segmentnorm=segment.replace("’","'")
    return(segmentnorm)
    
def remove_empty(SLsegment,TLsegment):
    remove=False
    if SLsegment.strip()=="": remove=True
    if TLsegment.strip()=="": remove=True
    return(remove)

def remove_short(segment,minimum):
    remove=False
    if len(segment)<int(minimum):
        remove=True
    return(remove)

def remove_equal(SLsegment,TLsegment):
    remove=False
    if SLsegment.strip()==TLsegment.split(): remove=True
    return(remove)
    
def unescape_html(segment):
    segmentUN=html.unescape(segment)
    return(segmentUN)
    
def percentNUM(segment):
    nl=0
    nn=0
    for l in segment:
        if l.isdigit():
            nn+=1
        else:
            nl+=1
    if len(segment)>0:
        percent=100*nn/len(segment)
    else:
        percent=0
    return percent
def percentLET(segment):
    nl=0
    nn=0
    for l in segment:
        if l.isdigit():
            nn+=1
        else:
            nl+=1
    percent=100*nl/len(segment)
    return percent
    
def escapeforMoses(segment):
    segment=segment.replace("[","&lbrack;")
    segment=segment.replace("]","&rbrack;")
    segment=segment.replace("|","&verbar;")
    return(segment)
    

parser = argparse.ArgumentParser(description='MTUOC program for cleaning tab separated parallel corpora.')
parser.add_argument('-i','--in', action="store", dest="inputfile", help='The input file.',required=True)
parser.add_argument('-o','--out', action="store", dest="outputfile", help='The output file.',required=True)
parser.add_argument('-a','--all', action="store_true", dest="all", help='Performs all the cleaning with NUMPC=60 and no escapeforMoses.')
parser.add_argument('--norm_apos', action='store_true', default=False, dest='norm_apos',help='Removes html/xmltags.')
parser.add_argument('--remove_tags', action='store_true', default=False, dest='remove_tags',help='Normalizes the apostrophes.')
parser.add_argument('--unescape_html', action='store_true', default=False, dest='unescape_html',help='Normalizes the apostrophes.')
parser.add_argument('--remove_empty', action='store_true', default=False, dest='remove_empty',help='Removes segments with empty SL or TL segments.')
parser.add_argument('--remove_short', action='store', default=False, dest='remove_short',help='Removes segments with less than the given number of characters.')
parser.add_argument('--remove_equal', action='store_true', default=False, dest='remove_equal',help='Removes segments with empty SL or TL segments.')
parser.add_argument('--remove_NUMPC', action='store', default=False, dest='remove_NUMPC',help='Removes segments with a percent of numbers higher than the given.')
parser.add_argument('--escapeforMoses', action='store_true', default=False, dest='escapeforMoses',help='Replaces [ ] and | with entities.')
parser.add_argument('--stringFromFile', action='store', default=False, dest='stringFromFile',help='Removes segments containing strings from the given file (one string for line).')
parser.add_argument('--regexFromFile', action='store', default=False, dest='regexFromFile',help='Removes segments containing strings from the given file (one string for line).')
parser.add_argument('--vSL', action='store', default=False, dest='vSL',help='Verify language of source language segments.')
parser.add_argument('--vTL', action='store', default=False, dest='vTL',help='Verify language of source language segments.')
parser.add_argument('--vTNOTL', action='store', default=False, dest='vTNOTL',help='Verify target language not being a given one (to avoid having SL in TL).')
parser.add_argument('--noUPPER', action='store_true', default=False, dest='noUPPER',help='Deletes the segment is it is uppercased.')


args = parser.parse_args()

if args.all:
    args.norm_apos=True
    args.remove_tags=True
    args.unescape_html=True
    args.remove_empty=True
    args.remove_equal=True
    if not args.remove_NUMPC: args.remove_NUMPC=60
    if not args.remove_short: args.remove_short=5
entrada=codecs.open(args.inputfile,"r",encoding="utf-8")
sortida=codecs.open(args.outputfile,"w",encoding="utf-8")

if args.stringFromFile:
    sfile=codecs.open(args.stringFromFile,"r",encoding="utf-8")
    remlist=[]
    for lsfile in sfile:
        lsfile=lsfile.rstrip()
        remlist.append(lsfile)
        
if args.regexFromFile:
    regfile=codecs.open(args.regexFromFile,"r",encoding="utf-8")
    reglist=[]
    for lsfile in regfile:
        lsfile=lsfile.rstrip()
        reglist.append(lsfile)

for linia in entrada:
    toWrite=True
    linia=linia.strip()
    camps=linia.split("\t")
    if len(camps)>=1:
        slsegment=camps[0]
        tlsegment=""
    if len(camps)>=2:
        tlsegment=camps[1]
    if args.remove_tags and toWrite:
        slsegment=remove_tags(slsegment)
        tlsegment=remove_tags(tlsegment)
    if args.norm_apos and toWrite:
        slsegment=norm_apos(slsegment)
        tlsegment=norm_apos(tlsegment)
    if args.remove_empty and toWrite:
        if remove_empty(slsegment,tlsegment): toWrite=False
    if args.remove_short and toWrite:
        if remove_short(slsegment,args.remove_short): toWrite=False
    if args.remove_short and toWrite:
        if remove_short(slsegment,args.remove_short): toWrite=False
        if remove_short(tlsegment,args.remove_short): toWrite=False
    if args.remove_equal and toWrite:
        if remove_equal(slsegment,tlsegment): toWrite=False
    if args.unescape_html and toWrite:
        slsegment=unescape_html(slsegment)
        tlsegment=unescape_html(tlsegment)
    if args.remove_NUMPC and toWrite:
        if percentNUM(slsegment)>=float(args.remove_NUMPC):
            toWrite=False
        elif percentNUM(tlsegment)>=float(args.remove_NUMPC):
            toWrite=False
    if args.escapeforMoses and toWrite:
        slsegment=escapeforMoses(slsegment)
        tlsegment=escapeforMoses(tlsegment)
    if args.vSL and toWrite:
        
        try:
            sldetect=detect_langs(slsegment)
            sls=[]
            for slm in sldetect:
                camps=str(slm).split(":")
                sls.append(camps[0])
        except:
            sls=[]
        if not args.vSL in sls:
            print("NO SL MATCHING:",sldetect,slsegment)
            toWrite=False
    if args.vTL and toWrite:
        
        try:
            sldetect=detect_langs(tlsegment)
            sls=[]
            for slm in sldetect:
                camps=str(slm).split(":")
                sls.append(camps[0])
            
        except:
            sls=[]
        if not args.vTL in sls:
            print("NO TL MATCHING:",sldetect,tlsegment)
            toWrite=False
            
    if args.vTNOTL and toWrite:
        try:
            sldetect=detect_langs(tlsegment)
            sls=[]
            for slm in sldetect:
                camps=str(slm).split(":")
                sls.append(camps[0])
            
        except:
            sls=[]
        if args.vTNOTL in sls:
            print("TL MATCHING:",sldetect,tlsegment)

            toWrite=False
            


    if args.noUPPER and toWrite:
        if slsegment==slsegment.upper():
            toWrite=False
            print("DELETE UPPER:",slsegment)
        if tlsegment==tlsegment.upper():
            toWrite=False
            print("DELETE UPPER:",tlsegment)
                
    if args.stringFromFile and toWrite:
        for rmstring in remlist:
            if slsegment.find(rmstring)>-1:
                toWrite=False
                break
            if tlsegment.find(rmstring)>-1:
                toWrite=False
 
                break
                
                
                
    if args.regexFromFile and toWrite:
        for regex in reglist:
            pattern = re.compile(regex)
            
            if pattern.search(slsegment):
                toWrite=False
                break
            if pattern.search(tlsegment):
                toWrite=False
                break
            
        
        
    if toWrite:
        cadena=slsegment+"\t"+tlsegment
        sortida.write(cadena+"\n")
        
    
