#    MTUOC-corpus-preprocessing
#    Copyright (C) 2022  Antoni Oliver
#
#    This program is free software: you can redistribute it and/or modifytrainCorpus
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
from datetime import datetime
import os
import codecs
import importlib
import re

import pickle

from shutil import copyfile

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

stream = open('config-corpus-preprocessing.yaml', 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)

MTUOC=config["MTUOC"]
sys.path.append(MTUOC)

from MTUOC_train_truecaser import TC_Trainer
from MTUOC_truecaser import Truecaser
from MTUOC_splitnumbers import splitnumbers
from MTUOC_sentencepiece import sentencepiece_train
from MTUOC_sentencepiece import sentencepiece_encode
from MTUOC_subwordnmt import subwordnmt_train
from MTUOC_subwordnmt import subwordnmt_encode

preprocess_type=config["preprocess_type"]

corpus=config["corpus"]
valsize=int(config["valsize"])
evalsize=int(config["evalsize"])
SLcode3=config["SLcode3"]
SLcode2=config["SLcode2"]
TLcode3=config["TLcode3"]
TLcode2=config["TLcode2"]

#VERBOSE
VERBOSE=config["VERBOSE"]
LOGFILE=config["LOG_FILE"]

REPLACE_EMAILS=config["REPLACE_EMAILS"]
EMAIL_CODE=config["EMAIL_CODE"]
REPLACE_URLS=config["REPLACE_URLS"]
URL_CODE=config["URL_CODE"]


TRAIN_SL_TRUECASER=config["TRAIN_SL_TRUECASER"]
SL_DICT=config["SL_DICT"]
TRUECASE_SL=config["TRUECASE_SL"]
SL_TC_MODEL=config["SL_TC_MODEL"]
if SL_TC_MODEL=="auto":
    SL_TC_MODEL="tc."+SLcode2

TRAIN_TL_TRUECASER=config["TRAIN_TL_TRUECASER"]
TL_DICT=config["TL_DICT"]
TRUECASE_TL=config["TRUECASE_TL"]
TL_TC_MODEL=config["TL_TC_MODEL"]
if TL_TC_MODEL=="auto":
    TL_TC_MODEL="tc."+TLcode2
    
SL_TOKENIZER=config["SL_TOKENIZER"]
if SL_TOKENIZER=="None":
    SL_TOKENIZER=None
TL_TOKENIZER=config["TL_TOKENIZER"]
if TL_TOKENIZER=="None":
    TL_TOKENIZER=None
    
CLEAN=config["CLEAN"]
MIN_TOK=config["MIN_TOK"]
MAX_TOK=config["MAX_TOK"]

MIN_CHAR=config["MIN_CHAR"]
MAX_CHAR=config["MAX_CHAR"]

#SENTENCE PIECE
SP_MODEL_PREFIX=config["SP_MODEL_PREFIX"]
MODEL_TYPE=config["MODEL_TYPE"]
#one of unigram, bpe, char, word
JOIN_LANGUAGES=config["JOIN_LANGUAGES"]
VOCAB_SIZE=config["VOCAB_SIZE"]
CHARACTER_COVERAGE=config["CHARACTER_COVERAGE"]
CHARACTER_COVERAGE_SL=config["CHARACTER_COVERAGE_SL"]
CHARACTER_COVERAGE_TL=config["CHARACTER_COVERAGE_TL"]
VOCABULARY_THRESHOLD=config["VOCABULARY_THRESHOLD"]
INPUT_SENTENCE_SIZE=config["INPUT_SENTENCE_SIZE"]
CONTROL_SYMBOLS=config["CONTROL_SYMBOLS"]
USER_DEFINED_SYMBOLS=config["USER_DEFINED_SYMBOLS"]

BOS=config["bos"]
EOS=config["eos"]

#SUBWORD NMT
LEARN_BPE=config["LEARN_BPE"]
JOINER=config["JOINER"]
SPLIT_DIGITS=config["SPLIT_DIGITS"]
NUM_OPERATIONS=config["NUM_OPERATIONS"]
APPLY_BPE=config["APPLY_BPE"]
BPE_DROPOUT=config["BPE_DROPOUT"]
BPE_DROPOUT_P=config["BPE_DROPOUT_P"]

