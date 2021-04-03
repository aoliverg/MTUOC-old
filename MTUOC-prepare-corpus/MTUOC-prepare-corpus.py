#    MTUOC-prepare-corpus
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


import codecs
import re
import sys
import importlib
import pickle
import unicodedata
import os



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


def findEMAILs(string): 
    email=re.findall('\S+@\S+', string)   
    return email
    
def findURLs(string): 
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)       
    return [x[0] for x in url] 
    
def replace_EMAILs(string,code="@EMAIL@"):
    EMAILs=findEMAILs(string)
    cont=0
    for EMAIL in EMAILs:
        string=string.replace(EMAIL,code)
    return(string)

def replace_URLs(string,code="@URL@"):
    URLs=findURLs(string)
    cont=0
    for URL in URLs:
        string=string.replace(URL,code)
    return(string)

   
def file_len(fname):
    num_lines = sum(1 for line in open(fname))
    return(num_lines)

if len(sys.argv)==1:
    configfile="config-prepare-corpus.yaml"
else:
    configfile=sys.argv[1]

stream = open(configfile, 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)


trainCorpus=config["trainCorpus"]
valCorpus=config["valCorpus"]

trainPreCorpus=config["trainPreCorpus"]
valPreCorpus=config["valPreCorpus"]

MTUOC=config["MTUOC"]
sys.path.append(MTUOC)

from MTUOC_train_truecaser import TC_Trainer
from MTUOC_truecaser import Truecaser

REPLACE_EMAILS=config["REPLACE_EMAILS"]
EMAIL_CODE=config["EMAIL_CODE"]
REPLACE_URLS=config["REPLACE_URLS"]
URL_CODE=config["URL_CODE"]


TRAIN_SL_TRUECASER=config["TRAIN_SL_TRUECASER"]
SL_DICT=config["SL_DICT"]
TRUECASE_SL=config["TRUECASE_SL"]
SL_TC_MODEL=config["SL_TC_MODEL"]

TRAIN_TL_TRUECASER=config["TRAIN_TL_TRUECASER"]
TL_DICT=config["TL_DICT"]
TRUECASE_TL=config["TRUECASE_TL"]
TL_TC_MODEL=config["TL_TC_MODEL"]

SL_TOKENIZER=config["SL_TOKENIZER"]
TL_TOKENIZER=config["TL_TOKENIZER"]

CLEAN=config["CLEAN"]
MIN_TOK=config["MIN_TOK"]
MAX_TOK=config["MAX_TOK"]

MIN_CHAR=config["MIN_CHAR"]
MAX_CHAR=config["MAX_CHAR"]

#TRAIN
'''
entrada=codecs.open(trainCorpus,"r",encoding="utf-8")
sortidaSL=codecs.open("trainSL.temp","w",encoding="utf-8")
sortidaTL=codecs.open("trainTL.temp","w",encoding="utf-8")

for linia in entrada:
    camps=linia.split("\t")
    sortidaSL.write(camps[0]+"\n")
    sortidaTL.write(camps[1]+"\n")



entrada.close()
sortidaSL.close()
sortidaTL.close()
'''
if TRAIN_SL_TRUECASER:
    SLTrainer=TC_Trainer(MTUOC, SL_TC_MODEL, "trainSL.temp", SL_DICT, SL_TOKENIZER)
    SLTrainer.train_truecaser()
    
if TRAIN_SL_TRUECASER:
    TLTrainer=TC_Trainer(MTUOC, TL_TC_MODEL, "trainTL.temp", TL_DICT, TL_TOKENIZER)
    TLTrainer.train_truecaser()

truecaserSL=Truecaser()
truecaserSL.set_MTUOCPath(MTUOC)
truecaserSL.set_tokenizer(SL_TOKENIZER)
truecaserSL.set_tc_model(SL_TC_MODEL)

truecaserTL=Truecaser()
truecaserTL.set_MTUOCPath(MTUOC)
truecaserTL.set_tokenizer(TL_TOKENIZER)
truecaserTL.set_tc_model(TL_TC_MODEL)

