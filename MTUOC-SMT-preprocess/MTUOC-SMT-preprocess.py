#    MTUOC-SMT-preprocess
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

import sys
import importlib
import codecs
from datetime import datetime

def escapeforMoses(segment):
    segment=segment.replace("[","&lbrack;")
    segment=segment.replace("]","&rbrack;")    
    segment=segment.replace("|","&verbar;")
    segment=segment.replace("<","&lt;")
    segment=segment.replace(">","&gt;")
    return(segment)

###YAML IMPORTS
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    

if len(sys.argv)==1:
    configfile="config-SMT-preprocess.yaml"
else:
    configfile=sys.argv[1]

stream = open(configfile, 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)

MTUOC=config["MTUOC"]
sys.path.append(MTUOC)
from MTUOC_replacenumbers import replace

trainPreCorpus=config["trainPreCorpus"]
valPreCorpus=config["valPreCorpus"]

SL=config["SL"]
TL=config["TL"]


#VERBOSE
VERBOSE=config["VERBOSE"]

SL_TOKENIZER=config["SL_TOKENIZER"]
TL_TOKENIZER=config["TL_TOKENIZER"]

command="from "+SL_TOKENIZER+" import Tokenizer as TokenizerSL"
exec(command)
tokenizerSL=TokenizerSL()

command="from "+TL_TOKENIZER+" import Tokenizer as TokenizerTL"
exec(command)
tokenizerTL=TokenizerTL()


REPLACE_NUM=config["REPLACE_NUM"]
NUM_CODE=config["NUM_CODE"]

ESCAPE_FOR_MOSES=config["ESCAPE_FOR_MOSES"]

DELETE_TEMP=config["DELETE_TEMP"]


if not SL_TOKENIZER.endswith(".py"): SL_TOKENIZER=SL_TOKENIZER+".py"
SL_TOKENIZER=MTUOC+"/"+SL_TOKENIZER

if not TL_TOKENIZER.endswith(".py"): TL_TOKENIZER=TL_TOKENIZER+".py"
TL_TOKENIZER=MTUOC+"/"+TL_TOKENIZER

if VERBOSE: print("Processing TRAIN corpus",datetime.now())
entrada=codecs.open(trainPreCorpus,"r",encoding="utf-8")
sortidaSL=codecs.open("train.smt."+SL,"w",encoding="utf-8")
sortidaTL=codecs.open("train.smt."+TL,"w",encoding="utf-8")

for linia in entrada:
    linia=linia.rstrip()
    camps=linia.split("\t")
    try:
        if ESCAPE_FOR_MOSES:
            sls=escapeforMoses(camps[0])
            tls=escapeforMoses(camps[1])
        else:
            sls=camps[0]
            tls=camps[1]
        sltok=tokenizerSL.tokenize(sls)
        tltok=tokenizerTL.tokenize(tls)
        if REPLACE_NUM:
            sltok=replace(sltok,NUM_CODE)
            tltok=replace(tltok,NUM_CODE)            
        sortidaSL.write(sltok+"\n")
        sortidaTL.write(tltok+"\n")
    except:
        print("Error",sys.exc_info())
        pass

entrada.close()
sortidaSL.close()
sortidaTL.close()

if VERBOSE: print("Processing VAL corpus",datetime.now())        
entrada=codecs.open(valPreCorpus,"r",encoding="utf-8")
sortidaSL=codecs.open("val.smt."+SL,"w",encoding="utf-8")
sortidaTL=codecs.open("val.smt."+TL,"w",encoding="utf-8")

for linia in entrada:
    linia=linia.rstrip()
    camps=linia.split("\t")
    try:
        if ESCAPE_FOR_MOSES:
            sls=escapeforMoses(camps[0])
            tls=escapeforMoses(camps[1])
        else:
            sls=camps[0]
            tls=camps[1]
        sltok=tokenizerSL.tokenize(sls)
        tltok=tokenizerTL.tokenize(tls)
        if REPLACE_NUM:
            sltok=replace(sltok,NUM_CODE)
            tltok=replace(tltok,NUM_CODE)            
        sortidaSL.write(sltok+"\n")
        sortidaTL.write(tltok+"\n")
    except:
        pass
        
entrada.close()
sortidaSL.close()
sortidaTL.close()