#GUIDED ALIGNMENT
#TRAIN CORPUS
GUIDED_ALIGNMENT=config["GUIDED_ALIGNMENT"]
ALIGNER=config["ALIGNER"]
#one of eflomal, fast_align

DELETE_EXISTING=config["DELETE_EXISTING"]
DELETE_TEMP=config["DELETE_TEMP"]
SPLIT_LIMIT=config["SPLIT_LIMIT"]
#For efomal, max number of segments to align at a time

#VALID CORPUS
GUIDED_ALIGNMENT_VALID=config["GUIDED_ALIGNMENT_VALID"]
ALIGNER_VALID=config["ALIGNER_VALID"]
#one of eflomal, fast_align
#BOTH_DIRECTIONS_VALID: True 
#only for fast_align, eflomal aligns always the two directions at the same time
DELETE_EXISTING_VALID=config["DELETE_EXISTING_VALID"]


if VERBOSE:
    logfile=codecs.open(LOGFILE,"w",encoding="utf-8")

#SPLITTING CORPUS
from MTUOC_train_val_eval import split_corpus
if VERBOSE:
    cadena="Splitting corpus: "+str(datetime.now())
    print(cadena)
    logfile.write(cadena+"\n")
split_corpus(corpus,valsize,evalsize,SLcode3,TLcode3)

trainCorpus="train-"+SLcode3+"-"+TLcode3+".txt"
valCorpus="val-"+SLcode3+"-"+TLcode3+".txt"
evalCorpus="eval-"+SLcode3+"-"+TLcode3+".txt"
trainPreCorpus="train-pre-"+SLcode3+"-"+TLcode3+".txt"
valPreCorpus="val-pre-"+SLcode3+"-"+TLcode3+".txt"

evalSL="eval."+SLcode2
evalTL="eval."+TLcode2
entrada=codecs.open(evalCorpus,"r",encoding="utf-8")
sortidaSL=codecs.open(evalSL,"w",encoding="utf-8")
sortidaTL=codecs.open(evalTL,"w",encoding="utf-8")

for linia in entrada:
    linia=linia.rstrip()
    camps=linia.split("\t")
    if len(camps)>=2:
        sortidaSL.write(camps[0]+"\n")
        sortidaTL.write(camps[1]+"\n")
entrada.close()
sortidaSL.close()
sortidaTL.close()

if VERBOSE:
    cadena="Start of process: "+str(datetime.now())
    print(cadena)
    logfile.write(cadena+"\n")

#TRAIN

entrada=codecs.open(trainCorpus,"r",encoding="utf-8")
sortidaSL=codecs.open("trainSL.tmp","w",encoding="utf-8")
sortidaTL=codecs.open("trainTL.tmp","w",encoding="utf-8")
for linia in entrada:
    camps=linia.split("\t")
    if len(camps)>=2:
        sortidaSL.write(camps[0]+"\n")
        sortidaTL.write(camps[1]+"\n")
entrada.close()
sortidaSL.close()
sortidaTL.close()

if TRAIN_SL_TRUECASER:
    if VERBOSE:
        cadena="Training SL Truecaser: "+str(datetime.now())
        print(cadena)
        logfile.write(cadena+"\n")
    SLTrainer=TC_Trainer(MTUOC, SL_TC_MODEL, "trainSL.tmp", SL_DICT, SL_TOKENIZER)
    SLTrainer.train_truecaser()

if TRAIN_TL_TRUECASER:
    if VERBOSE:
        cadena="Training TL Truecaser: "+str(datetime.now())
        print(cadena)
        logfile.write(cadena+"\n")
    TLTrainer=TC_Trainer(MTUOC, TL_TC_MODEL, "trainTL.tmp", TL_DICT, TL_TOKENIZER)
    TLTrainer.train_truecaser()    

