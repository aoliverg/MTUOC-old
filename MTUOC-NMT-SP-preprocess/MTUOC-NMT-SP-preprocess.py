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

import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    
def file_len(fname):
    num_lines = sum(1 for line in open(fname))
    return(num_lines)

stream = open('config-NMT-SP-preprocess.yaml', 'r',encoding="utf-8")
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
bos=config["bos"]
eos=config["eos"]

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
    print("Start of process",datetime.now())

#SENTENCE PIECE

if VERBOSE: print("Starting SentencePiece training",datetime.now())

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

if JOIN_LANGUAGES:
    if VERBOSE: print("JOIN LANGUAGES",datetime.now())
    command = "cat trainPreSL.temp trainPreTL.temp | shuf > train"
    os.system(command)
    
    if VERBOSE: print("Training SentencePiece model",datetime.now())
    command="spm_train --input=train --model_prefix="+SP_MODEL_PREFIX+" --model_type="+MODEL_TYPE+" --vocab_size="+str(VOCAB_SIZE)+" --character_coverage="+str(CHARACTER_COVERAGE)+" --split_digits --input_sentence_size="+str(INPUT_SENTENCE_SIZE)
    os.system(command)
    
    if VERBOSE: print("Generating vocabularies",datetime.now())
    command="spm_encode --model="+SP_MODEL_PREFIX+".model --generate_vocabulary < trainPreSL.temp > vocab_file."+SL
    os.system(command)
    command="spm_encode --model="+SP_MODEL_PREFIX+".model --generate_vocabulary < trainPreTL.temp > vocab_file."+TL
    os.system(command)
    
else:
    if VERBOSE: print("NOT JOINING LANGUAGES",datetime.now())
    if VERBOSE: print("Training source language SentencePiece model",datetime.now())
    command="spm_train --input=trainPreSL.temp --model_prefix="+SP_MODEL_PREFIX+"-"+SL+" --model_type="+MODEL_TYPE+" --vocab_size="+str(VOCAB_SIZE)+" --character_coverage="+str(CHARACTER_COVERAGE)+" --split_digits --input_sentence_size="+str(INPUT_SENTENCE_SIZE)
    os.system(command)
    if VERBOSE: print("Training target language SentencePiece model",datetime.now())
    command="spm_train --input=trainPreTL.temp --model_prefix="+SP_MODEL_PREFIX+"-"+TL+" --model_type="+MODEL_TYPE+" --vocab_size="+str(VOCAB_SIZE)+" --character_coverage="+str(CHARACTER_COVERAGE)+" --split_digits --input_sentence_size="+str(INPUT_SENTENCE_SIZE)
    os.system(command)
    if VERBOSE: print("Generating vocabularies",datetime.now())
    command="spm_encode --model="+SP_MODEL_PREFIX+"-"+SL+".model --generate_vocabulary < trainPreSL.temp > vocab_file."+SL
    os.system(command)
    command="spm_encode --model="+SP_MODEL_PREFIX+"-"+TL+".model --generate_vocabulary < trainPreTL.temp > vocab_file."+TL
    os.system(command)
       
if JOIN_LANGUAGES:
    command="spm_encode --model="+SP_MODEL_PREFIX+".model --extra_options eos:bos --vocabulary=vocab_file."+SL+" --vocabulary_threshold="+str(VOCABULARY_THRESHOLD)+" < trainPreSL.temp > train.sp."+SL
    if VERBOSE: print("Encoding source language training corpus",datetime.now())
    os.system(command)
    command="spm_encode --model="+SP_MODEL_PREFIX+".model --extra_options eos:bos --vocabulary=vocab_file."+TL+" --vocabulary_threshold="+str(VOCABULARY_THRESHOLD)+" < trainPreTL.temp > train.sp."+TL
    if VERBOSE: print("Encoding target language training corpus",datetime.now())
    os.system(command)
    command="spm_encode --model="+SP_MODEL_PREFIX+".model --extra_options eos:bos --vocabulary=vocab_file."+SL+" --vocabulary_threshold="+str(VOCABULARY_THRESHOLD)+" < valPreSL.temp > val.sp."+SL
    if VERBOSE: print("Encoding source language validation corpus",datetime.now())
    os.system(command)
    command="spm_encode --model="+SP_MODEL_PREFIX+".model --extra_options eos:bos --vocabulary=vocab_file."+TL+" --vocabulary_threshold="+str(VOCABULARY_THRESHOLD)+" < valPreTL.temp > val.sp."+TL
    if VERBOSE: print("Encoding target language validation corpus",datetime.now())
    os.system(command)
   
