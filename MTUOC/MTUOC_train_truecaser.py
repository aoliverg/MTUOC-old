#    MTUOC_train_truecaser
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
import codecs
import pickle
import argparse




def detect_type(segment):
    #regular,uppercased,titled
    tipus="unknown"
    tokens=segment.split(" ")
    ntok=len(tokens)
    utokens=0
    ltokens=0
    for token in tokens:
        if token.isalpha() and token==token.lower():
            ltokens+=1
        elif token.isalpha():
            utokens+=1
    if ntok>=5 and utokens>=ntok/2:
        tipus="titled"
    elif segment==segment.upper():
        tipus="uppercased"
    else:
        tipus="regular"

    return(tipus)
    
    
def train_truecaser(model,corpus,dictionary):
    tc_model={}
    if not corpus=="none":
        print("Reading corpus:",corpus)
        entrada=codecs.open(corpus,"r",encoding="utf-8")
        for line in entrada:
            line=line.strip()
            tipus=detect_type(line)
            if tipus=="regular":
                #learn model only from regular segments
                tokens=line.split(" ")
                position=0
                for token in tokens:
                    position+=1
                    key=token.lower()
                    if key==key.lower() and key==key.upper():
                        pass
                    elif position>1: #don't taking into account tokens in first position
                        tipus=""
                        if token==key:tipus="lc"
                        elif token==key.capitalize():tipus="u1"
                        else: tipus="other"
                        if not key in tc_model:
                            tc_model[key]={}
                            tc_model[key]["lc"]=0
                            tc_model[key]["u1"]=0
                        if tipus=="lc":
                            tc_model[key]["lc"]+=1
                        elif tipus=="u1":
                            tc_model[key]["u1"]+=1
                        elif tipus=="other":
                            if not key in tc_model:
                                tc_model[key]={}
                                tc_model[key]["lc"]=0
                                tc_model[key]["u1"]=0
                            if not token in tc_model[key]:
                                tc_model[key][token]=1
                            else:
                                tc_model[key][token]+=1
                                
                            
                    
    if not dictionary=="none":
        print("Reading dictionary:",dictionary)
        entrada=codecs.open(dictionary,"r",encoding="utf-8")
        for line in entrada:
            token=line.strip()
            key=token.lower()
            tipus=""
            if token==key:tipus="lc"
            elif token==key.capitalize():tipus="u1"
            else: tipus="other"
            if not key in tc_model:
                tc_model[key]={}
                tc_model[key]["lc"]=0
                tc_model[key]["u1"]=0
            if tipus=="lc":
                tc_model[key]["lc"]+=1
            elif tipus=="u1":
                tc_model[key]["u1"]+=1
            elif tipus=="other":
                if not key in tc_model:
                    tc_model[key]={}
                    tc_model[key]["lc"]=0
                    tc_model[key]["u1"]=0
                if not token in tc_model[key]:
                    tc_model[key][token]=1
                else:
                    tc_model[key][token]+=1
            
    pickle.dump(tc_model, open(model, "wb"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MTUOC program for truecaser training.')
    parser.add_argument('-m','--model', action="store", dest="model", help='The resulting truecasing model.',required=True)
    parser.add_argument('-c','--corpus', action="store", dest="corpus", help='The tokenizer to be used.',required=False)
    parser.add_argument('-d','--dictionary', action="store", dest="dictionary", help='The tokenizer to be used.',required=False)
    

    args = parser.parse_args()
    model=args.model
    corpus=args.corpus
    dictionary=args.dictionary
    train_truecaser(model,corpus,dictionary)
    
