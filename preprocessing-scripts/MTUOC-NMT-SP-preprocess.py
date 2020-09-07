#    MTUOC-NMT-SP-preprocess
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

import pyonmttok
import sys
import importlib
from importlib import import_module
import codecs
import os
import subprocess
from datetime import datetime
import re
from shutil import copyfile


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

stream = open('config-NMT-SP.yaml', 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)

VERBOSE=config["VERBOSE"]

MTUOC=config["MTUOC"]
sys.path.append(MTUOC)
import MTUOC_cleaning as cleaner


ROOTNAME=config["ROOTNAME"]

SL=config["SL"]
TL=config["TL"]

TOKENIZE_SL=config["TOKENIZE_SL"]
SL_TOKENIZER=config["SL_TOKENIZER"]
TOKENIZE_TL=config["TOKENIZE_TL"]
TL_TOKENIZER=config["TL_TOKENIZER"]

CLEAN=config["CLEAN"]
CLEAN_MIN_TOK=config["CLEAN_MIN_TOK"]
CLEAN_MAX_TOK=config["CLEAN_MAX_TOK"]

#SENTENCE PIECE
MODEL_TYPE=config["MODEL_TYPE"]
JOIN_LANGUAGES=config["JOIN_LANGUAGES"]
VOCAB_SIZE=config["VOCAB_SIZE"]
CHARACTER_COVERAGE=config["CHARACTER_COVERAGE"]
CHARACTER_COVERAGE_SL=config["CHARACTER_COVERAGE_SL"]
CHARACTER_COVERAGE_TL=config["CHARACTER_COVERAGE_TL"]
INPUT_SENTENCE_SIZE=config["INPUT_SENTENCE_SIZE"]

#SPLITTING CORPUS
SPLIT_CORPUS=config["SPLIT_CORPUS"]
lval=config["lval"]
leval=config["leval"]

#GUIDED ALIGNMENT
GUIDED_ALIGNMENT=config["GUIDED_ALIGNMENT"]
ROOTNAME_ALI="train.sp"
ALIGNER=config["ALIGNER"]
#one of eflomal, fast_align
BOTH_DIRECTIONS=config["BOTH_DIRECTIONS"]
#only for fast_align, eflomal aligns always the two directions at the same time
DELETE_EXISTING=config["DELETE_EXISTING"]
DELETE_TEMP=config["DELETE_TEMP"]

#GUIDED ALIGNMENT VALID
GUIDED_ALIGNMENT_VALID=config["GUIDED_ALIGNMENT_VALID"]
ROOTNAME_ALI_VALID="val.sp"
ALIGNER_VALID=config["ALIGNER_VALID"]
#one of eflomal, fast_align
BOTH_DIRECTIONS_VALID=config["BOTH_DIRECTIONS"]
#only for fast_align, eflomal aligns always the two directions at the same time
DELETE_EXISTING_VALID=config["DELETE_EXISTING"]
DELETE_TEMP_VALID=config["DELETE_TEMP"]
SPLIT_LIMIT=int(config["SPLIT_LIMIT"])

sys.path.append(MTUOC)

tokenizerASL=importlib.import_module(SL_TOKENIZER)
tokenizerATL=importlib.import_module(TL_TOKENIZER)



from MTUOC_split_corpus import split_corpus


learner = pyonmttok.SentencePieceLearner(vocab_size=VOCAB_SIZE, character_coverage=CHARACTER_COVERAGE, model_type=MODEL_TYPE,input_sentence_size=INPUT_SENTENCE_SIZE, shuffle_input_sentence=True, hard_vocab_limit=False)
learnerSL = pyonmttok.SentencePieceLearner(vocab_size=VOCAB_SIZE, character_coverage=CHARACTER_COVERAGE, model_type=MODEL_TYPE,input_sentence_size=INPUT_SENTENCE_SIZE, shuffle_input_sentence=True, hard_vocab_limit=False)
learnerTL = pyonmttok.SentencePieceLearner(vocab_size=VOCAB_SIZE, character_coverage=CHARACTER_COVERAGE, model_type=MODEL_TYPE,input_sentence_size=INPUT_SENTENCE_SIZE, shuffle_input_sentence=True, hard_vocab_limit=False)

filename=ROOTNAME+"."+SL
entrada=codecs.open(filename,"r",encoding="utf-8")

if VERBOSE:
    print("Start of process",datetime.now())

if VERBOSE:
    print("LEARNING SENTENCEPIECE")
    print("SL: tokenizing and ingesting",datetime.now())

