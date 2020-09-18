import sys
import codecs
import importlib
import os
import pickle
from datetime import datetime

def adapt_output(segment):
    if joiner=="￭":
        segment=segment.replace("@@","￭")
    elif joiner=="@@":
        segment=segment.replace("￭","@@")
    if bos_annotate:
        segment="<s> "+segment
    if eos_annotate:
        segment=segment+" </s>"
    return(segment)

def file_len(fname):
    num_lines = sum(1 for line in open(fname))
    return(num_lines)

###YAML IMPORTS
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

    
stream = open('config-NMT-combi.yaml', 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)

VERBOSE=config["VERBOSE"]

ROOTNAME_SPE=config["ROOTNAME_SPE"]
ROOTNAME_GEN=config["ROOTNAME_GEN"]

SL=config["SL"]
TL=config["TL"]

#MTUOC's scripts directory
MTUOC=config["MTUOC"]
sys.path.append(MTUOC)

#MTUOC IMPORTS
import MTUOC_cleaning as cleaner
import MTUOC_train_truecaser as truecaserlearner
import MTUOC_truecaser as truecaserSL
import MTUOC_truecaser as truecaserTL
from MTUOC_split_corpus import split_corpus
import MTUOC_combine_corpus as combiner

#TOKENIZATION
TOKENIZE_SL=config["TOKENIZE_SL"]
SLTOKENIZER=config["SLTOKENIZER"]
TOKENIZE_TL=config["TOKENIZE_TL"]
TLTOKENIZER=config["TLTOKENIZER"]
    
#CLEANING
CLEAN=config["CLEAN"]
CLEAN_MIN_TOK=config["CLEAN_MIN_TOK"]
CLEAN_MAX_TOK=config["CLEAN_MAX_TOK"]

#COMBINATION
SELECTED_SEGMENTS=int(config["SELECTED_SEGMENTS"])

#TRUECASING
LEARN_TRUECASER_SL=config["LEARN_TRUECASER_SL"]
SLDICT=config["SLDICT"]
LEARN_TRUECASER_TL=config["LEARN_TRUECASER_TL"]
TLDICT=config["TLDICT"]
TRUECASE_SL=config["TRUECASE_SL"]
TRUECASE_TL=config["TRUECASE_TL"]


#SPLITTING CORPUS
SPLIT_CORPUS=config["SPLIT_CORPUS"]
lval=config["lval"]
leval=config["leval"]

#SUBWORD-NMT
LEARN_BPE=config["LEARN_BPE"]
joiner=config["joiner"]
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
GUIDED_ALIGNMENT=config["GUIDED_ALIGNMENT"]
if not APPLY_BPE:
    ROOTNAME_ALI="train_COMBI.pre"
if APPLY_BPE:
    ROOTNAME_ALI="train_COMBI.bpe"
ALIGNER=config["ALIGNER"]
#one of eflomal, fast_align
BOTH_DIRECTIONS=config["BOTH_DIRECTIONS"]
#only for fast_align, eflomal aligns always the two directions at the same time
DELETE_EXISTING=config["DELETE_EXISTING"]
DELETE_TEMP=config["DELETE_TEMP"]
SPLIT_LIMIT=int(config["SPLIT_LIMIT"])


#GUIDED ALIGNMENT VALID
GUIDED_ALIGNMENT_VALID=config["GUIDED_ALIGNMENT_VALID"]
if not APPLY_BPE:
    ROOTNAME_ALI_VALID="val_SPE.pre"
if APPLY_BPE:
    ROOTNAME_ALI_VALID="val_SPE.bpe"
ALIGNER_VALID=config["ALIGNER_VALID"]
#one of eflomal, fast_align
BOTH_DIRECTIONS_VALID=config["BOTH_DIRECTIONS"]
#only for fast_align, eflomal aligns always the two directions at the same time
DELETE_EXISTING_VALID=config["DELETE_EXISTING"]
DELETE_TEMP_VALID=config["DELETE_TEMP"]

tokenizerSL=importlib.import_module(SLTOKENIZER)
tokenizerTL=importlib.import_module(TLTOKENIZER)

######
#TOKENIZATION AND CLEANING? OF CORPUS_SPE AND CORPUS_GEN
#TEMPFILES: corpus_spe.clean.SL/TL corpus_gen.clean.SL/TL

