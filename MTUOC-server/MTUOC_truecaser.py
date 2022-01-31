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

class Truecaser():
    def __init__(self, MTUOCPath=".", tokenizer=None, tc_model=None):
        
        self.initchars=["¡","¿","-","*","+","'",'"',"«","»","—","‘","’","“","”","„",]
        
        if tokenizer==None:
            self.tokenizer=None
        else:
            sys.path.append(MTUOCPath)
            if tokenizer.endswith(".py"):tokenizer=tokenizer.replace(".py","")
            self.module = importlib.import_module(tokenizer)
            self.tokenizer=self.module.Tokenizer()
        if tc_model:
            self.tc_model = pickle.load(open(tc_model, "rb" ) )
        else:
            self.tc_model={}
    def set_tc_model(self, tc_model):
        self.tc_model = pickle.load(open(tc_model, "rb" ) )
        
    def set_tokenizer(self, tokenizer):
        if tokenizer.endswith(".py"):tokenizer=tokenizer.replace(".py","")
        self.module = importlib.import_module(tokenizer)
        self.tokenizer=self.module.Tokenizer()
    
    def set_MTUOCPath(self, path):
        sys.path.append(path)
        
    def isinitsymbol(self, token):
        if len(token)==1 and token in self.initchars:
            return(True)
        else:
            return(False)
        
    def detect_type(self, segment):
        tipus="unknown"
        if self.tokenizer==None:
            tokens=segment.split(" ")
        else:
            tokens=self.tokenizer.tokenize(segment)
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
        
    def truecase(self, line, ucf=False, restoreCase=False):
        if self.tokenizer:
            tokens=self.tokenizer.tokenize_s(line).split(" ")
        else:
            tokens=line.split(" ")
        nsegment=[]
        for token in tokens:
            
            try:
                leadingsplitter=False
                trailingsplitter=False
                leadingjoiner=False
                trailingjoiner=False
                if token.startswith("▁"):leadingsplitter=True
                if token.endswith("▁"):trailingsplitter=True
                if token.startswith("￭"):leadingjoiner=True
                if token.endswith("￭"):trailingjoiner=True
                token=token.replace("▁","")
                token=token.replace("￭","")
                try:
                    nlc=self.tc_model[token.lower()]["lc"]
                except:
                    nlc=0
                try:
                    nu1=self.tc_model[token.lower()]["u1"]
                except:
                    nu1=0
                try:
                    nuc=self.tc_model[token.lower()]["uc"]
                except:
                    nuc=0
                proceed=False
                if not token==token.lower(): proceed=True
                if restoreCase: proceed=True
                if proceed:
                    if nlc>0 and nlc>=nu1 and nlc>=nuc:
                        token=token.lower()
                    elif nu1>0 and nu1>nlc and nu1>nuc:
                        token=token.lower().capitalize()
                    elif nuc>0 and nuc>nlc and nuc>nu1:
                        token=token.upper()

                if leadingsplitter:token="▁"+token
                if trailingsplitter:token=token+"▁"
                if leadingjoiner:token="￭"+token
                if trailingjoiner:token=token+"￭"
                nsegment.append(token)
            except:
                print("ERROR",sys.exc_info())
                nsegment.append(token)
        if self.tokenizer:
            nsegment=self.tokenizer.detokenize_s(" ".join(nsegment))     
        else:
            nsegment=" ".join(nsegment)
        if ucf:
            if self.isinitsymbol(nsegment[0]):firstchar=1
            else: firstchar=0
            try:
                if firstchar==0:
                    nsegment=nsegment[firstchar].upper()+"".join(nsegment[1:])
                elif firstchar==1:
                    nsegment=nsegment[0]+nsegment[firstchar].upper()+"".join(nsegment[2:])
            except:
                pass
        return(nsegment)
        
    def detruecase(self,line,tokenizer):
        tokens=line.split(" ")
        new=[]
        yet=False
        if tokenizer:
            tokens=tokenizer.tokenize_j(line).split(" ")
        else:
            tokens=line.split(" ")
        for token in tokens:
            if not yet and token.isalpha():
                yet=True
                new.append(token[0].upper()+token[1:])
            else:
                new.append(token)
        line=" ".join(new)
        detrue=tokenizer.detokenize_j(line)
        return(line)    
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MTUOC program for truecasing.')
    parser.add_argument('-m','--model', action="store", dest="model", help='The truecasing model to use.',required=True)
    parser.add_argument('-t','--tokenizer', action="store", dest="tokenizer", help='The tokenizer to used',required=False)
    parser.add_argument('-u','--ucf', action="store_true", dest="ucf", help='Set if you want first word capitalized',required=False)
    parser.add_argument('-r','--restore', action="store_true", dest="restore", help='Set if you want to restore case (uppercase lower cased)',required=False)
    parser.add_argument('--mtuoc','--MTUOC', action="store", dest="MTUOC", help='The path to the MTUOC components',required=False)
    
    args = parser.parse_args()
    model=args.model
    ucf=args.ucf
    restore=args.restore
        

    if args.MTUOC:
        MTUOCPath=args.MTUOC
    else:
        MTUOCPath=""

    truecaser=Truecaser(MTUOCPath, args.tokenizer, args.model)
    for line in sys.stdin:
        line=line.strip()
        tcline=truecaser.truecase(line, ucf, restore)
        print(tcline)
    
