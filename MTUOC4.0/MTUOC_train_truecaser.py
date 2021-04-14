#    MTUOC_train_truecaser
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

class TC_Trainer():
    def __init__(self, MTUOCPath=".", tc_model=None, corpus=None, dictionary=None, tokenizer=None, ):
        self.initchars=["¡","¿","-","*","+","'",'"',"«","»","—","‘","’","“","”","„",]
        if tokenizer==None:
            self.tokenizer=None
        else:
            tokenizer=MTUOCPath+"/"+tokenizer

            if not tokenizer.endswith(".py"): tokenizer=tokenizer+".py"
            spec = importlib.util.spec_from_file_location('', tokenizer)
            tokenizermod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tokenizermod)
            self.tokenizer=tokenizermod.Tokenizer()
            
        self.corpus=corpus
        self.dictionary=dictionary
        self.tc_model=tc_model
        self.tc={}
    
    def set_MTUOCPath(self, path):
        sys.path.append(path)
        
    def set_tc_model(self, tc_model):
        self.tc_model=tc_model
    
    def set_corpus(self,corpus):
        self.corpus=corpus
        
    def set_dictionary(self,dictionary):
        self.dictionary=dictionary
    
    def set_tokenizer(self, tokenizer):
        if tokenizer.endswith(".py"):tokenizer=tokenizer.replace(".py","")
        self.module = importlib.import_module(tokenizer)
        self.tokenizer=self.module.Tokenizer()

    def detect_type(self, segment):
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
        
    def isinitsymbol(self, token):
        if len(token)==1 and token in self.initchars:
            return(True)
        else:
            return(False)
        
    def train_truecaser(self):
        tc={}
        if not self.corpus=="None":
            print("Reading corpus:",self.corpus)
            entrada=codecs.open(self.corpus,"r",encoding="utf-8")
            for line in entrada:
                line=line.strip()
                tipus=self.detect_type(line)
                if tipus=="regular":
                    #learn model only from regular segments
                    tokens=self.tokenizer.tokenize(line).split(" ")
                    position=0
                    for token in tokens:
                        if not self.isinitsymbol(token):
                            position+=1
                        key=token.lower()
                        if key==key.lower() and key==key.upper():
                            pass
                        elif position>1: #don't taking into account tokens in first position
                            tipus=""
                            if token==key:tipus="lc"
                            elif token==key.capitalize():tipus="u1"
                            elif token==key.upper():tipus="uc"
                            if not key in tc:
                                tc[key]={}
                                tc[key]["lc"]=0
                                tc[key]["u1"]=0
                                tc[key]["uc"]=0
                            if tipus=="lc":
                                tc[key]["lc"]+=1
                            elif tipus=="u1":
                                tc[key]["u1"]+=1
                            elif tipus=="uc":
                                tc[key]["uc"]+=1                           
                                    
                                
                        
        if not self.dictionary=="None":
            print("Reading dictionary:",self.dictionary)
            entrada=codecs.open(self.dictionary,"r",encoding="utf-8")
            for line in entrada:
                token=line.strip()
                key=token.lower()
                tipus=""
                tipus=""
                if token==key:tipus="lc"
                elif token==key.capitalize():tipus="u1"
                elif token==key.upper():tipus="uc"
                if not key in tc:
                    tc[key]={}
                    tc[key]["lc"]=0
                    tc[key]["u1"]=0
                    tc[key]["uc"]=0
                if tipus=="lc":
                    tc[key]["lc"]+=1
                elif tipus=="u1":
                    tc[key]["u1"]+=1
                elif tipus=="uc":
                    tc[key]["uc"]+=1
                
        pickle.dump(tc, open(self.tc_model, "wb"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MTUOC program for truecaser training.')
    parser.add_argument('-m','--model', action="store", dest="model", help='The resulting truecasing model.',required=True)
    parser.add_argument('-c','--corpus', action="store", dest="corpus", help='The corpus to be used or None.',required=True)
    parser.add_argument('-d','--dictionary', action="store", dest="dictionary", help='The dictionary to be used or None.',required=True)
    parser.add_argument('-t','--tokenizer', action="store", dest="tokenizer", help='The tokenizer to be used.',required=True)
    parser.add_argument('--mtuoc','--MTUOC', action="store", dest="MTUOC", help='The path to the MTUOC components',required=False)
    
    args = parser.parse_args()
    model=args.model
    corpus=args.corpus
    dictionary=args.dictionary
    if args.MTUOC:
        MTUOCPath=args.MTUOC
    else:
        MTUOCPath=""
    tokenizer=args.tokenizer
    trainer=TC_Trainer(MTUOCPath, model, corpus, dictionary, tokenizer)
    trainer.train_truecaser()
    