sortidatempSPESL=codecs.open("corpus_spe_clean."+SL,"w",encoding="utf-8")
sortidatempSPETL=codecs.open("corpus_spe_clean."+TL,"w",encoding="utf-8")

sortidatempGENSL=codecs.open("corpus_gen_clean."+SL,"w",encoding="utf-8")
sortidatempGENTL=codecs.open("corpus_gen_clean."+TL,"w",encoding="utf-8")

filenameSL=ROOTNAME_SPE+"."+SL
entradaSL=codecs.open(filenameSL,"r",encoding="utf-8")
filenameTL=ROOTNAME_SPE+"."+TL
entradaTL=codecs.open(filenameTL,"r",encoding="utf-8")

if VERBOSE:
    print("Start of process",datetime.now())
    
if VERBOSE:
    print("SPE corpus: tokenization and cleaning for combination",datetime.now())

while 1:
    liniaSL=entradaSL.readline()
    if not liniaSL:
        break
    liniaSL=liniaSL.strip()
    tokensSL=tokenizerSL.tokenize_m(liniaSL)
    liniaTL=entradaTL.readline()
    liniaTL=liniaTL.strip()
    tokensTL=tokenizerTL.tokenize_m(liniaTL)
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
    tokensSL=tokenizerSL.tokenize(liniaSL)
    liniaTL=entradaTL.readline()
    liniaTL=liniaTL.strip()
    tokensTL=tokenizerTL.tokenize(liniaTL)
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

currentdir=os.getcwd()

if VERBOSE:
    print("Combining corpora",datetime.now())
    
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
######


if LEARN_TRUECASER_SL:
    if VERBOSE:
        print("Learning Truecaser SL",datetime.now())
    truecasemodel="tc."+SL
    filenameSL="train_COMBI."+SL
    entrada=codecs.open(filenameSL,"r",encoding="utf-8")
    sortidaTMP=codecs.open("traintruecaser.temp","w",encoding="utf-8")
    while 1:
        linia=entrada.readline()
        if not linia:
            break
        linia=linia.strip()
        tokens=tokenizerSL.tokenize(linia)
        sortidaTMP.write(tokens+"\n")
    truecaserlearner.train_truecaser(truecasemodel,"traintruecaser.temp",SLDICT)
    if os.path.exists("traintruecaser.temp"): os.remove("traintruecaser.temp")
    print("End of traning SL truecaser")
    
if LEARN_TRUECASER_TL:
    if VERBOSE:
        print("Learning Truecaser TL",datetime.now())
    truecasemodel="tc."+TL
    filenameTL="train_COMBI."+TL
    entrada=codecs.open(filenameTL,"r",encoding="utf-8")
    sortidaTMP=codecs.open("traintruecaser.temp","w",encoding="utf-8")
    while 1:
        linia=entrada.readline()
        if not linia:
            break
        linia=linia.strip()
        tokens=tokenizerTL.tokenize(linia)
        sortidaTMP.write(tokens+"\n")
    truecaserlearner.train_truecaser(truecasemodel,"traintruecaser.temp",TLDICT)
    if os.path.exists("traintruecaser.temp"): os.remove("traintruecaser.temp")
    print("End of traning TL truecaser")
    
#TRUECASE train_COMBI val_SPE eval_SPE

if VERBOSE:
    print("Tokenizing and cleaning SL and TL train_COMBI corpus",datetime.now())

tc_modelSL = pickle.load(open("tc."+SL, "rb" ) )
tc_modelTL = pickle.load(open("tc."+TL, "rb" ) )

entradaSL=codecs.open("train_COMBI."+SL,"r",encoding="utf-8")
entradaTL=codecs.open("train_COMBI."+TL,"r",encoding="utf-8")

sortidaSL=codecs.open("train_COMBI.pre."+SL,"w",encoding="utf-8")
sortidaTL=codecs.open("train_COMBI.pre."+TL,"w",encoding="utf-8")


