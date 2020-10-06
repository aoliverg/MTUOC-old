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



###YAML IMPORTS
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
    
    
stream = open('config-NMT-SP-combi.yaml', 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)

VERBOSE=config["VERBOSE"]


MTUOC=config["MTUOC"]
sys.path.append(MTUOC)
import MTUOC_cleaning as cleaner


ROOTNAME_SPE=config["ROOTNAME_SPE"]
ROOTNAME_GEN=config["ROOTNAME_GEN"]

SL=config["SL"]
TL=config["TL"]

TOKENIZE_SL=config["TOKENIZE_SL"]
SL_TOKENIZER=config["SL_TOKENIZER"]
TOKENIZE_TL=config["TOKENIZE_TL"]
TL_TOKENIZER=config["TL_TOKENIZER"]

CLEAN=config["CLEAN"]
CLEAN_MIN_TOK=config["CLEAN_MIN_TOK"]
CLEAN_MAX_TOK=config["CLEAN_MAX_TOK"]

#COMBINATION
SELECTED_SEGMENTS=int(config["SELECTED_SEGMENTS"])

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
ROOTNAME_ALI="train_COMBI.sp"
ALIGNER=config["ALIGNER"]
#one of eflomal, fast_align
BOTH_DIRECTIONS=config["BOTH_DIRECTIONS"]
#only for fast_align, eflomal aligns always the two directions at the same time
DELETE_EXISTING=config["DELETE_EXISTING"]
DELETE_TEMP=config["DELETE_TEMP"]
SPLIT_LIMIT=int(config["SPLIT_LIMIT"])


#GUIDED ALIGNMENT VALID
GUIDED_ALIGNMENT_VALID=config["GUIDED_ALIGNMENT_VALID"]
ROOTNAME_ALI_VALID="val_SPE.sp"
ALIGNER_VALID=config["ALIGNER_VALID"]
#one of eflomal, fast_align
BOTH_DIRECTIONS_VALID=config["BOTH_DIRECTIONS"]
#only for fast_align, eflomal aligns always the two directions at the same time
DELETE_EXISTING_VALID=config["DELETE_EXISTING"]
DELETE_TEMP_VALID=config["DELETE_TEMP"]

if VERBOSE:
    print("Start of process",datetime.now())

tokenizerASL=importlib.import_module(SL_TOKENIZER)
tokenizerATL=importlib.import_module(TL_TOKENIZER)

from MTUOC_split_corpus import split_corpus
import MTUOC_combine_corpus as combiner

#TOKENIZATION AND CLEANING? OF CORPUS_SPE AND CORPUS_GEN
#TEMPFILES: corpus_spe.clean.SL/TL corpus_gen.clean.SL/TL

if VERBOSE:
    print("SPE corpus: tokenization and cleaning for combination",datetime.now())

sortidatempSPESL=codecs.open("corpus_spe_clean."+SL,"w",encoding="utf-8")
sortidatempSPETL=codecs.open("corpus_spe_clean."+TL,"w",encoding="utf-8")

sortidatempGENSL=codecs.open("corpus_gen_clean."+SL,"w",encoding="utf-8")
sortidatempGENTL=codecs.open("corpus_gen_clean."+TL,"w",encoding="utf-8")

filenameSL=ROOTNAME_SPE+"."+SL
entradaSL=codecs.open(filenameSL,"r",encoding="utf-8")
filenameTL=ROOTNAME_SPE+"."+TL
entradaTL=codecs.open(filenameTL,"r",encoding="utf-8")

while 1:
    liniaSL=entradaSL.readline()
    if not liniaSL:
        break
    liniaSL=liniaSL.strip()
    tokensSL=tokenizerASL.tokenize_m(liniaSL)
    liniaTL=entradaTL.readline()
    liniaTL=liniaTL.strip()
    tokensTL=tokenizerATL.tokenize_m(liniaTL)
    if not CLEAN:
        toclean=False
    else:
        toclean=cleaner.clean(tokensSL,tokensSL,CLEAN_MIN_TOK,CLEAN_MAX_TOK)
    if not toclean:
        sortidatempSPESL.write(tokensSL+"\n")
        sortidatempSPETL.write(tokensTL+"\n")
entradaSL.close()
sortidatempSPESL.close()        
entradaTL.close()
sortidatempSPETL.close()

filenameSL=ROOTNAME_GEN+"."+SL
entradaSL=codecs.open(filenameSL,"r",encoding="utf-8")
filenameTL=ROOTNAME_GEN+"."+TL
entradaTL=codecs.open(filenameTL,"r",encoding="utf-8")