if TRUECASE_SL:
    truecaserSL=Truecaser()
    truecaserSL.set_MTUOCPath(MTUOC)
    truecaserSL.set_tokenizer(SL_TOKENIZER)
    truecaserSL.set_tc_model(SL_TC_MODEL)

if TRUECASE_TL:
    truecaserTL=Truecaser()
    truecaserTL.set_MTUOCPath(MTUOC)
    truecaserTL.set_tokenizer(TL_TOKENIZER)
    truecaserTL.set_tc_model(TL_TC_MODEL)


try:
    os.remove(trainSL.tmp)
except:
    pass
try:
    os.remove(trainTL.tmp)
except:
    pass


if not SL_TOKENIZER==None:
    SL_TOKENIZER=MTUOC+"/"+SL_TOKENIZER
    if not SL_TOKENIZER.endswith(".py"): SL_TOKENIZER=SL_TOKENIZER+".py"
    spec = importlib.util.spec_from_file_location('', SL_TOKENIZER)
    tokenizerSLmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tokenizerSLmod)
    tokenizerSL=tokenizerSLmod.Tokenizer()

if not SL_TOKENIZER==None: 
    TL_TOKENIZER=MTUOC+"/"+TL_TOKENIZER   
    if not TL_TOKENIZER.endswith(".py"): TL_TOKENIZER=TL_TOKENIZER+".py"
    spec = importlib.util.spec_from_file_location('', TL_TOKENIZER)
    tokenizerTLmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tokenizerTLmod)
    tokenizerTL=tokenizerTLmod.Tokenizer()

if VERBOSE:
    cadena="Preprocessing train corpus: "+str(datetime.now())
    print(cadena)
    logfile.write(cadena+"\n")

entrada=codecs.open(trainCorpus,"r",encoding="utf-8")
sortida=codecs.open(trainPreCorpus,"w",encoding="utf-8")

for linia in entrada:
    toWrite=True
    linia=linia.rstrip()
    camps=linia.split("\t")
    if len(camps)>=2:
        l1=camps[0]
        l2=camps[1]
        lensl=len(l1)
        lentl=len(l2)
        if not SL_TOKENIZER==None:
            toksl=tokenizerSL.tokenize(l1)
        else:
            toksl=l1
        if not TL_TOKENIZER==None:
            toktl=tokenizerTL.tokenize(l2)
        else:
            toktl=l2
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
            if TRUECASE_SL:
                l1t=truecaserSL.truecase(l1)
            else:
                l1t=l1
            if TRUECASE_TL:
                l2t=truecaserTL.truecase(l2)
            else:
                l2t=l2
            cadena=l1t+"\t"+l2t
            sortida.write(cadena+"\n")
    
entrada.close()
sortida.close()

os.remove(trainCorpus)

if VERBOSE:
    cadena="Preprocessing val corpus: "+str(datetime.now())
    print(cadena)
    logfile.write(cadena+"\n")

entrada=codecs.open(valCorpus,"r",encoding="utf-8")
sortida=codecs.open(valPreCorpus,"w",encoding="utf-8")

for linia in entrada:
    toWrite=True
    linia=linia.rstrip()
    camps=linia.split("\t")
    if len(camps)>=2:
        l1=camps[0]
        l2=camps[1]
        lensl=len(l1)
        lentl=len(l2)
        if not SL_TOKENIZER==None:
            toksl=tokenizerSL.tokenize(l1)
        else:
            toksl=l1
        if not TL_TOKENIZER==None:
            toktl=tokenizerTL.tokenize(l2)
        else:
            toktl=l2
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
            if TRUECASE_SL:
                l1t=truecaserSL.truecase(l1)
            else:
                l1t=l1
            if TRUECASE_TL:
                l2t=truecaserTL.truecase(l2)
            else:
                l2t=l2 
            cadena=l1t+"\t"+l2t
            sortida.write(cadena+"\n")
    
entrada.close()
sortida.close()

os.remove(valCorpus)