while 1:
    liniaSL=entradaSL.readline()
    if not liniaSL:
        break
    liniaSL=liniaSL.strip()
    liniaTL=entradaTL.readline()
    liniaTL=liniaTL.strip()
    if TOKENIZE_SL:
        tokens=tokenizerSL.tokenize_mn(liniaSL)
        liniaSL=tokens
    if TOKENIZE_TL:
        tokens=tokenizerTL.tokenize_mn(liniaTL)
        liniaTL=tokens
    if not CLEAN:
        toclean=False
    else:
        toclean=cleaner.clean(liniaSL,liniaTL,CLEAN_MIN_TOK,CLEAN_MAX_TOK)
    if not toclean:
        if TRUECASE_SL:
            liniaSL=truecaserSL.truecase(tc_modelSL,liniaSL)
        if TRUECASE_TL:
            liniaTL=truecaserTL.truecase(tc_modelTL,liniaTL)
        
        sortidaSL.write(liniaSL+"\n")
        sortidaTL.write(liniaTL+"\n")
        
entradaSL.close()
entradaTL.close()
sortidaSL.close()
sortidaTL.close()

if VERBOSE:
    print("Tokenizing and cleaning SL and TL val_SPE corpus",datetime.now())

entradaSL=codecs.open("val_SPE."+SL,"r",encoding="utf-8")
entradaTL=codecs.open("val_SPE."+TL,"r",encoding="utf-8")

sortidaSL=codecs.open("val_SPE.pre."+SL,"w",encoding="utf-8")
sortidaTL=codecs.open("val_SPE.pre."+TL,"w",encoding="utf-8")


while 1:
    liniaSL=entradaSL.readline()
    if not liniaSL:
        break
    liniaSL=liniaSL.strip()
    liniaTL=entradaTL.readline()
    liniaTL=liniaTL.strip()
    if TOKENIZE_SL:
        tokens=tokenizerSL.tokenize_mn(liniaSL)
        liniaSL=tokens
    if TOKENIZE_TL:
        tokens=tokenizerTL.tokenize_mn(liniaTL)
        liniaTL=tokens
    if not CLEAN:
        toclean=False
    else:
        toclean=cleaner.clean(liniaSL,liniaTL,CLEAN_MIN_TOK,CLEAN_MAX_TOK)
    if not toclean:
        if TRUECASE_SL:
            liniaSL=truecaserSL.truecase(tc_modelSL,liniaSL)
        if TRUECASE_TL:
            liniaTL=truecaserTL.truecase(tc_modelTL,liniaTL)
        
        sortidaSL.write(liniaSL+"\n")
        sortidaTL.write(liniaTL+"\n")
        
entradaSL.close()
entradaTL.close()
sortidaSL.close()
sortidaTL.close()

if VERBOSE:
    print("Tokenizing and cleaning SL and TL eval_SPE corpus",datetime.now())

entradaSL=codecs.open("eval_SPE."+SL,"r",encoding="utf-8")
entradaTL=codecs.open("eval_SPE."+TL,"r",encoding="utf-8")

sortidaSL=codecs.open("eval_SPE.pre."+SL,"w",encoding="utf-8")
sortidaTL=codecs.open("eval_SPE.pre."+TL,"w",encoding="utf-8")


while 1:
    liniaSL=entradaSL.readline()
    if not liniaSL:
        break
    liniaSL=liniaSL.strip()
    liniaTL=entradaTL.readline()
    liniaTL=liniaTL.strip()
    if TOKENIZE_SL:
        tokens=tokenizerSL.tokenize_mn(liniaSL)
        liniaSL=tokens
    if TOKENIZE_TL:
        tokens=tokenizerTL.tokenize_mn(liniaTL)
        liniaTL=tokens
    if not CLEAN:
        toclean=False
    else:
        toclean=cleaner.clean(liniaSL,liniaTL,CLEAN_MIN_TOK,CLEAN_MAX_TOK)
    if not toclean:
        if TRUECASE_SL:
            liniaSL=truecaserSL.truecase(tc_modelSL,liniaSL)
        if TRUECASE_TL:
            liniaTL=truecaserTL.truecase(tc_modelTL,liniaTL)
        
        sortidaSL.write(liniaSL+"\n")
        sortidaTL.write(liniaTL+"\n")

entradaSL.close()
entradaTL.close()
sortidaSL.close()
sortidaTL.close()

########################


