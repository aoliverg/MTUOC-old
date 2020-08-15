import sys
import codecs
import importlib
import os

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
    

    
stream = open('config-NMT.yaml', 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)

ROOTNAME=config["ROOTNAME"]
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



#TOKENIZATION
TOKENIZE_SL=config["TOKENIZE_SL"]
SLTOKENIZER=config["SLTOKENIZER"]
TOKENIZE_TL=config["TOKENIZE_TL"]
TLTOKENIZER=config["TLTOKENIZER"]
    
#CLEANING
CLEAN=config["CLEAN"]
CLEAN_MIN_TOK=config["CLEAN_MIN_TOK"]
CLEAN_MAX_TOK=config["CLEAN_MAX_TOK"]

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
    ROOTNAME_ALI="train.pre"
if APPLY_BPE:
    ROOTNAME_ALI="train.bpe"
ALIGNER=config["ALIGNER"]
#one of eflomal, fast_align
BOTH_DIRECTIONS=config["BOTH_DIRECTIONS"]
#only for fast_align, eflomal aligns always the two directions at the same time
DELETE_EXISTING=config["DELETE_EXISTING"]
DELETE_TEMP=config["DELETE_TEMP"]

#GUIDED ALIGNMENT VALID
GUIDED_ALIGNMENT_VALID=config["GUIDED_ALIGNMENT_VALID"]
if not APPLY_BPE:
    ROOTNAME_ALI_VALID="val.pre"
if APPLY_BPE:
    ROOTNAME_ALI_VALID="val.bpe"
ALIGNER_VALID=config["ALIGNER_VALID"]
#one of eflomal, fast_align
BOTH_DIRECTIONS_VALID=config["BOTH_DIRECTIONS"]
#only for fast_align, eflomal aligns always the two directions at the same time
DELETE_EXISTING_VALID=config["DELETE_EXISTING"]
DELETE_TEMP_VALID=config["DELETE_TEMP"]

tokenizerSL=importlib.import_module(SLTOKENIZER)
tokenizerTL=importlib.import_module(TLTOKENIZER)

       

if LEARN_TRUECASER_SL:
    print("Starting training SL truecaser")
    truecasemodel="tc."+SL
    filenameSL=ROOTNAME+"."+SL
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
    os.remove("traintruecaser.temp")
    print("End of traning SL truecaser")
    
if LEARN_TRUECASER_TL:
    print("Starting training TL truecaser")
    truecasemodel="tc."+TL
    filenameTL=ROOTNAME+"."+TL
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
    os.remove("traintruecaser.temp")
    print("End of traning TL truecaser")
    

filenameSL=ROOTNAME+"."+SL
entradaSL=codecs.open(filenameSL,"r",encoding="utf-8")

filenameTL=ROOTNAME+"."+TL
entradaTL=codecs.open(filenameTL,"r",encoding="utf-8")


sortidaTMPSL=codecs.open("corpusSL.temp","w",encoding="utf-8")
sortidaTMPTL=codecs.open("corpusTL.temp","w",encoding="utf-8")

while 1:
    liniaSL=entradaSL.readline()
    if not liniaSL:
        break
    liniaSL=liniaSL.strip()
    liniaTL=entradaTL.readline()
    liniaTL=liniaTL.strip()
    if TOKENIZE_SL:
        tokensSL=tokenizerSL.tokenize_mn(liniaSL)
    if TOKENIZE_TL:
        tokensTL=tokenizerTL.tokenize_mn(liniaTL)
    if not CLEAN:
        toclean=False
    else:
        toclean=cleaner.clean(tokensSL,tokensTL,CLEAN_MIN_TOK,CLEAN_MAX_TOK)
    if not toclean:
        liniaSL=liniaSL.strip()
        liniaTL=liniaTL.strip()
        if len(liniaSL)>0 and len(liniaTL)>0:
            sortidaTMPSL.write(liniaSL+"\n")
            sortidaTMPTL.write(liniaTL+"\n")
    

        