for linia in entrada:
    linia=linia.strip()
    if TOKENIZE_SL:
        tokens=tokenizerASL.tokenize_mn(linia)
        linia=tokens
    if JOIN_LANGUAGES:
        learner.ingest(linia)
    else:
        learnerSL.ingest(linia)

filename=ROOTNAME+"."+TL
entrada=codecs.open(filename,"r",encoding="utf-8")

if VERBOSE:
    print("TL: tokenizing and ingesting",datetime.now())

for linia in entrada:
    linia=linia.strip()
    if TOKENIZE_TL:
        tokens=tokenizerATL.tokenize_mn(linia)
        linia=tokens
    if JOIN_LANGUAGES:
        learner.ingest(linia)
    else:
        learnerTL.ingest(linia)

if JOIN_LANGUAGES:
    tokenizer = learner.learn("model-SP")
    tokenizerSL = pyonmttok.Tokenizer("space", spacer_annotate=True, segment_numbers=False, sp_model_path="model-SP")
    tokenizerTL = pyonmttok.Tokenizer("space", spacer_annotate=True, segment_numbers=False, sp_model_path="model-SP")
else:
    tokenizerSL = learnerSL.learn("modelSL-SP")
    tokenizerTL = learnerTL.learn("modelTL-SP")
    tokenizerSL = pyonmttok.Tokenizer("space", spacer_annotate=True, segment_numbers=False, sp_model_path="modelSL-SP")
    tokenizerTL = pyonmttok.Tokenizer("space", spacer_annotate=True, segment_numbers=False, sp_model_path="modelTL-SP")

filenameSL=ROOTNAME+"."+SL
entradaSL=codecs.open(filenameSL,"r",encoding="utf-8")
filenameSL=ROOTNAME+".clean."+SL
sortidaSL=codecs.open(filenameSL,"w",encoding="utf-8")
sortidaSL=codecs.open(filenameSL,"w",encoding="utf-8")


filenameTL=ROOTNAME+"."+TL
entradaTL=codecs.open(filenameTL,"r",encoding="utf-8")
filenameTL=ROOTNAME+".clean."+TL
sortidaTL=codecs.open(filenameTL,"w",encoding="utf-8")

if VERBOSE:
    print("Tokenizing and cleaning SL and TL corpora",datetime.now())

while 1:
    liniaSL=entradaSL.readline()
    if not liniaSL:
        break
    liniaSL=liniaSL.strip()
    liniaTL=entradaTL.readline()
    liniaTL=liniaTL.strip()
    if TOKENIZE_SL:
        liniapSL=tokenizerASL.protect(liniaSL)
    if TOKENIZE_TL:
        liniapTL=tokenizerATL.protect(liniaTL)
    if not CLEAN:
        toclean=False
    else:
        toclean=cleaner.clean(liniapSL,liniapTL,CLEAN_MIN_TOK,CLEAN_MAX_TOK)
    if not toclean:
        sortidaSL.write(liniaSL+"\n")
        sortidaTL.write(liniaTL+"\n")