if LEARN_BPE: 
    if VERBOSE:
        print("Learning BPE",datetime.now())
    if JOIN_LANGUAGES: 
        print("JOINING LANGUAGES")
        command="subword-nmt learn-joint-bpe-and-vocab --input "+"train_COMBI.pre."+SL+" train_COMBI.pre."+TL+" -s "+str(NUM_OPERATIONS)+" -o codes_file --write-vocabulary vocab_BPE."+SL+" vocab_BPE."+TL
        os.system(command)
    else:
        print("SL")
        command="subword-nmt learn-joint-bpe-and-vocab --input "+"train_COMBI.pre."+SL+" -s "+str(NUM_OPERATIONS)+" -o codes_file."+SL+" --write-vocabulary vocab_BPE."+SL
        os.system(command)
        print("TL")
        command="subword-nmt learn-joint-bpe-and-vocab --input "+"train_COMBI.pre."+TL+" -s "+str(NUM_OPERATIONS)+" -o codes_file."+TL+" --write-vocabulary vocab_BPE."+TL
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
        print("NO BPE DROPOUT")
        print("SL using ",BPESL)
        #train
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"train_COMBI.pre."+SL+" > train.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"trainCOMBI.pre."+TL+" > train.bpe.temp."+TL
        os.system(command)
        #val
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"val_SPE.pre."+SL+" > val.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"val_SPE.pre."+TL+" > val.bpe.temp."+TL
        os.system(command)
        #eval
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"eval_SPE.pre."+SL+" > eval.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"eval_SPE.pre."+TL+" > eval.bpe.temp."+TL
        os.system(command)
        
        
    if BPE_DROPOUT:
        print("BPE DROPOUT")
        print("SL using ",BPESL)
        #train
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"train_COMBI.pre."+SL+" > train.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"train_COMBI.pre."+TL+" > train.bpe.temp."+TL
        os.system(command)
        #val
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"val_SPE.pre."+SL+" > val.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"val_SPE.pre."+TL+" > val.bpe.temp."+TL
        os.system(command)
        #eval
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"eval_SPE.pre."+SL+" > eval.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"eval_SPE.pre."+TL+" > eval.bpe.temp."+TL
        os.system(command)
        
        
    #train
    entradaBPETEMPSL=codecs.open("train.bpe.temp."+SL,"r",encoding="utf-8")
    sortidaBPESL=codecs.open("train_COMBI.bpe."+SL,"w",encoding="utf-8")
    for linia in entradaBPETEMPSL:
        linia=linia.strip()
        linia=adapt_output(linia)
        sortidaBPESL.write(linia+"\n")
    entradaBPETEMPTL=codecs.open("train.bpe.temp."+TL,"r",encoding="utf-8")
    sortidaBPETL=codecs.open("train_COMBI.bpe."+TL,"w",encoding="utf-8")
    for linia in entradaBPETEMPTL:
        linia=linia.strip()
        linia=adapt_output(linia)
        sortidaBPETL.write(linia+"\n")
    entradaBPETEMPSL.close()
    sortidaBPESL.close()
    entradaBPETEMPTL.close()
    sortidaBPETL.close()
    #val
    entradaBPETEMPSL=codecs.open("val.bpe.temp."+SL,"r",encoding="utf-8")
    sortidaBPESL=codecs.open("val_SPE.bpe."+SL,"w",encoding="utf-8")
    for linia in entradaBPETEMPSL:
        linia=linia.strip()
        linia=adapt_output(linia)
        sortidaBPESL.write(linia+"\n")
    entradaBPETEMPTL=codecs.open("val.bpe.temp."+TL,"r",encoding="utf-8")
    sortidaBPETL=codecs.open("val_SPE.bpe."+TL,"w",encoding="utf-8")
    for linia in entradaBPETEMPTL:
        linia=linia.strip()
        linia=adapt_output(linia)
        sortidaBPETL.write(linia+"\n")
    entradaBPETEMPSL.close()
    sortidaBPESL.close()
    entradaBPETEMPTL.close()
    sortidaBPETL.close()
    #eval
    entradaBPETEMPSL=codecs.open("eval.bpe.temp."+SL,"r",encoding="utf-8")
    sortidaBPESL=codecs.open("eval_SPE.bpe."+SL,"w",encoding="utf-8")
    for linia in entradaBPETEMPSL:
        linia=linia.strip()
        linia=adapt_output(linia)
        sortidaBPESL.write(linia+"\n")
    entradaBPETEMPTL=codecs.open("eval.bpe.temp."+TL,"r",encoding="utf-8")
    sortidaBPETL=codecs.open("eval_SPE.bpe."+TL,"w",encoding="utf-8")
    for linia in entradaBPETEMPTL:
        linia=linia.strip()
        linia=adapt_output(linia)
        sortidaBPETL.write(linia+"\n")
    entradaBPETEMPSL.close()
    sortidaBPESL.close()
    entradaBPETEMPTL.close()
    sortidaBPETL.close()
    
    if os.path.exists("train.bpe.temp."+SL): os.remove("train.bpe.temp."+SL)
    if os.path.exists("train.bpe.temp."+TL): os.remove("train.bpe.temp."+TL)
    if os.path.exists("val.bpe.temp."+SL): os.remove("val.bpe.temp."+SL)
    if os.path.exists("val.bpe.temp."+TL): os.remove("val.bpe.temp."+TL)
    if os.path.exists("eval.bpe.temp."+SL): os.remove("eval.bpe.temp."+SL)
    if os.path.exists("eval.bpe.temp."+TL): os.remove("eval.bpe.temp."+TL)
        
            