if VERBOSE:
    print("GEN corpus: tokenization and cleaning for combination",datetime.now())

while 1:
    liniaSL=entradaSL.readline()
    if not liniaSL:
        break
    liniaSL=liniaSL.strip()
    tokensSL=tokenizerASL.tokenize(liniaSL)
    liniaTL=entradaTL.readline()
    liniaTL=liniaTL.strip()
    tokensTL=tokenizerATL.tokenize(liniaTL)
    if not CLEAN:
        toclean=False
    else:
        toclean=cleaner.clean(tokensSL,tokensSL,CLEAN_MIN_TOK,CLEAN_MAX_TOK)
    if not toclean:
        sortidatempGENSL.write(tokensSL+"\n")
        sortidatempGENTL.write(tokensTL+"\n")
entradaSL.close()
sortidatempGENSL.close()        
entradaTL.close()
sortidatempGENTL.close()

if VERBOSE:
    print("Combining corpora",datetime.now())

currentdir=os.getcwd()
combiner.combine_corpus(MTUOC, currentdir, SL, TL, "corpus_spe_clean", "corpus_gen_clean", "genselected", SELECTED_SEGMENTS) 

#SPLIT CORPUS_SPE INTO TRAIN_SPE, VAL_SPE AND EVAL_SPE

if VERBOSE:
    print("Splitting corpora",datetime.now())

NUMOFLINES=file_len(ROOTNAME_SPE+"."+SL)
NLTRAIN=NUMOFLINES - lval -leval
parameters=["train_SPE."+SL,NLTRAIN,"val_SPE."+SL,lval,"eval_SPE."+SL,leval]
split_corpus(ROOTNAME_SPE+"."+SL,parameters)
parameters=["train_SPE."+TL,NLTRAIN,"val_SPE."+TL,lval,"eval_SPE."+TL,leval]
split_corpus(ROOTNAME_SPE+"."+TL,parameters)

#TRAIN CORPUS IS train_spe + genselected

command="cat train_SPE."+SL+" genselected."+SL+" > train_COMBI."+SL
os.system(command)

command="cat train_SPE."+TL+" genselected."+TL+" > train_COMBI."+TL
os.system(command)

learner = pyonmttok.SentencePieceLearner(vocab_size=VOCAB_SIZE, character_coverage=CHARACTER_COVERAGE, model_type=MODEL_TYPE,input_sentence_size=INPUT_SENTENCE_SIZE, shuffle_input_sentence=True, hard_vocab_limit=False)
learnerSL = pyonmttok.SentencePieceLearner(vocab_size=VOCAB_SIZE, character_coverage=CHARACTER_COVERAGE, model_type=MODEL_TYPE,input_sentence_size=INPUT_SENTENCE_SIZE, shuffle_input_sentence=True, hard_vocab_limit=False)
learnerTL = pyonmttok.SentencePieceLearner(vocab_size=VOCAB_SIZE, character_coverage=CHARACTER_COVERAGE, model_type=MODEL_TYPE,input_sentence_size=INPUT_SENTENCE_SIZE, shuffle_input_sentence=True, hard_vocab_limit=False)

filename="train_COMBI."+SL
entrada=codecs.open(filename,"r",encoding="utf-8")

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

filename="train_COMBI."+TL
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
    tokenizerSL = pyonmttok.Tokenizer("space", spacer_annotate=True, segment_numbers=True, sp_model_path="model-SP")
    tokenizerTL = pyonmttok.Tokenizer("space", spacer_annotate=True, segment_numbers=True, sp_model_path="model-SP")
else:
    tokenizerSLL = learnerSL.learn("modelSL-SP")
    tokenizerTLL = learnerTL.learn("modelTL-SP")
    tokenizerSL = pyonmttok.Tokenizer("space", spacer_annotate=True, segment_numbers=True, sp_model_path="modelSL-SP")
    tokenizerTL = pyonmttok.Tokenizer("space", spacer_annotate=True, segment_numbers=True, sp_model_path="modelTL-SP")



if VERBOSE:
    print("Tokenizing SL and TL corpora with SentencePiece",datetime.now())

filename="train_COMBI."+SL
entrada=codecs.open(filename,"r",encoding="utf-8")
filename="train_COMBI.sp."+SL
sortida=codecs.open(filename,"w",encoding="utf-8")


if VERBOSE:
    print("SentencePiece train_COMBI SL",datetime.now())