if preprocess_type=="smt":
    #train
    entrada=codecs.open(trainPreCorpus,"r",encoding="utf-8")
    nomsl="train.smt."+SLcode2
    nomtl="train.smt."+TLcode2
    sortidaSL=codecs.open(nomsl,"w",encoding="utf-8")
    sortidaTL=codecs.open(nomtl,"w",encoding="utf-8")
    for linia in entrada:
        linia=linia.rstrip()
        try:
            camps=linia.split("\t")
            SLsegment=camps[0]
            TLsegment=camps[1]
            sortidaSL.write(SLsegment+"\n")
            sortidaTL.write(TLsegment+"\n")
        except:
            pass
            
    #val
    entrada=codecs.open(valPreCorpus,"r",encoding="utf-8")
    nomsl="val.smt."+SLcode2
    nomtl="val.smt."+TLcode2
    sortidaSL=codecs.open(nomsl,"w",encoding="utf-8")
    sortidaTL=codecs.open(nomtl,"w",encoding="utf-8")
    for linia in entrada:
        linia=linia.rstrip()
        try:
            camps=linia.split("\t")
            SLsegment=camps[0]
            TLsegment=camps[1]
            sortidaSL.write(SLsegment+"\n")
            sortidaTL.write(TLsegment+"\n")
        except:
            pass
            
    
