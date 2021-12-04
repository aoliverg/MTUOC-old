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


parser = argparse.ArgumentParser(description='A script to segment all the files in one directory and save the segmented files in another directory.')
parser.add_argument("-i", "--input_file", type=str, help="The input file to segment.", required=True)
parser.add_argument("-o", "--output_file", type=str, help="The output segmented file.", required=True)
parser.add_argument("-s", "--srxfile", type=str, help="The SRX file to use", required=True)
parser.add_argument("-l", "--srxlang", type=str, help="The language as stated in the SRX file", required=True)





args = parser.parse_args()
infile=args.input_file
outfile=args.output_file

srxfile=args.srxfile
srxlang=args.srxlang
rules = srx_segmenter.parse(srxfile)




entrada=codecs.open(infile,"r",encoding="utf-8")
sortida=codecs.open(outfile,"w",encoding="utf-8")
for linia in entrada:
    segments=segmenta(linia)
    if len(segments)>0:
        sortida.write("<p>\n")
        sortida.write(segments+"\n")