else:
    command="spm_encode --model="+SP_MODEL_PREFIX+"-"+SL+".model --extra_options eos:bos --vocabulary=vocab_file."+SL+" --vocabulary_threshold="+str(VOCABULARY_THRESHOLD)+" < trainPreSL.temp > train.sp."+SL
    if VERBOSE: print("Encoding source language training corpus",datetime.now())
    os.system(command)
    command="spm_encode --model="+SP_MODEL_PREFIX+"-"+TL+".model --extra_options eos:bos --vocabulary=vocab_file."+TL+" --vocabulary_threshold="+str(VOCABULARY_THRESHOLD)+" < trainPreTL.temp > train.sp."+TL
    os.system(command)
    if VERBOSE: print("Encoding target language training corpus",datetime.now())
    command="spm_encode --model="+SP_MODEL_PREFIX+"-"+SL+".model --extra_options eos:bos --vocabulary=vocab_file."+SL+" --vocabulary_threshold="+str(VOCABULARY_THRESHOLD)+" < valPreSL.temp > val.sp."+SL
    if VERBOSE: print("Encoding source language validation corpus",datetime.now())
    os.system(command)
    command="spm_encode --model="+SP_MODEL_PREFIX+"-"+TL+".model --extra_options eos:bos --vocabulary=vocab_file."+TL+" --vocabulary_threshold="+str(VOCABULARY_THRESHOLD)+" < valPreTL.temp > val.sp."+TL
    if VERBOSE: print("Encoding target language validation corpus",datetime.now())
    os.system(command)
    
if GUIDED_ALIGNMENT:
    if VERBOSE:
        print("GUIDED ALIGNMENT TRAINING",datetime.now())
    if DELETE_EXISTING:
        FILE="train.sp."+SL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
    if ALIGNER=="fast_align":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
        guided_alignment_fast_align(MTUOC,"train.sp","train.sp",SL,TL,False,VERBOSE)
        
    if ALIGNER=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
        if VERBOSE: print("EFLOMAL",MTUOC,"train.sp","train.sp",SL,TL,SPLIT_LIMIT,VERBOSE)
        guided_alignment_eflomal(MTUOC,"train.sp","train.sp",SL,TL,SPLIT_LIMIT,VERBOSE)

if GUIDED_ALIGNMENT_VALID:
    if VERBOSE:
        print("GUIDED ALIGNMENT TRAINING",datetime.now())
    if DELETE_EXISTING:
        FILE="val.sp."+SL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
        FILE="val.sp."+TL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    if ALIGNER=="fast_align":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
        guided_alignment_fast_align(MTUOC,"val.sp","val.sp",SL,TL,False,VERBOSE)
        
    if ALIGNER=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
        guided_alignment_eflomal(MTUOC,"val.sp","val.sp",SL,TL,SPLIT_LIMIT,VERBOSE)

if VERBOSE:
    print("End of process",datetime.now())

#DELETE TEMPORAL FILES

if DELETE_TEMP:
    if VERBOSE: print("Deleting temporal files",datetime.now())
    os.remove("trainPreSL.temp")
    os.remove("trainPreTL.temp")
    os.remove("valPreSL.temp")
    os.remove("valPreTL.temp")