if SPLIT_CORPUS:
    print("SPLITTING CORPUS")
    NUMOFLINES=file_len("corpusSL.temp")
    NLTRAIN=NUMOFLINES - lval -leval
    parameters=["train."+SL,NLTRAIN,"val."+SL,lval,"eval."+SL,leval]
    split_corpus("corpusSL.temp",parameters)
    parameters=["train."+TL,NLTRAIN,"val."+TL,lval,"eval."+TL,leval]
    split_corpus("corpusTL.temp",parameters)
    
#TRUECASE train_COMBI val_SPE eval_SPE

print("Truecasing corpora...")

tc_modelSL = truecaserSL.load_model("tc."+SL)
tc_modelTL = truecaserTL.load_model("tc."+TL)

entradaSL=codecs.open("train."+SL,"r",encoding="utf-8")
entradaTL=codecs.open("train."+TL,"r",encoding="utf-8")

sortidaSL=codecs.open("train.pre."+SL,"w",encoding="utf-8")
sortidaTL=codecs.open("train.pre."+TL,"w",encoding="utf-8")


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


entradaSL=codecs.open("val."+SL,"r",encoding="utf-8")
entradaTL=codecs.open("val."+TL,"r",encoding="utf-8")

sortidaSL=codecs.open("val.pre."+SL,"w",encoding="utf-8")
sortidaTL=codecs.open("val.pre."+TL,"w",encoding="utf-8")


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
        
        liniaSL=liniaSL.strip()
        liniaTL=liniaTL.strip()
        sortidaSL.write(liniaSL+"\n")
        sortidaTL.write(liniaTL+"\n")
        
entradaSL.close()
entradaTL.close()
sortidaSL.close()
sortidaTL.close()

entradaSL=codecs.open("eval."+SL,"r",encoding="utf-8")
entradaTL=codecs.open("eval."+TL,"r",encoding="utf-8")

sortidaSL=codecs.open("eval.pre."+SL,"w",encoding="utf-8")
sortidaTL=codecs.open("eval.pre."+TL,"w",encoding="utf-8")


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
    print("LEARNING BPE")
    if JOIN_LANGUAGES: 
        print("JOINING LANGUAGES")
        command="subword-nmt learn-joint-bpe-and-vocab --input "+"train.pre."+SL+" train.pre."+TL+" -s "+str(NUM_OPERATIONS)+" -o codes_file --write-vocabulary vocab_BPE."+SL+" vocab_BPE."+TL
        os.system(command)
    else:
        if PROCESS_SL:
            print("SL")
            command="subword-nmt learn-joint-bpe-and-vocab --input "+"train.pre."+SL+" -s "+str(NUM_OPERATIONS)+" -o codes_file."+SL+" --write-vocabulary vocab_BPE."+SL
            os.system(command)
        if PROCESS_TL:
            print("TL")
            command="subword-nmt learn-joint-bpe-and-vocab --input "+"train.pre."+TL+" -s "+str(NUM_OPERATIONS)+" -o codes_file."+TL+" --write-vocabulary vocab_BPE."+TL
            os.system(command)
            
