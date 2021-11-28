import sys
import codecs
import unicodedata
import argparse
import os

def remove_control_characters(s):
    return "".join(ch for ch in s if unicodedata.category(ch)[0]!="C")

parser = argparse.ArgumentParser(description='A script to select hunalign aligments in a directory with a higner confidence than the given one into a single file..')
parser.add_argument("--inDir", type=str, help="The input dir containing the hunalign alignments.", required=True)
parser.add_argument("--outFile", type=str, help="The input fule.", required=True)
parser.add_argument("--confidence", type=float, help="The minimun confidence (the output confidence will be highet tnar the one provided..", required=True)


args = parser.parse_args()


dirin=args.inDir
fout=args.outFile
confidence=args.confidence

sortida=codecs.open(fout,"w",encoding="utf-8")

for r, d, f in os.walk(dirin):
    for file in f:
        fullname=os.path.join(dirin,file)
        
        entrada=codecs.open(fullname,"r",encoding="utf-8")


        for linia in entrada:
            linia=linia.rstrip()
            camps=linia.split("\t")
            L1seg=camps[0]
            L2seg=camps[1]
            sim=float(camps[2])
            if sim>=confidence and not L1seg=="<p>" and not L1seg=="" and not L2seg=="<p>" and not L2seg=="":
                L1seg=remove_control_characters(L1seg)
                L2seg=remove_control_characters(L2seg)
                if len(L1seg)>0 and len(L2seg)>0:
                    cadena=L1seg+"\t"+L2seg
                    sortida.write(cadena+"\n")
