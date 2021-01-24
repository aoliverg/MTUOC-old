#    MTUOC-prepare-corpus
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
import importlib
import pickle
import unicodedata

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

def load_model(model):
    if not model=="None":
        tc_model = pickle.load(open(model, "rb" ) )
    else:
        tc_model={}
    return(tc_model)
    
def truecase(tc_model,line):
    tokens=line.split(" ")
    nsegment=[]
    cont=0
    for token in tokens:
        try:
            leadingsplitter=False
            trailingsplitter=False
            leadingjoiner=False
            trailingjoiner=False
            if token.startswith("▁"):leadingsplitter=True
            if token.endswith("▁"):trailingsplitter=True
            if token.startswith("￭"):leadingjoiner=True
            if token.endswith("￭"):trailingjoiner=True
            token=token.replace("▁","")
            token=token.replace("￭","")
            try:
                nlc=tc_model[token.lower()]["lc"]
            except:
                nlc=0
            try:
                nu1=tc_model[token.lower()]["u1"]
            except:
                nu1=0
            try:
                nuc=tc_model[token.lower()]["uc"]
            except:
                nuc=0
            
            if nlc>0 and nlc>=nu1 and nlc>=nuc:
                token=token.lower()
            elif nu1>0 and nu1>nlc and nu1>nuc:
                token=token.lower().capitalize()
            elif nuc>0 and nuc>nlc and nuc>nu1:
                token=token.upper()
            if cont==1:
                token=token.capitalize()
            if leadingsplitter:token="▁"+token
            if trailingsplitter:token=token+"▁"
            if leadingjoiner:token="￭"+token
            if trailingjoiner:token=token+"￭"
            nsegment.append(token)
        except:
            print("ERROR",sys.exc_info())
            nsegment.append(token)
    nsegment=" ".join(nsegment)
    return(nsegment)


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




if not SL_TOKENIZER.endswith(".py"): SL_TOKENIZER=SL_TOKENIZER+".py"
SL_TOKENIZER=MTUOC+"/"+SL_TOKENIZER

spec = importlib.util.spec_from_file_location('', SL_TOKENIZER)
tokenizerSL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tokenizerSL)

if not TL_TOKENIZER.endswith(".py"): TL_TOKENIZER=TL_TOKENIZER+".py"
TL_TOKENIZER=MTUOC+"/"+TL_TOKENIZER

spec = importlib.util.spec_from_file_location('', TL_TOKENIZER)
tokenizerTL = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tokenizerTL)

if TRAIN_SL_TRUECASER or TRAIN_TL_TRUECASER:
    entradaTC=codecs.open(trainCorpus,"r",encoding="utf-8")
    sortidaL1=codecs.open("trainTokSL.temp","w",encoding="utf-8")
    sortidaL2=codecs.open("trainTokTL.temp","w",encoding="utf-8")    
    for linia in entradaTC:
        linia=linia.rstrip()
        camps=linia.split("\t")
        try:
            tokensSL=tokenizerSL.tokenize(camps[0])
            tokensTL=tokenizerTL.tokenize(camps[1])
            sortidaL1.write(tokensSL+"\n")
            sortidaL2.write(tokensTL+"\n")
        except:
            pass

if TRAIN_SL_TRUECASER:
    from MTUOC_train_truecaser import train_truecaser
    train_truecaser(SL_TC_MODEL,"trainTokSL.temp",SL_DICT)
    
if TRAIN_TL_TRUECASER:
    from MTUOC_train_truecaser import train_truecaser
    train_truecaser(TL_TC_MODEL,"trainTokTL.temp",TL_DICT)

if TRUECASE_SL: sltcmodel=load_model(SL_TC_MODEL)
if TRUECASE_TL: tltcmodel=load_model(TL_TC_MODEL)


#TRAIN
entrada=codecs.open(trainCorpus,"r",encoding="utf-8")
sortida=codecs.open(trainPreCorpus,"w",encoding="utf-8")

for linia in entrada:
    linia=linia.rstrip()
    linia=unicodedata.normalize("NFKC",linia)
    camps=linia.split("\t")
    towrite=True
    if len(camps)==2:
        sl1=camps[0]
        sl2=camps[1]
        if REPLACE_EMAILS:
            sl1=replace_EMAILs(sl1,EMAIL_CODE)
            sl2=replace_EMAILs(sl2,EMAIL_CODE)
        if REPLACE_URLS:
            sl1=replace_URLs(sl1)
            sl2=replace_URLs(sl2)
    
    l1tokenized=tokenizerSL.tokenize_j(sl1)
    l2tokenized=tokenizerTL.tokenize_j(sl2)
    if CLEAN and len(l1tokenized.split(" "))<MIN_TOK:towrite=False
    if CLEAN and len(l1tokenized.split(" "))>MAX_TOK:towrite=False
    if CLEAN and len(l2tokenized.split(" "))<MIN_TOK:towrite=False
    if CLEAN and len(l2tokenized.split(" "))>MAX_TOK:towrite=False
    if not CLEAN: towrite=True
    
    if towrite and len(sl1)>0 and len(sl2)>0:
        if TRUECASE_SL:
            sl1toktrue=truecase(sltcmodel,l1tokenized)
        else:
            sl1toktrue=l1tokenized
        if TRUECASE_TL:
            sl2toktrue=truecase(tltcmodel,l2tokenized)
        else:
            sl2toktrue=l2tokenized
        
        sl1=tokenizerSL.detokenize_j(sl1toktrue)
        sl2=tokenizerTL.detokenize_j(sl2toktrue)
        cadena=sl1+"\t"+sl2
        sortida.write(cadena+"\n")
        
        
#VAL
entrada=codecs.open(valCorpus,"r",encoding="utf-8")
sortida=codecs.open(valPreCorpus,"w",encoding="utf-8")

for linia in entrada:
    linia=linia.rstrip()
    linia=unicodedata.normalize("NFKC",linia)
    camps=linia.split("\t")
    towrite=True
    if len(camps)==2:
        sl1=camps[0]
        sl2=camps[1]
        if REPLACE_EMAILS:
            sl1=replace_EMAILs(sl1)
            sl2=replace_EMAILs(sl2)
        if REPLACE_URLS:
            sl1=replace_URLs(sl1)
            sl2=replace_URLs(sl2)
    
    l1tokenized=tokenizerSL.tokenize_j(sl1)
    l2tokenized=tokenizerTL.tokenize_j(sl2)
    if CLEAN and len(l1tokenized.split(" "))<MIN_TOK:towrite=False
    if CLEAN and len(l1tokenized.split(" "))>MAX_TOK:towrite=False
    if CLEAN and len(l2tokenized.split(" "))<MIN_TOK:towrite=False
    if CLEAN and len(l2tokenized.split(" "))>MAX_TOK:towrite=False
    if not CLEAN: towrite=True
    
    if towrite and len(sl1)>0 and len(sl2)>0:
        if TRUECASE_SL:
            sl1toktrue=truecase(sltcmodel,l1tokenized)
        else:
            sl1toktrue=l1tokenized
        if TRUECASE_TL:
            sl2toktrue=truecase(tltcmodel,l2tokenized)
        else:
            sl2toktrue=l2tokenized
        
        sl1=tokenizerSL.detokenize_j(sl1toktrue)
        sl2=tokenizerTL.detokenize_j(sl2toktrue)
        cadena=sl1+"\t"+sl2
        sortida.write(cadena+"\n")
        
