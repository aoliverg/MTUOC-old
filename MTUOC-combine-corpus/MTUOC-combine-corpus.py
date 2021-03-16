#    MTUOC-combine-corpus
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
import os
import codecs
import importlib


import kenlm
from nltk.probability import FreqDist



###YAML IMPORTS
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def file_len(fname):
    num_lines = sum(1 for line in open(fname))
    return(num_lines)


if len(sys.argv)==1:
    configfile="config-combine-corpus.yaml"
else:
    configfile=sys.argv[1]

stream = open(configfile, 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)

MTUOC=config["MTUOC"]
sys.path.append(MTUOC)
from MTUOC_split_corpus import split_corpus

sys.path.append(MTUOC)
corpus_SPE=config["corpus_SPE"]
corpus_GEN=config["corpus_GEN"]
SL=config["SL"]
TL=config["TL"]
SL_tokenizer=config["SL_tokenizer"]
GEN_selected_segments=config["GEN_selected_segments"]
lval=config["lval"]
leval=config["leval"]

corpusTRAIN=config["corpusTRAIN"]
corpusVAL=config["corpusVAL"]
corpusEVAL=config["corpusEVAL"]

if SL_tokenizer.endswith(".py"): SL_tokenizer=SL_tokenizer.replace(".py","")

command="from "+SL_tokenizer+" import Tokenizer as Tokenizer"
exec(command)
tokenizer=Tokenizer()

print("STEP 1. Tokenizing SL SPE corpus")

entrada=codecs.open(corpus_SPE,"r",encoding="utf-8")
sortida=codecs.open("slcorpustok.temp","w",encoding="utf-8")

for linia in entrada:
    linia=linia.rstrip()
    camps=linia.split("\t")
    tokens=tokenizer.tokenize(camps[0])
    sortida.write(tokens+"\n")

currentdir=os.getcwd()    

print("STEP 2. Language Model Calculation")
kenlmmodel= "lm.arpa."+SL
command=MTUOC+"/lmplz -o 5 --skip_symbols --discount_fallback < "+currentdir+"/slcorpustok.temp > "+currentdir+"/"+kenlmmodel
print("*******************************")
print(command)
print("*******************************")
os.system(command)

#Scores calculation
print("STEP 3. Scores calculation")
entrada=codecs.open(corpus_GEN,"r",encoding="utf-8")
sortida=codecs.open("slcorpustok.temp","w",encoding="utf-8")
for linia in entrada:
    linia=linia.rstrip()
    camps=linia.split("\t")
    tokens=tokenizer.tokenize(camps[0])
    sortida.write(tokens+"\n")


print("STEP 4. Tokenizing SL GEN corpus")
entrada=codecs.open("slcorpustok.temp","r",encoding="utf-8")
sortida=codecs.open("scores.temp","w",encoding="utf-8")
model = kenlm.Model(kenlmmodel)
for linia in entrada:
    linia=linia.rstrip()
    perplexity=model.perplexity(linia)
    invperplexity=1/perplexity
    sortida.write(str(invperplexity)+"\n")
    
#Creation of selection file
print("STEP 5. Creation of the selection file")
entrada=codecs.open("scores.temp","r",encoding="utf-8")
sortida=codecs.open("selection.temp","w",encoding="utf-8")
fdist = FreqDist()
cont=0
for linia in entrada:
    linia=float(linia.rstrip())
    fdist[cont]=linia
    cont+=1


for element in fdist.most_common(GEN_selected_segments):
    cadena=str(element[0])+"\t"+str(element[1])
    sortida.write(cadena+"\n")
    
    
#Selection from LM
print("STEP 6. Selection from LM")
entrada=codecs.open("selection.temp","r",encoding="utf-8")

select={}

for linia in entrada:
    linia=linia.rstrip()
    camps=linia.split("\t")
    select[camps[0]]=camps[1]

entrada=codecs.open(corpus_GEN,"r",encoding="utf-8")
sortida=codecs.open("corpusselected.temp","w",encoding="utf-8")

cont=0
while 1:
    linia=entrada.readline()
    linia=linia.rstrip()
    if not linia:
        break
    if str(cont) in select:
        sortida.write(linia+"\n")
    cont+=1
    
#Split spe corpus
print("STEP 7. Splitting the corpus")
NUMOFLINES=file_len(corpus_SPE)
NLTRAIN=NUMOFLINES - lval -leval
parameters=["traintemp.temp",NLTRAIN,corpusVAL,lval,corpusEVAL,leval]
split_corpus(corpus_SPE,parameters)

command="cat traintemp.temp corpusselected.temp | sort | uniq | shuf > "+corpusTRAIN
os.system(command)


print("STEP 8. Deleting temporal files")
os.remove(kenlmmodel)
os.remove("corpusselected.temp")
os.remove("scores.temp")
os.remove("selection.temp")
os.remove("slcorpustok.temp")
os.remove("traintemp.temp")