elif preprocess_type=="subwordnmt":
    print("SUBWORD NMT BPE")
    #####################
    print("Starting BPE training",datetime.now())

    entrada=codecs.open(trainPreCorpus,"r",encoding="utf-8")
    sortidaSL=codecs.open("trainPreSL.tmp","w",encoding="utf-8")
    sortidaTL=codecs.open("trainPreTL.tmp","w",encoding="utf-8")

    for linia in entrada:
        linia=linia.rstrip()
        camps=linia.split("\t")
        if len(camps)>=2:
            sortidaSL.write(camps[0]+"\n")
            sortidaTL.write(camps[1]+"\n")
        else:
            print("ERROR",camps)
    entrada.close()
    sortidaSL.close()
    sortidaTL.close()
            
    entrada=codecs.open(valPreCorpus,"r",encoding="utf-8")
    sortidaSL=codecs.open("valPreSL.tmp","w",encoding="utf-8")
    sortidaTL=codecs.open("valPreTL.tmp","w",encoding="utf-8")

    for linia in entrada:
        linia=linia.rstrip()
        camps=linia.split("\t")
        if len(camps)>=2:
            sortidaSL.write(camps[0]+"\n")
            sortidaTL.write(camps[1]+"\n")
        else:
            print("ERROR",camps)
    entrada.close()
    sortidaSL.close()
    sortidaTL.close()

    if LEARN_BPE: 
        if VERBOSE:
            print("Learning BPE",datetime.now())
        if JOIN_LANGUAGES: 
            if VERBOSE: print("JOINING LANGUAGES",datetime.now())
            subwordnmt_train("trainPreSL.tmp trainPreTL.tmp",SLcode2=SLcode2,TLcode2=TLcode2,NUM_OPERATIONS=NUM_OPERATIONS,CODES_file="codes_file")
            
        else:
            if VERBOSE: print("SL",datetime.now())
            subwordnmt_train("trainPreSL.tmp",SLcode2=SLcode2,TLcode2="",NUM_OPERATIONS=NUM_OPERATIONS,CODES_FILE="codes_file."+SLcode2)
           
            if VERBOSE: print("TL",datetime.now())
            subwordnmt_train("trainPreTL.tmp",SLcode2=TLcode2,TLcode2="",NUM_OPERATIONS=NUM_OPERATIONS,CODES_FILE="codes_file."+TLcode2)
           


    if APPLY_BPE: 
        if VERBOSE:
            print("Applying BPE",datetime.now())
        if JOIN_LANGUAGES:
            BPESL="codes_file"
            BPETL="codes_file"
        if not JOIN_LANGUAGES:
            BPESL="codes_file."+SLcode2
            BPETL="codes_file."+TLcode2
        
        subwordnmt_encode("trainPreSL.tmp","train.bpe."+SLcode2,CODES_FILE=BPESL,VOCAB_FILE="vocab_BPE."+SLcode2,VOCABULARY_THRESHOLD=VOCABULARY_THRESHOLD,JOINER=JOINER,BPE_DROPOUT=BPE_DROPOUT,BPE_DROPOUT_P=BPE_DROPOUT_P,SPLIT_DIGITS=SPLIT_DIGITS,BOS=BOS,EOS=EOS)
        subwordnmt_encode("trainPreTL.tmp","train.bpe."+TLcode2,CODES_FILE=BPETL,VOCAB_FILE="vocab_BPE."+TLcode2,VOCABULARY_THRESHOLD=VOCABULARY_THRESHOLD,JOINER=JOINER,BPE_DROPOUT=BPE_DROPOUT,BPE_DROPOUT_P=BPE_DROPOUT_P,SPLIT_DIGITS=SPLIT_DIGITS,BOS=BOS,EOS=EOS)
        
        subwordnmt_encode("valPreSL.tmp","val.bpe."+SLcode2,CODES_FILE=BPESL,VOCAB_FILE="vocab_BPE."+SLcode2,VOCABULARY_THRESHOLD=VOCABULARY_THRESHOLD,JOINER=JOINER,BPE_DROPOUT=BPE_DROPOUT,BPE_DROPOUT_P=BPE_DROPOUT_P,SPLIT_DIGITS=SPLIT_DIGITS,BOS=BOS,EOS=EOS)
        subwordnmt_encode("valPreTL.tmp","val.bpe."+TLcode2,CODES_FILE=BPETL,VOCAB_FILE="vocab_BPE."+TLcode2,VOCABULARY_THRESHOLD=VOCABULARY_THRESHOLD,JOINER=JOINER,BPE_DROPOUT=BPE_DROPOUT,BPE_DROPOUT_P=BPE_DROPOUT_P,SPLIT_DIGITS=SPLIT_DIGITS,BOS=BOS,EOS=EOS)
       
            
   
    
    if GUIDED_ALIGNMENT:
        if VERBOSE:
            cadena="Guided alignment training: "+str(datetime.now())
            print(cadena)
            logfile.write(cadena+"\n")
        if DELETE_EXISTING:
            FILE="train.bpe."+SLcode2+"."+SLcode2+".align" 
            if os.path.exists(FILE):
                os.remove(FILE)
        if ALIGNER=="fast_align":
            sys.path.append(MTUOC)
            from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
            if VERBOSE:
                cadena="Fast_align: "+str(datetime.now())
                print(cadena)
                logfile.write(cadena+"\n")
            guided_alignment_fast_align(MTUOC,"train.bpe","train.bpe",SLcode2,TLcode2,False,VERBOSE)
            
        if ALIGNER=="eflomal":
            sys.path.append(MTUOC)
            from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
            if VERBOSE:
                cadena="Eflomal: "+str(datetime.now())
                print(cadena)
                logfile.write(cadena+"\n")
            guided_alignment_eflomal(MTUOC,"train.bpe","train.bpe",SLcode2,TLcode2,SPLIT_LIMIT,VERBOSE)

    if GUIDED_ALIGNMENT_VALID:
        if VERBOSE:
                cadena="Guided alignment valid: "+str(datetime.now())
                print(cadena)
                logfile.write(cadena+"\n")
        if DELETE_EXISTING:
            FILE="val.bpe."+SLcode2+"."+SLcode2+".align" 
            if os.path.exists(FILE):
                os.remove(FILE)
            FILE="val.bpe."+TLcode2+"."+TLcode2+".align" 
            if os.path.exists(FILE):
                os.remove(FILE)            
        if ALIGNER_VALID=="fast_align":
            sys.path.append(MTUOC)
            from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
            if VERBOSE:
                cadena="Fast_align: "+str(datetime.now())
                print(cadena)
                logfile.write(cadena+"\n")
            guided_alignment_fast_align(MTUOC,"val.bpe","val.bpe",SLcode2,TLcode2,False,VERBOSE)
            
        if ALIGNER_VALID=="eflomal":
            sys.path.append(MTUOC)
            from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
            guided_alignment_eflomal(MTUOC,"val.bpe","val.bpe",SLcode2,TLcode2,SPLIT_LIMIT,VERBOSE)
            if VERBOSE:
                cadena="Eflomal: "+str(datetime.now())
                print(cadena)
                logfile.write(cadena+"\n")
    
    
    #####################
    
