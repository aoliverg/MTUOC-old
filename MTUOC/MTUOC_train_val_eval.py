#    MTUOC-train-val-eval
#    Copyright (C) 2022  Antoni Oliver
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
from itertools import (takewhile,repeat)
import argparse


def rawincount(filename):
    f = open(filename, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024*1024) for _ in repeat(None)))
    return sum( buf.count(b'\n') for buf in bufgen )
    

def split_corpus(filename,valsize,evalsize,slcode,tlcode):
    count=rawincount(filename)
    numlinestrain=count-valsize-evalsize
    numlinestrain2=numlinestrain
    if numlinestrain<0: numlinestrain2=0
    entrada=codecs.open(filename,"r",encoding="utf-8")
    filenametrain="train-"+slcode+"-"+tlcode+".txt"
    sortidaTrain=codecs.open(filenametrain,"w",encoding="utf-8")
    filenameval="val-"+slcode+"-"+tlcode+".txt"
    sortidaVal=codecs.open(filenameval,"w",encoding="utf-8")
    filenameeval="eval-"+slcode+"-"+tlcode+".txt"
    sortidaEval=codecs.open(filenameeval,"w",encoding="utf-8")
    cont=0
    for linia in entrada:
        if cont < numlinestrain:
            sortidaTrain.write(linia)
        elif cont>= numlinestrain2 and cont < numlinestrain2+valsize:
            sortidaVal.write(linia)
        else:
            sortidaEval.write(linia)
        cont+=1
    sortidaTrain.close()
    sortidaVal.close()
    sortidaEval.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='A script to split a corpus into train, val and eval sets.')
    parser.add_argument("--corpus", type=str, help="The name and path of the input tab text corpus file.", required=True)
    parser.add_argument("--val", type=int, help="The number of lines of the val corpus.", required=True)
    parser.add_argument("--eval", type=int, help="The number of lines of the eval corpus.", required=True)
    parser.add_argument("--slcode", type=str, help="The language code of the source language.", required=True)
    parser.add_argument("--tlcode", type=str, help="The language code of the target language.", required=True)


    args = parser.parse_args()
    split_corpus(args.corpus,args.val,args.eval,args.slcode,args.tlcode)
    
    
    
    
    