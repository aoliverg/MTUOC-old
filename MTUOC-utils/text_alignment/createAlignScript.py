import codecs
import os
import sys
import argparse

parser = argparse.ArgumentParser(description='A script to create the align script to be used with hunalign.')
parser.add_argument("--dirSL", type=str, help="The input dir containing the segmented text files for the source language.", required=True)
parser.add_argument("--dirTL", type=str, help="The input dir containing the segmented text files for the target language.", required=True)
parser.add_argument("--dirALI", type=str, help="The output dir to save the aligned files.", required=True)
parser.add_argument("--dictionary", type=str, help="The bilingual dictionary to use.", required=True)
parser.add_argument("--script", type=str, help="The name of the alignment script.", required=True)
parser.add_argument("--r1", type=str, help="The first string for name replacement.", required=False)
parser.add_argument("--r2", type=str, help="The second string for name replacement.", required=False)
parser.add_argument("--windows", action='store_true', help="Create a bat file for Windows.", required=False)

args = parser.parse_args()

windows=False
if args.windows:
    windows=True
if args.r1:
    r1=args.r1
else:
    r1=""
if args.r2:
    r2=args.r2
else:
    r2=""


dir1=args.dirSL
dir2=args.dirTL
dir3=args.dirALI
if not os.path.exists(dir3):
    os.makedirs(dir3)
outfile=args.script
hundict=args.dictionary

thisdir = os.getcwd()
files1=[]
for r, d, f in os.walk(dir1):
    for file in f:
        files1.append(file)
        
files2=[]
for r, d, f in os.walk(dir2):
    for file in f:
        files2.append(file)
sortida=codecs.open(outfile,"w",encoding="utf-8")
for file1 in files1:
    file2=file1.replace(r1,r2)
    if file2 in files2:
        fileali="ali-"+file1
        if windows:
            cadena="hunalign.exe "+hundict+" -utf -realign -text \""+dir1+"/"+file1+"\" "+"\""+dir2+"/"+file2+"\" > \""+dir3+"/"+fileali+"\""
        else:
            cadena="timeout 5m ./hunalign "+hundict+" -utf -realign -text \""+dir1+"/"+file1+"\" "+"\""+dir2+"/"+file2+"\" > \""+dir3+"/"+fileali+"\""
        print(cadena)
        sortida.write(cadena+"\n")
    else:
        print("***",file1)
        
