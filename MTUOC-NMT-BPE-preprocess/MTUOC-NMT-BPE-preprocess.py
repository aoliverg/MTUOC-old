#    MTUOC-NMT-SP-preprocess
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


import sys
from datetime import datetime
import os
import codecs
import importlib
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

stream = open('config-NMT-BPE-preprocess.yaml', 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)

VERBOSE=config["VERBOSE"]

MTUOC=config["MTUOC"]
sys.path.append(MTUOC)

trainPreCorpus=config["trainPreCorpus"]
valPreCorpus=config["valPreCorpus"]

SL=config["SL"]
TL=config["TL"]

#VERBOSE
VERBOSE=config["VERBOSE"]

#SUBWORD-NMT
LEARN_BPE=config["LEARN_BPE"]
joiner=config["joiner"]
SPLIT_NUMBERS=config["SPLIT_NUMBERS"]
bos=config["bos"]
bos_annotate=config["bos_annotate"]
eos=config["eos"]
eos_annotate=config["eos_annotate"]
NUM_OPERATIONS=config["NUM_OPERATIONS"]
JOIN_LANGUAGES=config["JOIN_LANGUAGES"]
APPLY_BPE=config["APPLY_BPE"]
VOCABULARY_THRESHOLD=config["VOCABULARY_THRESHOLD"]
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

if SPLIT_NUMBERS:
    from MTUOC_splitnumbers import splitnumbers

if VERBOSE:
    print("Start of process",datetime.now())

#BPE

print("Starting BPE training",datetime.now())

entrada=codecs.open(trainPreCorpus,"r",encoding="utf-8")
sortidaSL=codecs.open("trainPreSL.temp","w",encoding="utf-8")
sortidaTL=codecs.open("trainPreTL.temp","w",encoding="utf-8")

for linia in entrada:
    linia=linia.rstrip()
    camps=linia.split("\t")
    if len(camps)==2:
        sortidaSL.write(camps[0]+"\n")
        sortidaTL.write(camps[1]+"\n")
    else:
        print("ERROR",camps)
entrada.close()
sortidaSL.close()
sortidaTL.close()
        
entrada=codecs.open(valPreCorpus,"r",encoding="utf-8")
sortidaSL=codecs.open("valPreSL.temp","w",encoding="utf-8")
sortidaTL=codecs.open("valPreTL.temp","w",encoding="utf-8")

for linia in entrada:
    linia=linia.rstrip()
    camps=linia.split("\t")
    if len(camps)==2:
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
        command="subword-nmt learn-joint-bpe-and-vocab --input trainPreSL.temp trainPreTL.temp -s "+str(NUM_OPERATIONS)+" -o codes_file --write-vocabulary vocab_BPE."+SL+" vocab_BPE."+TL
        os.system(command)
    else:
        if VERBOSE: print("SL",datetime.now())
        command="subword-nmt learn-joint-bpe-and-vocab --input trainPreSL.temp -s "+str(NUM_OPERATIONS)+" -o codes_file."+SL+" --write-vocabulary vocab_BPE."+SL
        os.system(command)
        if VERBOSE: print("TL",datetime.now())
        command="subword-nmt learn-joint-bpe-and-vocab --input trainPreTL.temp -s "+str(NUM_OPERATIONS)+" -o codes_file."+TL+" --write-vocabulary vocab_BPE."+TL
        os.system(command)