if APPLY_BPE: 
    print("APPLYING BPE")
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
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"train.pre."+SL+" > train.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"train.pre."+TL+" > train.bpe.temp."+TL
        os.system(command)
        #val
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"val.pre."+SL+" > val.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"val.pre."+TL+" > val.bpe.temp."+TL
        os.system(command)
        #eval
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"eval.pre."+SL+" > eval.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" < "+"eval.pre."+TL+" > eval.bpe.temp."+TL
        os.system(command)
        
        
    if BPE_DROPOUT:
        print("BPE DROPOUT")
        print("SL using ",BPESL)
        #train
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"train.pre."+SL+" > train.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"train.pre."+TL+" > train.bpe.temp."+TL
        os.system(command)
        #val
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"val.pre."+SL+" > val.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"val.pre."+TL+" > val.bpe.temp."+TL
        os.system(command)
        #eval
        command="subword-nmt apply-bpe -c "+BPESL+" --vocabulary vocab_BPE."+SL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"eval.pre."+SL+" > eval.bpe.temp."+SL
        os.system(command)
        print("TL using",BPETL)
        command="subword-nmt apply-bpe -c "+BPETL+" --vocabulary vocab_BPE."+TL+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --dropout "+str(BPE_DROPOUT_P)+" < "+"eval.pre."+TL+" > eval.bpe.temp."+TL
        os.system(command)
        
        
    #train
    entradaBPETEMPSL=codecs.open("train.bpe.temp."+SL,"r",encoding="utf-8")
    sortidaBPESL=codecs.open("train.bpe."+SL,"w",encoding="utf-8")
    for linia in entradaBPETEMPSL:
        linia=linia.strip()
        linia=adapt_output(linia)
        sortidaBPESL.write(linia+"\n")
    entradaBPETEMPTL=codecs.open("train.bpe.temp."+TL,"r",encoding="utf-8")
    sortidaBPETL=codecs.open("train.bpe."+TL,"w",encoding="utf-8")
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
    sortidaBPESL=codecs.open("val.bpe."+SL,"w",encoding="utf-8")
    for linia in entradaBPETEMPSL:
        linia=linia.strip()
        linia=adapt_output(linia)
        sortidaBPESL.write(linia+"\n")
    entradaBPETEMPTL=codecs.open("val.bpe.temp."+TL,"r",encoding="utf-8")
    sortidaBPETL=codecs.open("val.bpe."+TL,"w",encoding="utf-8")
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
    sortidaBPESL=codecs.open("eval.bpe."+SL,"w",encoding="utf-8")
    for linia in entradaBPETEMPSL:
        linia=linia.strip()
        linia=adapt_output(linia)
        sortidaBPESL.write(linia+"\n")
    entradaBPETEMPTL=codecs.open("eval.bpe.temp."+TL,"r",encoding="utf-8")
    sortidaBPETL=codecs.open("eval.bpe."+TL,"w",encoding="utf-8")
    for linia in entradaBPETEMPTL:
        linia=linia.strip()
        linia=adapt_output(linia)
        sortidaBPETL.write(linia+"\n")
    entradaBPETEMPSL.close()
    sortidaBPESL.close()
    entradaBPETEMPTL.close()
    sortidaBPETL.close()
    
    os.remove("train.bpe.temp."+SL)
    os.remove("train.bpe.temp."+TL)
    os.remove("val.bpe.temp."+SL)
    os.remove("val.bpe.temp."+TL)
    os.remove("eval.bpe.temp."+SL)
    os.remove("eval.bpe.temp."+TL)
        
        


if GUIDED_ALIGNMENT:
    print("GUIDED ALIGNMENT")
    print("Using aligner:", ALIGNER)
    if DELETE_EXISTING:
        FILE=ROOTNAME_ALI+"."+SL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
        FILE=ROOTNAME_ALI+"."+TL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    FILE1=ROOTNAME_ALI+"."+SL
    FILE2=ROOTNAME_ALI+"."+TL
    FILEOUT="corpus."+SL+"."+TL+".fa"
    command="paste "+FILE1+" "+FILE2+" | sed 's/\\t/ ||| /g' > "+FILEOUT
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

if os.path.exists("corpusSL.temp"):        
    os.remove("corpusSL.temp")
if os.path.exists("corpusTL.temp"):        
    os.remove("corpusTL.temp")
FILEOUT="corpus."+SL+"."+TL+"."+"fa"
if os.path.exists(FILEOUT):
    os.remove(FILEOUT)
    
    
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

if os.path.exists("corpusSL.temp"):        
    os.remove("corpusSL.temp")
if os.path.exists("corpusTL.temp"):        
    os.remove("corpusTL.temp")
FILEOUT="corpus."+SL+"."+TL+"."+"fa"
if os.path.exists(FILEOUT):
    os.remove(FILEOUT)
    
