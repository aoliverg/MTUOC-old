import pyonmttok
import sys
import importlib
from importlib import import_module
import codecs
import os
import subprocess

###YAML IMPORTS
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    
    
stream = open('config-NMT-SP.yaml', 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)


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

sys.path.append(MTUOC)



    
def file_len(fname):
    num_lines = sum(1 for line in open(fname))
    return(num_lines)

tokenizerASL=importlib.import_module(SL_TOKENIZER)
tokenizerATL=importlib.import_module(TL_TOKENIZER)



from MTUOC_split_corpus import split_corpus


learner = pyonmttok.SentencePieceLearner(vocab_size=VOCAB_SIZE, character_coverage=CHARACTER_COVERAGE, model_type=MODEL_TYPE,input_sentence_size=INPUT_SENTENCE_SIZE, shuffle_input_sentence=True, hard_vocab_limit=False)
learnerSL = pyonmttok.SentencePieceLearner(vocab_size=VOCAB_SIZE, character_coverage=CHARACTER_COVERAGE, model_type=MODEL_TYPE,input_sentence_size=INPUT_SENTENCE_SIZE, shuffle_input_sentence=True, hard_vocab_limit=False)
learnerTL = pyonmttok.SentencePieceLearner(vocab_size=VOCAB_SIZE, character_coverage=CHARACTER_COVERAGE, model_type=MODEL_TYPE,input_sentence_size=INPUT_SENTENCE_SIZE, shuffle_input_sentence=True, hard_vocab_limit=False)

filename=ROOTNAME+"."+SL
entrada=codecs.open(filename,"r",encoding="utf-8")

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
filenameSL=ROOTNAME+".sp."+SL
sortidaSL=codecs.open(filenameSL,"w",encoding="utf-8")
filenameSLTEMP="corpustemp."+SL
sortidaSL=codecs.open(filenameSL,"w",encoding="utf-8")
sortidaSLTEMP=codecs.open(filenameSLTEMP,"w",encoding="utf-8")


filenameTL=ROOTNAME+"."+TL
entradaTL=codecs.open(filenameTL,"r",encoding="utf-8")
filenameTL=ROOTNAME+".sp."+TL
filenameTLTEMP="corpustemp."+TL
sortidaTL=codecs.open(filenameTL,"w",encoding="utf-8")
sortidaTLTEMP=codecs.open(filenameTLTEMP,"w",encoding="utf-8")


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
        output="<s> "+tokenizerASL.unprotect(" ".join(tokenizerSL.tokenize(liniapSL)[0]))+" </s>"
        sortidaSL.write(output+"\n")
        sortidaSLTEMP.write(liniaSL)
        output="<s> "+tokenizerATL.unprotect(" ".join(tokenizerTL.tokenize(liniapTL)[0]))+" </s>"
        sortidaTL.write(output+"\n")
        sortidaSLTEMP.write(liniaTL)
if SPLIT_CORPUS:
    print("SPLITTING CORPUS")
    NUMOFLINES=file_len("corpustemp."+SL)
    NLTRAIN=NUMOFLINES - lval -leval
    parameters=["train."+SL,NLTRAIN,"val."+SL,lval,"eval."+SL,leval]
    split_corpus("corpustemp."+SL,parameters)
    parameters=["train."+TL,NLTRAIN,"val."+TL,lval,"eval."+TL,leval]
    split_corpus("corpustemp."+TL,parameters)
    
    NUMOFLINES=file_len(ROOTNAME+".sp."+SL)
    NLTRAIN=NUMOFLINES - lval -leval
    parameters=["train.sp."+SL,NLTRAIN,"val.sp."+SL,lval,"eval.sp."+SL,leval]
    split_corpus(ROOTNAME+".sp."+SL,parameters)
    parameters=["train.sp."+TL,NLTRAIN,"val.sp."+TL,lval,"eval.sp."+TL,leval]
    split_corpus(ROOTNAME+".sp."+TL,parameters)