else:
    ###sentencepiece is default if no smt or subword-nmt is selected
    if VERBOSE:
        cadena="Start of sentencepiece process: "+str(datetime.now())
        print(cadena)
        logfile.write(cadena+"\n")

    if VERBOSE:
        cadena="Start of sentencepiece training: "+str(datetime.now())
        print(cadena)
        logfile.write(cadena+"\n")

    entrada=codecs.open(trainPreCorpus,"r",encoding="utf-8")
    sortidaSL=codecs.open("trainPreSL.tmp","w",encoding="utf-8")
    sortidaTL=codecs.open("trainPreTL.tmp","w",encoding="utf-8")

    for linia in entrada:
        linia=linia.rstrip()
        camps=linia.split("\t")
        if len(camps)>=2:
            sortidaSL.write(camps[0]+"\n")
            sortidaTL.write(camps[1]+"\n")
        else:
            print("ERROR",camps)
    entrada.close()
    sortidaSL.close()
    sortidaTL.close()
            
    entrada=codecs.open(valPreCorpus,"r",encoding="utf-8")
    sortidaSL=codecs.open("valPreSL.tmp","w",encoding="utf-8")
    sortidaTL=codecs.open("valPreTL.tmp","w",encoding="utf-8")

    for linia in entrada:
        linia=linia.rstrip()
        camps=linia.split("\t")
        if len(camps)>=2:
            sortidaSL.write(camps[0]+"\n")
            sortidaTL.write(camps[1]+"\n")
        else:
            print("ERROR",camps)
    entrada.close()
    sortidaSL.close()
    sortidaTL.close()
        
    if VERBOSE:
        cadena="Training sentencepiece: "+str(datetime.now())
        print(cadena)
        logfile.write(cadena+"\n")
    bosSP=True
    eosSP=True
    if BOS=="None": bosSP=False
    if EOS=="None": eosSP=False
    sentencepiece_train("trainPreSL.tmp","trainPreTL.tmp",SLcode2=SLcode2,TLcode2=TLcode2,JOIN_LANGUAGES=JOIN_LANGUAGES,SP_MODEL_PREFIX=SP_MODEL_PREFIX,MODEL_TYPE=MODEL_TYPE,VOCAB_SIZE=VOCAB_SIZE,CHARACTER_COVERAGE=CHARACTER_COVERAGE,INPUT_SENTENCE_SIZE=INPUT_SENTENCE_SIZE,SPLIT_DIGITS=SPLIT_DIGITS)
           
    if VERBOSE:
        cadena="Encoding corpora with sentencepiece: "+str(datetime.now())
        print(cadena)
        logfile.write(cadena+"\n")
    
    if JOIN_LANGUAGES:
        SP_MODEL_SL=SP_MODEL_PREFIX+".model"
        SP_MODEL_TL=SP_MODEL_PREFIX+".model"
    else:
        SP_MODEL_SL=SP_MODEL_PREFIX+"-"+SLcode2+".model"
        SP_MODEL_TL=SP_MODEL_PREFIX+"-"+TLcode2+".model"
    
    outfile="train.sp."+SLcode2
    vocabulary_file="vocab_file."+SLcode2
    sentencepiece_encode("trainPreSL.tmp",OUTFILE=outfile,SP_MODEL=SP_MODEL_SL,VOCABULARY=vocabulary_file,VOCABULARY_THRESHOLD=VOCABULARY_THRESHOLD,BOS=bosSP,EOS=eosSP)
    outfile="train.sp."+TLcode2
    vocabulary_file="vocab_file."+TLcode2
    sentencepiece_encode("trainPreTL.tmp",OUTFILE=outfile,SP_MODEL=SP_MODEL_TL,VOCABULARY=vocabulary_file,VOCABULARY_THRESHOLD=VOCABULARY_THRESHOLD,BOS=bosSP,EOS=eosSP)
    outfile="val.sp."+SLcode2
    vocabulary_file="vocab_file."+SLcode2
    sentencepiece_encode("valPreSL.tmp",OUTFILE=outfile,SP_MODEL=SP_MODEL_SL,VOCABULARY=vocabulary_file,VOCABULARY_THRESHOLD=VOCABULARY_THRESHOLD,BOS=bosSP,EOS=eosSP)
    outfile="val.sp."+TLcode2
    vocabulary_file="vocab_file."+TLcode2
    sentencepiece_encode("valPreTL.tmp",OUTFILE=outfile,SP_MODEL=SP_MODEL_TL,VOCABULARY=vocabulary_file,VOCABULARY_THRESHOLD=VOCABULARY_THRESHOLD,BOS=bosSP,EOS=eosSP)

    if GUIDED_ALIGNMENT:
        if VERBOSE:
            cadena="Guided alignment training: "+str(datetime.now())
            print(cadena)
            logfile.write(cadena+"\n")
        if DELETE_EXISTING:
            FILE="train.sp."+SLcode2+"."+SLcode2+".align" 
            if os.path.exists(FILE):
                os.remove(FILE)
        if ALIGNER=="fast_align":
            sys.path.append(MTUOC)
            from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
            if VERBOSE:
                cadena="Fast_align: "+str(datetime.now())
                print(cadena)
                logfile.write(cadena+"\n")
            guided_alignment_fast_align(MTUOC,"train.sp","train.sp",SLcode2,TLcode2,False,VERBOSE)
            
        if ALIGNER=="eflomal":
            sys.path.append(MTUOC)
            from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
            if VERBOSE:
                cadena="Eflomal: "+str(datetime.now())
                print(cadena)
                logfile.write(cadena+"\n")
            guided_alignment_eflomal(MTUOC,"train.sp","train.sp",SLcode2,TLcode2,SPLIT_LIMIT,VERBOSE)

    if GUIDED_ALIGNMENT_VALID:
        if VERBOSE:
                cadena="Guided alignment valid: "+str(datetime.now())
                print(cadena)
                logfile.write(cadena+"\n")
        if DELETE_EXISTING:
            FILE="val.sp."+SLcode2+"."+SLcode2+".align" 
            if os.path.exists(FILE):
                os.remove(FILE)
            FILE="val.sp."+TLcode2+"."+TLcode2+".align" 
            if os.path.exists(FILE):
                os.remove(FILE)            
        if ALIGNER_VALID=="fast_align":
            sys.path.append(MTUOC)
            from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
            if VERBOSE:
                cadena="Fast_align: "+str(datetime.now())
                print(cadena)
                logfile.write(cadena+"\n")
            guided_alignment_fast_align(MTUOC,"val.sp","val.sp",SLcode2,TLcode2,False,VERBOSE)
            
        if ALIGNER_VALID=="eflomal":
            sys.path.append(MTUOC)
            from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
            guided_alignment_eflomal(MTUOC,"val.sp","val.sp",SLcode2,TLcode2,SPLIT_LIMIT,VERBOSE)
            if VERBOSE:
                cadena="Eflomal: "+str(datetime.now())
                print(cadena)
                logfile.write(cadena+"\n")

if VERBOSE:
    cadena="End of process: "+str(datetime.now())
    print(cadena)
    logfile.write(cadena+"\n")

#DELETE TEMPORAL FILES

if DELETE_TEMP:
    if VERBOSE:
        cadena="Deleting temporal files: "+str(datetime.now())
        print(cadena)
        logfile.write(cadena+"\n")
    todeletetemp=["trainPreTL.tmp","valPreSL.tmp","valPreTL.tmp"]
    for td in todeletetemp:
        try:
            os.remove(td)
        except:
            pass
    
