#    txt2segmentDIR
#    Copyright (C) 2021  Antoni Oliver
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


import argparse
import sys
import re
import codecs
import nltk
import glob
import os
import srx_segmenter



#IMPORTS FOR YAML
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def segmenta(cadena):
    segmenter = srx_segmenter.SrxSegmenter(rules[srxlang],cadena)
    segments=segmenter.extract()
    resposta=[]
    for segment in segments[0]:
        segment=segment.replace("’","'")
        print(segment)
        #sortida.write(segment+"\n")
        resposta.append(segment)
    resposta="\n".join(resposta)
    return(resposta)



def translate(segment):
    return(segment[::-1])


parser = argparse.ArgumentParser(description='A script to convert an epub file into a text file with a light markup.')
parser.add_argument("-i", "--input_dir", type=str, help="The input dir containing the epub files to convert", required=True)
parser.add_argument("-o", "--output_dir", type=str, help="The output dir to save the text files", required=True)
parser.add_argument("-s", "--srxfile", type=str, help="The SRX file to use", required=True)
parser.add_argument("-l", "--srxlang", type=str, help="The language as stated in the SRX file", required=True)





args = parser.parse_args()
inDir=args.input_dir
outDir=args.output_dir
if not os.path.exists(outDir):
    os.makedirs(outDir)
srxfile=args.srxfile
srxlang=args.srxlang
rules = srx_segmenter.parse(srxfile)



files = []
for r, d, f in os.walk(inDir):
    for file in f:
        if file.endswith('.txt'):
            fullpath=os.path.join(r, file)            
            print(fullpath)
            entrada=codecs.open(fullpath,"r",encoding="utf-8")
            outfile=fullpath.replace(inDir,outDir)
            print(outfile)
            sortida=codecs.open(outfile,"w",encoding="utf-8")
            for linia in entrada:
                segments=segmenta(linia)
                if len(segments)>0:
                    sortida.write("<p>\n")
                    sortida.write(segments+"\n")