entrada=codecs.open(trainCorpus,"r",encoding="utf-8")
sortida=codecs.open(trainPreCorpus,"w",encoding="utf-8")

SL_TOKENIZER=MTUOC+"/"+SL_TOKENIZER
TL_TOKENIZER=MTUOC+"/"+TL_TOKENIZER

if not SL_TOKENIZER.endswith(".py"): SL_TOKENIZER=SL_TOKENIZER+".py"
spec = importlib.util.spec_from_file_location('', SL_TOKENIZER)
tokenizerSLmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tokenizerSLmod)
tokenizerSL=tokenizerSLmod.Tokenizer()
    
if not TL_TOKENIZER.endswith(".py"): TL_TOKENIZER=TL_TOKENIZER+".py"
spec = importlib.util.spec_from_file_location('', TL_TOKENIZER)
tokenizerTLmod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tokenizerTLmod)
tokenizerTL=tokenizerTLmod.Tokenizer()

for linia in entrada:
    toWrite=True
    linia=linia.rstrip()
    (l1,l2)=linia.split("\t")
    lensl=len(l1)
    lentl=len(l2)
    toksl=tokenizerSL.tokenize(l1)
    toktl=tokenizerTL.tokenize(l2)
    lentoksl=len(toksl.split(" "))
    lentoktl=len(toktl.split(" "))
    if lensl<MIN_CHAR: toWrite=False
    if lentl<MIN_CHAR: toWrite=False
    if lensl>MAX_CHAR: toWrite=False
    if lentl>MAX_CHAR: toWrite=False
    
    if lentoksl<MIN_TOK: toWrite=False
    if lentoktl<MIN_TOK: toWrite=False
    if lentoksl>MAX_TOK: toWrite=False
    if lentoktl>MAX_TOK: toWrite=False
    
    if toWrite:
        if REPLACE_EMAILS:
            l1=replace_EMAILs(l1,EMAIL_CODE)
            l2=replace_EMAILs(l2,EMAIL_CODE)
        if REPLACE_URLS:
            l1=replace_URLs(l1)
            l2=replace_URLs(l2)
        l1t=truecaserSL.truecase(l1)
        l2t=truecaserTL.truecase(l2)
        cadena=l1t+"\t"+l2t
        sortida.write(cadena+"\n")
    
entrada.close()
sortida.close()

entrada=codecs.open(valCorpus,"r",encoding="utf-8")
sortida=codecs.open(valPreCorpus,"w",encoding="utf-8")

for linia in entrada:
    toWrite=True
    linia=linia.rstrip()
    (l1,l2)=linia.split("\t")
    lensl=len(l1)
    lentl=len(l2)
    toksl=tokenizerSL.tokenize(l1)
    toktl=tokenizerTL.tokenize(l2)
    lentoksl=len(toksl.split(" "))
    lentoktl=len(toktl.split(" "))
    if lensl<MIN_CHAR: toWrite=False
    if lentl<MIN_CHAR: toWrite=False
    if lensl>MAX_CHAR: toWrite=False
    if lentl>MAX_CHAR: toWrite=False
    
    if lentoksl<MIN_TOK: toWrite=False
    if lentoktl<MIN_TOK: toWrite=False
    if lentoksl>MAX_TOK: toWrite=False
    if lentoktl>MAX_TOK: toWrite=False
    
    if toWrite:
        if REPLACE_EMAILS:
            l1=replace_EMAILs(l1,EMAIL_CODE)
            l2=replace_EMAILs(l2,EMAIL_CODE)
        if REPLACE_URLS:
            l1=replace_URLs(l1)
            l2=replace_URLs(l2)
        l1t=truecaserSL.truecase(l1)
        l2t=truecaserTL.truecase(l2)
        cadena=l1t+"\t"+l2t
        sortida.write(cadena+"\n")
    
entrada.close()
sortida.close()