for linia in entrada:
    linia=linia.strip()
    liniap=tokenizerASL.protect(linia)
    output="<s> "+tokenizerASL.unprotect(" ".join(tokenizerSL.tokenize(liniap)[0]))+" </s>"
    sortida.write(output+"\n")

    
filename="train_COMBI."+TL
entrada=codecs.open(filename,"r",encoding="utf-8")
filename="train_COMBI.sp."+TL
sortida=codecs.open(filename,"w",encoding="utf-8")

if VERBOSE:
    print("SentencePiece train_COMBI TL",datetime.now())

for linia in entrada:
    linia=linia.strip()
    liniap=tokenizerATL.protect(linia)
    output="<s> "+tokenizerATL.unprotect(" ".join(tokenizerTL.tokenize(liniap)[0]))+" </s>"
    sortida.write(output+"\n")


filename="val_SPE."+SL
entrada=codecs.open(filename,"r",encoding="utf-8")
filename="val_SPE.sp."+SL
sortida=codecs.open(filename,"w",encoding="utf-8")

if VERBOSE:
    print("SentencePiece val_SPE SL",datetime.now())

for linia in entrada:
    linia=linia.strip()
    liniap=tokenizerASL.protect(linia)
    output="<s> "+tokenizerASL.unprotect(" ".join(tokenizerSL.tokenize(liniap)[0]))+" </s>"
    sortida.write(output+"\n")

if VERBOSE:
    print("SentencePiece val_SPE TL",datetime.now())

filename="val_SPE."+TL
entrada=codecs.open(filename,"r",encoding="utf-8")
filename="val_SPE.sp."+TL
sortida=codecs.open(filename,"w",encoding="utf-8")

for linia in entrada:
    linia=linia.strip()
    liniap=tokenizerATL.protect(linia)
    output="<s> "+tokenizerATL.unprotect(" ".join(tokenizerTL.tokenize(liniap)[0]))+" </s>"
    sortida.write(output+"\n")
    
filename="eval_SPE."+SL
entrada=codecs.open(filename,"r",encoding="utf-8")
filename="eval_SPE.sp."+SL
sortida=codecs.open(filename,"w",encoding="utf-8")

if VERBOSE:
    print("SentencePiece eval_SPE SL",datetime.now())

for linia in entrada:
    linia=linia.strip()
    liniap=tokenizerASL.protect(linia)
    output="<s> "+tokenizerASL.unprotect(" ".join(tokenizerSL.tokenize(liniap)[0]))+" </s>"
    sortida.write(output+"\n")
    
filename="eval_SPE."+TL
entrada=codecs.open(filename,"r",encoding="utf-8")
filename="eval_SPE.sp."+TL
sortida=codecs.open(filename,"w",encoding="utf-8")

if VERBOSE:
    print("SentencePiece eval_SPE TL",datetime.now())

for linia in entrada:
    linia=linia.strip()
    liniap=tokenizerATL.protect(linia)
    output="<s> "+tokenizerATL.unprotect(" ".join(tokenizerTL.tokenize(liniap)[0]))+" </s>"
    sortida.write(output+"\n")
    
if GUIDED_ALIGNMENT:
    if VERBOSE:
        print("GUIDED ALIGNMENT TRAINING using ", ALIGNER, datetime.now())
    if DELETE_EXISTING:
        FILE="train_COMBI.sp."+SL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
        FILE="train_COMBI.sp."+TL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    if ALIGNER=="fast_align":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
        guided_alignment_fast_align(MTUOC,"train_COMBI.sp","train_COMBI.sp",SL,TL,BOTH_DIRECTIONS,VERBOSE)
        
    if ALIGNER=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
        guided_alignment_eflomal(MTUOC,"train_COMBI.sp","train_COMBI.sp",SL,TL,SPLIT_LIMIT,VERBOSE)


if GUIDED_ALIGNMENT_VALID:
    if VERBOSE:
        print("GUIDED ALIGNMENT VALID using ", ALIGNER,datetime.now())
    if DELETE_EXISTING:
        FILE="val_SPE.sp."+SL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
        FILE="val_SPE.sp."+TL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    if ALIGNER=="fast_align":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
        guided_alignment_fast_align(MTUOC,"val_SPE.sp","val_SPE.sp",SL,TL,BOTH_DIRECTIONS,VERBOSE)
        
    if ALIGNER=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
        guided_alignment_eflomal(MTUOC,"val_SPE.sp","val_SPE.sp",SL,TL,SPLIT_LIMIT,VERBOSE)

if VERBOSE:
    print("End of process",datetime.now())