if APPLY_BPE: 
    if VERBOSE:
        print("Applying BPE",datetime.now())
    if JOIN_LANGUAGES:
        BPESL="codes_file"
        BPETL="codes_file"
    if not JOIN_LANGUAGES:
        BPESL="codes_file."+SL
        BPETL="codes_file."+TL
    if not BPE_DROPOUT:
        if VERBOSE: print("NO BPE DROPOUT",datetime.now())
        if VERBOSE: print("SL using ",BPESL,datetime.now())
        #train
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --separator "+joiner+" < trainPreSL.temp > train.bpe."+SL
        os.system(command)
        if VERBOSE: print("TL using",BPETL,datetime.now())
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --separator "+joiner+" < trainPreTL.temp."+TL+" > train.bpe.temp."+TL
        os.system(command)
        #val
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --separator "+joiner+" < "+"valPreSL.temp  > val.bpe."+SL
        os.system(command)
        if VERBOSE: print("TL using",BPETL,datetime.now())
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --separator "+joiner+" < "+"val.PreTL,temp > val.bpe."+TL
        os.system(command)
                
        
    if BPE_DROPOUT:
        if VERBOSE: print("BPE DROPOUT",datetime.now())
        if VERBOSE: print("SL using ",BPESL,datetime.now())
        #train
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --separator "+joiner+" --dropout "+str(BPE_DROPOUT_P)+" < "+"trainPreSL.temp > train.bpe."+SL
        os.system(command)
        if VERBOSE: print("TL using",BPETL,datetime.now())
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --separator "+joiner+" --dropout "+str(BPE_DROPOUT_P)+" < "+"trainPreTL.temp > train.bpe."+TL
        os.system(command)
        #val
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --separator "+joiner+" --dropout "+str(BPE_DROPOUT_P)+" < "+"valPreSL.temp > val.bpe."+SL
        os.system(command)
        if VERBOSE: print("TL using",BPETL,datetime.now())
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --separator "+joiner+" --dropout "+str(BPE_DROPOUT_P)+" < "+"valPreTL.temp > val.bpe."+TL
        os.system(command)
        
if SPLIT_NUMBERS:
    if VERBOSE: print("Splitting numbers",datetime.now())
    #train SL
    copyfile("train.bpe."+SL, "temp.temp")
    entrada=codecs.open("temp.temp","r",encoding="utf-8")
    sortida=codecs.open("train.bpe."+SL,"w",encoding="utf-8")
    for linia in entrada:
        linia=linia.rstrip()
        linia=splitnumbers(linia,joiner)
        sortida.write(linia+"\n")
    entrada.close()
    sortida.close()
    
    #train TL
    copyfile("train.bpe."+TL, "temp.temp")
    entrada=codecs.open("temp.temp","r",encoding="utf-8")
    sortida=codecs.open("train.bpe."+TL,"w",encoding="utf-8")
    for linia in entrada:
        linia=linia.rstrip()
        linia=splitnumbers(linia,joiner)
        sortida.write(linia+"\n")
    entrada.close()
    sortida.close()
    
    #val SL
    copyfile("val.bpe."+SL, "temp.temp")
    entrada=codecs.open("temp.temp","r",encoding="utf-8")
    sortida=codecs.open("val.bpe."+SL,"w",encoding="utf-8")
    for linia in entrada:
        linia=linia.rstrip()
        linia=splitnumbers(linia,joiner)
        sortida.write(linia+"\n")
    entrada.close()
    sortida.close()
    
    #val TL
    copyfile("val.bpe."+TL, "temp.temp")
    entrada=codecs.open("temp.temp","r",encoding="utf-8")
    sortida=codecs.open("val.bpe."+TL,"w",encoding="utf-8")
    for linia in entrada:
        linia=linia.rstrip()
        linia=splitnumbers(linia,joiner)
        sortida.write(linia+"\n")
    entrada.close()
    sortida.close()
        
if GUIDED_ALIGNMENT:
    if VERBOSE:
        print("GUIDED ALIGNMENT TRAINING",datetime.now())
    if DELETE_EXISTING:
        FILE="train.bpe."+SL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
    if ALIGNER=="fast_align":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
        guided_alignment_fast_align(MTUOC,"train.bpe","train.bpe",SL,TL,False,VERBOSE)
        
    if ALIGNER=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
        guided_alignment_eflomal(MTUOC,"train.bpe","train.bpe",SL,TL,SPLIT_LIMIT,VERBOSE)

if GUIDED_ALIGNMENT_VALID:
    if VERBOSE:
        print("GUIDED ALIGNMENT VALIDATION",datetime.now())
    if DELETE_EXISTING:
        FILE="val.bpe."+SL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
        FILE="val.bpe."+TL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    if ALIGNER=="fast_align":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
        guided_alignment_fast_align(MTUOC,"val.bpe","val.bpe",SL,TL,False,VERBOSE)
        
    if ALIGNER=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
        guided_alignment_eflomal(MTUOC,"val.bpe","val.bpe",SL,TL,SPLIT_LIMIT,VERBOSE)

if VERBOSE:
    print("End of process",datetime.now())

#DELETE TEMPORAL FILES

if DELETE_TEMP:
    os.remove("trainPreSL.temp")
    os.remove("trainPreTL.temp")
    os.remove("valPreSL.temp")
    os.remove("valPreTL.temp")
    os.remove("temp.temp")