if SPLIT_CORPUS:
    if VERBOSE:
        print("SPLITTING CORPUS",datetime.now())
    
    NUMOFLINES=file_len(ROOTNAME+".clean."+SL)
    NLTRAIN=NUMOFLINES - lval -leval
    parameters=["train.clean."+SL,NLTRAIN,"val.clean."+SL,lval,"eval.clean."+SL,leval]
    split_corpus(ROOTNAME+".clean."+SL,parameters)
    parameters=["train.clean."+TL,NLTRAIN,"val.clean."+TL,lval,"eval.clean."+TL,leval]
    split_corpus(ROOTNAME+".clean."+TL,parameters)

    
    if VERBOSE:
        print("SentencePiece train SL",datetime.now())
    
    filename="train.clean."+SL
    entrada=codecs.open(filename,"r",encoding="utf-8")
    filename="train.sp."+SL
    sortida=codecs.open(filename,"w",encoding="utf-8")

    for linia in entrada:
        linia=linia.strip()
        liniap=tokenizerASL.protect(linia)
        output="<s> "+tokenizerASL.unprotect(" ".join(tokenizerSL.tokenize(liniap)[0]))+" </s>"
        sortida.write(output+"\n")

        
    filename="train.clean."+TL
    entrada=codecs.open(filename,"r",encoding="utf-8")
    filename="train.sp."+TL
    sortida=codecs.open(filename,"w",encoding="utf-8")

    if VERBOSE:
        print("SentencePiece train TL",datetime.now())

    for linia in entrada:
        linia=linia.strip()
        liniap=tokenizerATL.protect(linia)
        output="<s> "+tokenizerATL.unprotect(" ".join(tokenizerTL.tokenize(liniap)[0]))+" </s>"
        sortida.write(output+"\n")

    if VERBOSE:
        print("SentencePiece val SL",datetime.now())
    
    filename="val.clean."+SL
    entrada=codecs.open(filename,"r",encoding="utf-8")
    filename="val.sp."+SL
    sortida=codecs.open(filename,"w",encoding="utf-8")

    for linia in entrada:
        linia=linia.strip()
        liniap=tokenizerASL.protect(linia)
        output="<s> "+tokenizerASL.unprotect(" ".join(tokenizerSL.tokenize(liniap)[0]))+" </s>"
        sortida.write(output+"\n")

        
    filename="val.clean."+TL
    entrada=codecs.open(filename,"r",encoding="utf-8")
    filename="val.sp."+TL
    sortida=codecs.open(filename,"w",encoding="utf-8")

    if VERBOSE:
        print("SentencePiece val TL",datetime.now())

    for linia in entrada:
        linia=linia.strip()
        liniap=tokenizerATL.protect(linia)
        output="<s> "+tokenizerATL.unprotect(" ".join(tokenizerTL.tokenize(liniap)[0]))+" </s>"
        sortida.write(output+"\n")    

    if VERBOSE:
        print("SentencePiece eval SL",datetime.now())
    
    filename="eval.clean."+SL
    entrada=codecs.open(filename,"r",encoding="utf-8")
    filename="eval.sp."+SL
    sortida=codecs.open(filename,"w",encoding="utf-8")

    for linia in entrada:
        linia=linia.strip()
        liniap=tokenizerASL.protect(linia)
        output="<s> "+tokenizerASL.unprotect(" ".join(tokenizerSL.tokenize(liniap)[0]))+" </s>"
        sortida.write(output+"\n")

        
    filename="eval.clean."+TL
    entrada=codecs.open(filename,"r",encoding="utf-8")
    filename="eval.sp."+TL
    sortida=codecs.open(filename,"w",encoding="utf-8")

    if VERBOSE:
        print("SentencePiece eval TL",datetime.now())

    for linia in entrada:
        linia=linia.strip()
        liniap=tokenizerATL.protect(linia)
        output="<s> "+tokenizerATL.unprotect(" ".join(tokenizerTL.tokenize(liniap)[0]))+" </s>"
        sortida.write(output+"\n")  

if os.path.exists("train.clean."+SL): copyfile("train.clean."+SL, "train."+SL)
if os.path.exists("train.clean."+TL): copyfile("train.clean."+TL, "train."+TL)

if os.path.exists("val.clean."+SL): copyfile("val.clean."+SL, "val."+SL)
if os.path.exists("val.clean."+TL): copyfile("val.clean."+TL, "val."+TL)

if os.path.exists("eval.clean."+SL): copyfile("eval.clean."+SL, "eval."+SL)
if os.path.exists("eval.clean."+TL): copyfile("eval.clean."+TL, "eval."+TL)

if os.path.exists("train.clean."+SL): os.remove("train.clean."+SL)
if os.path.exists("train.clean."+TL): os.remove("train.clean."+TL)

if os.path.exists("val.clean."+SL): os.remove("val.clean."+SL)
if os.path.exists("val.clean."+TL): os.remove("val.clean."+TL)

if os.path.exists("eval.clean."+SL): os.remove("eval.clean."+SL)
if os.path.exists("eval.clean."+TL): os.remove("eval.clean."+TL)


if GUIDED_ALIGNMENT:
    if VERBOSE:
        print("GUIDED ALIGNMENT TRAINING",datetime.now())
    if DELETE_EXISTING:
        FILE="train.sp."+SL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
        FILE="train.sp."+TL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    if ALIGNER=="fast_align":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
        guided_alignment_fast_align(MTUOC,"train.sp","train.sp",SL,TL,BOTH_DIRECTIONS,VERBOSE)
        
    if ALIGNER=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
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
        guided_alignment_fast_align(MTUOC,"val.sp","val.sp",SL,TL,BOTH_DIRECTIONS,VERBOSE)
        
    if ALIGNER=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
        guided_alignment_eflomal(MTUOC,"val.sp","val.sp",SL,TL,SPLIT_LIMIT,VERBOSE)

if VERBOSE:
    print("End of process",datetime.now())
