#    MTUOC_truecaser
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
import codecs
import pickle
import argparse
import importlib

initchars=["¡","¿","-","*","+","'",'"',"«","»","—","‘","’","“","”","„",]

def isinitsymbol(token):
    if len(token)==1 and token in initchars:
        return(True)
    else:
        return(False)

def load_model(model):
    if not model=="None":
        tc_model = pickle.load(open(model, "rb" ) )
    else:
        tc_model={}
    return(tc_model)
    
def detect_type(segment):
    tipus="unknown"
    tokens=segment.split(" ")
    ntok=0
    utokens=0
    ltokens=0
    leadingsplitter=False
    trailingsplitter=False
    leadingjoiner=False
    trailingsplitter=False
    for token in tokens:
        token=token.replace("▁","")
        token=token.replace("￭","")
        if token.isalpha():ntok+=1
        if token.isalpha() and token==token.lower():
            ltokens+=1
        elif token.isalpha() and not token==token.lower():
            utokens+=1
    if ntok>=5 and utokens>=ntok/2 and not segment==segment.upper():
        tipus="titled"
    elif segment==segment.upper():
        tipus="uppercased"
    else:
        tipus="regular"
    return(tipus)
    
def truecase(tc_model,tokenizer,line):
    #tipus=detect_type(line)
    #if tipus=="regular" or tipus=="titled" or tipus=="uppercased":
    if tokenizer:
        tokens=tokenizer.tokenize_s(line).split(" ")
    else:
        tokens=line.split(" ")
    nsegment=[]
    cont=0
    for token in tokens:
        try:
            leadingsplitter=False
            trailingplitter=False
            leadingjoiner=False
            trailingjoiner=False
            if token.startswith("▁"):leadingsplitter=True
            if token.endswith("▁"):trailingplitter=True
            if token.startswith("￭"):leadingjoiner=True
            if token.endswith("￭"):trailingjoiner=True
            token=token.replace("▁","")
            token=token.replace("￭","")
            try:
                nlc=tc_model[token.lower()]["lc"]
            except:
                nlc=0
            try:
                nu1=tc_model[token.lower()]["u1"]
            except:
                nu1=0
            try:
                nuc=tc_model[token.lower()]["uc"]
            except:
                nuc=0
            
            if nlc>0 and nlc>=nu1 and nlc>=nuc:
                token=token.lower()
            elif nu1>0 and nu1>nlc and nu1>nuc:
                token=token.lower().capitalize()
            elif nuc>0 and nuc>nlc and nuc>nu1:
                token=token.upper()
            if cont==1:
                token=token.capitalize()
            if leadingsplitter:token="▁"+token
            if trailingsplitter:token=token+"▁"
            if leadingjoiner:token="￭"+token
            if trailingjoiner:token=token+"￭"
            nsegment.append(token)
        except:
            nsegment.append(token)
    if tokenizer:
        nsegment=tokenizer.detokenize_s(" ".join(nsegment))     
    else:
        nsegment=" ".join(nsegment)
    return(nsegment)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MTUOC program for truecasing.')
    parser.add_argument('-m','--model', action="store", dest="model", help='The truecasing model to use.',required=True)
    parser.add_argument('-t','--tokenizer', action="store", dest="tokenizer", help='The tokenizer to used',required=False)
    parser.add_argument('-n','--no_up_first', action="store_true", dest="nuf", help='Set if you don\'t need first word capitalized',required=False)
    
    args = parser.parse_args()
    model=args.model
    nuf=args.nuf
    if args.tokenizer:
        spec = importlib.util.spec_from_file_location('', args.tokenizer)
        tokenizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tokenizer)
    else:
        tokenizer=None
        
    tc_model=load_model(model)
    for line in sys.stdin:
        line=line.strip()
        tcline=truecase(tc_model,tokenizer,line)
        if isinitsymbol(tcline[0]):firstchar=1
        else: firstchar=0
        print(firstchar)
        if not nuf:
            try:
                if firstchar==0:
                    tcline=tcline[firstchar].upper()+"".join(tcline[1:])
                elif firstchar==1:
                    tcline=tcline[0]+tcline[firstchar].upper()+"".join(tcline[2:])
            except:
                pass
            
        print(tcline)
    