if GUIDED_ALIGNMENT:
    if VERBOSE:
        print("GUIDED ALIGNMENT TRAINING",datetime.now())
    if DELETE_EXISTING:
        if APPLY_BPE:
            FILE="train_COMBI.bpe."+SL+"."+SL+".align"
        else:
            FILE="train_COMBI."+SL+"."+SL+".align"
        if os.path.exists(FILE):
            os.remove(FILE)
        if APPLY_BPE:
            FILE="train_COMBI.bpe."+TL+"."+TL+".align" 
        else:
            FILE="train_COMBI."+TL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    if ALIGNER=="fast_align":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
        if APPLY_BPE:
            guided_alignment_fast_align(MTUOC,"train_COMBI.bpe","train_COMBI.bpe",SL,TL,BOTH_DIRECTIONS,VERBOSE)
        else:
            guided_alignment_fast_align(MTUOC,"train_COMBI","train_COMBI",SL,TL,BOTH_DIRECTIONS,VERBOSE)
        
    if ALIGNER=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
        if APPLY_BPE:
            guided_alignment_eflomal(MTUOC,"train_COMBI.bpe","train_COMBI.bpe",SL,TL,SPLIT_LIMIT,VERBOSE)
        else:
            guided_alignment_eflomal(MTUOC,"train_COMBI","train_COMBI",SL,TL,SPLIT_LIMIT,VERBOSE)


if GUIDED_ALIGNMENT_VALID:
    if VERBOSE:
        print("GUIDED ALIGNMENT TRAINING",datetime.now())
    if DELETE_EXISTING:
        if APPLY_BPE:
            FILE="val_SPE.bpe."+SL+"."+SL+".align" 
        else:
            FILE="val_SPE."+SL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
        if APPLY_BPE:
            FILE="val_SPE.bpe."+TL+"."+TL+".align" 
        else:
            FILE="val_SPE."+TL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    if ALIGNER=="fast_align":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
        if APPLY_BPE:
            guided_alignment_fast_align(MTUOC,"val_SPE.bpe","val_SPE.bpe",SL,TL,BOTH_DIRECTIONS,VERBOSE)
        else:
            guided_alignment_fast_align(MTUOC,"val_SPE","val_SPE",SL,TL,BOTH_DIRECTIONS,VERBOSE)
        
    if ALIGNER=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
        if APPLY_BPE:
            guided_alignment_eflomal(MTUOC,"val_SPE.bpe","val_SPE.bpe",SL,TL,SPLIT_LIMIT,VERBOSE)
        else:
            guided_alignment_eflomal(MTUOC,"val_SPE","val_SPE",SL,TL,SPLIT_LIMIT,VERBOSE)


if os.path.exists("corpus_gen_clean.en"): os.remove("corpus_gen_clean.en")
if os.path.exists("corpus_gen_clean.es"): os.remove("corpus_gen_clean.es")
if os.path.exists("corpus_spe_clean.en"): os.remove("corpus_spe_clean.en")
if os.path.exists("corpus_spe_clean.es"): os.remove("corpus_spe_clean.es")
if os.path.exists("genselected.en"): os.remove("genselected.en")
if os.path.exists("genselected.es"): os.remove("genselected.es")


if VERBOSE:
    print("End of process",datetime.now())