if GUIDED_ALIGNMENT:
    print("GUIDED ALIGNMENT")
    if DELETE_EXISTING:
        FILE=ROOTNAME_ALI+"."+SL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
        FILE=ROOTNAME_ALI+"."+TL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    FILE1=ROOTNAME_ALI+"."+SL
    FILE2=ROOTNAME_ALI+"."+TL
    FILEOUT="corpus."+SL+"."+TL+"."+"fa"
    command="paste "+FILE1+" "+FILE2+" | sed 's/\t/ ||| /g' > "+FILEOUT
    print("Running command: ",command)
    os.system(command)
    
    if ALIGNER=="fast_align":
        command=MTUOC+"/fast_align -vdo -i corpus."+SL+"."+TL+".fa > forward."+SL+"."+TL+".align"
        print("Running command: ",command)
        os.system(command)
        command=MTUOC+"/fast_align -vdor -i corpus."+SL+"."+TL+".fa > reverse."+SL+"."+TL+".align"
        print("Running command: ",command)
        os.system(command)
        command=MTUOC+"/atools -c grow-diag-final -i forward."+SL+"."+TL+".align -j reverse."+SL+"."+TL+".align > "+ROOTNAME_ALI+"."+SL+"."+TL+".align"
        print("Running command: ",command)
        os.system(command)
        
        if BOTH_DIRECTIONS:
            FILE1=ROOTNAME_ALI+"."+SL
            FILE2=ROOTNAME_ALI+"."+TL
            FILEOUT="corpus."+TL+"."+SL+"."+"fa"
            command="paste "+FILE2+" "+FILE1+" | sed 's/\t/ ||| /g' > "+FILEOUT
            print("Running command: ",command)
            os.system(command)
            command=MTUOC+"/fast_align -vdo -i corpus."+TL+"."+SL+".fa > forward."+TL+"."+SL+".align"
            print("Running command: ",command)
            os.system(command)
            command=MTUOC+"/fast_align -vdor -i corpus."+TL+"."+SL+".fa > reverse."+TL+"."+SL+".align"
            print("Running command: ",command)
            os.system(command)
            command=MTUOC+"/atools -c grow-diag-final -i forward."+TL+"."+SL+".align -j reverse."+TL+"."+SL+".align > "+ROOTNAME_ALI+"."+TL+"."+SL+".align"
            print("Running command: ",command)
            os.system(command)
        
    if ALIGNER=="eflomal":
        command=MTUOC+"/eflomal-align.py -i corpus."+SL+"."+TL+".fa --model 3 -f "+ROOTNAME_ALI+"."+SL+"."+TL+".align -r "+ROOTNAME_ALI+"."+TL+"."+SL+".align"
        print("Running command: ",command)
        os.system(command)
    if DELETE_TEMP:
        FILE="corpus."+SL+"."+TL+".fa" 
        if os.path.exists(FILE):
            os.remove(FILE)
        if ALIGNER=="fast_align":
            FILE="forward."+SL+"."+TL+".align" 
            if os.path.exists(FILE):
                os.remove(FILE)
            FILE="forward."+TL+"."+SL+".align" 
            if os.path.exists(FILE):
                os.remove(FILE)


if GUIDED_ALIGNMENT_VALID:
    print("GUIDED ALIGNMENT VALIDATION CORPUS")
    print("Using aligner:", ALIGNER_VALID)
    if DELETE_EXISTING_VALID:
        FILE=ROOTNAME_ALI_VALID+"."+SL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
        FILE=ROOTNAME_ALI_VALID+"."+TL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    FILE1=ROOTNAME_ALI_VALID+"."+SL
    FILE2=ROOTNAME_ALI_VALID+"."+TL
    FILEOUT="corpus."+SL+"."+TL+".fa"
    command="paste "+FILE1+" "+FILE2+" | sed 's/\\t/ ||| /g' > "+FILEOUT
    print("Running command: ",command)
    os.system(command)
    
    if ALIGNER_VALID=="fast_align":
        command=MTUOC+"/fast_align -vdo -i corpus."+SL+"."+TL+".fa > forward."+SL+"."+TL+".align"
        print("Running command: ",command)
        os.system(command)
        command=MTUOC+"/fast_align -vdor -i corpus."+SL+"."+TL+".fa > reverse."+SL+"."+TL+".align"
        print("Running command: ",command)
        os.system(command)
        command=MTUOC+"/atools -c grow-diag-final -i forward."+SL+"."+TL+".align -j reverse."+SL+"."+TL+".align > "+ROOTNAME_ALI_VALID+"."+SL+"."+TL+".align"
        print("Running command: ",command)
        os.system(command)
        
        if BOTH_DIRECTIONS_VALID:
            FILE1=ROOTNAME_ALI_VALID+"."+SL
            FILE2=ROOTNAME_ALI_VALID+"."+TL
            FILEOUT="corpus."+TL+"."+SL+"."+"fa"
            command="paste "+FILE2+" "+FILE1+" | sed 's/\t/ ||| /g' > "+FILEOUT
            print("Running command: ",command)
            os.system(command)
            command=MTUOC+"/fast_align -vdo -i corpus."+TL+"."+SL+".fa > forward."+TL+"."+SL+".align"
            print("Running command: ",command)
            os.system(command)
            command=MTUOC+"/fast_align -vdor -i corpus."+TL+"."+SL+".fa > reverse."+TL+"."+SL+".align"
            print("Running command: ",command)
            os.system(command)
            command=MTUOC+"/atools -c grow-diag-final -i forward."+TL+"."+SL+".align -j reverse."+TL+"."+SL+".align > "+ROOTNAME_ALI_VALID+"."+TL+"."+SL+".align"
            print("Running command: ",command)
            os.system(command)
        
    if ALIGNER_VALID=="eflomal":
        command=MTUOC+"/eflomal-align.py -i corpus."+SL+"."+TL+".fa --model 3 -f "+ROOTNAME_ALI_VALID+"."+SL+"."+TL+".align -r "+ROOTNAME_ALI_VALID+"."+TL+"."+SL+".align"
        print("Running command: ",command)
        os.system(command)
    if DELETE_TEMP_VALID:
        FILE="corpus."+SL+"."+TL+".fa" 
        if os.path.exists(FILE):
            os.remove(FILE)
        if ALIGNER=="fast_align":
            FILE="forward."+SL+"."+TL+".align" 
            if os.path.exists(FILE):
                os.remove(FILE)
            FILE="forward."+TL+"."+SL+".align" 
            if os.path.exists(FILE):
                os.remove(FILE)

