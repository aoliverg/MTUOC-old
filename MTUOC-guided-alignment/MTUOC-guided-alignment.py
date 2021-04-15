import os
import sys
from datetime import datetime

import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


stream = open('config-guided-alignment.yaml', 'r',encoding="utf-8")
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

ALIGNER=config["ALIGNER"]
#one of eflomal, fast_align

DELETE_EXISTING=config["DELETE_EXISTING"]
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
    print("GUIDED ALIGNMENT TRAINING",datetime.now())
if DELETE_EXISTING:
    FILE="train.sp."+SL+"."+TL+".align" 
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
        print("GUIDED ALIGNMENT VALID",datetime.now())
    if DELETE_EXISTING:
        FILE="val.sp."+SL+"."+SL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)
        FILE="val.sp."+TL+"."+TL+".align" 
        if os.path.exists(FILE):
            os.remove(FILE)            
    if ALIGNER_VALID=="fast_align":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_fast_align import guided_alignment_fast_align
        guided_alignment_fast_align(MTUOC,"val.sp","val.sp",SL,TL,False,VERBOSE)
        
    if ALIGNER_VALID=="eflomal":
        sys.path.append(MTUOC)
        from MTUOC_guided_alignment_eflomal import guided_alignment_eflomal
        guided_alignment_eflomal(MTUOC,"val.sp","val.sp",SL,TL,SPLIT_LIMIT,VERBOSE)
