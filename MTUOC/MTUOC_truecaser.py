#    MTUOC_truecaser
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

def load_model(model):
    tc_model = pickle.load(open(model, "rb" ) )
    return(tc_model)
    
def detect_type(segment):
    tipus="unknown"
    tokens=segment.split(" ")
    ntok=0
    utokens=0
    ltokens=0
    for token in tokens:
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
    
def truecase(tc_model,line):
    tipus=detect_type(line)
    if tipus=="regular" or tipus=="titled" or tipus=="uppercased":
        tokens=line.split(" ")
        nsegment=[]
        cont=0
        for token in tokens:
            try:
                has_joiner=False
                if token.startswith("￭"):
                    has_joiner=True
                    token=token.replace("￭","")
                if token.isalpha():
                    cont+=1
                if token.lower() in tc_model and "lc" in tc_model[token.lower()] and "u1" in tc_model[token.lower()]:
                    nlc=tc_model[token.lower()]["lc"]
                    nu1=tc_model[token.lower()]["u1"]
                    if token in tc_model[token.lower()]:
                        nasis=tc_model[token.lower()][token]
                    else:
                        nasis=0
                else:
                    nlc=1
                    nu1=0
                    nasis=1

                if cont==1:
                    #is the first token in the sentence
                    if nasis >= nlc and nasis >= nu1:
                        if has_joiner:
                            nsegment.append("￭"+token)
                        else:
                            nsegment.append(token)
                    elif nlc >= nu1:                    
                        if has_joiner:
                            nsegment.append("￭"+token.lower())
                        else:
                            nsegment.append(token.lower())
                    elif nu1 >= nlc:                    
                        if has_joiner:
                            nsegment.append("￭"+token.lower().capitalize())
                        else:
                            nsegment.append(token.lower().capitalize())
                    else:
                        nsegment.append(token.lower())
                        
                        if has_joiner:
                            nsegment.append("￭"+token.lower())
                        else:
                            nsegment.append(token.lower())
                else:
                    #the rest of the tokens in the sentence
                    if nasis >= nlc and nasis >= nu1:
                        if has_joiner:
                            nsegment.append("￭"+token)
                        else:
                            nsegment.append(token)
                    elif nlc >= nu1:
                        if has_joiner:
                            nsegment.append("￭"+token.lower())
                        else:
                            nsegment.append(token.lower())
                    elif nu1 >= nasis:
                        if has_joiner:
                            nsegment.append("￭"+token.lower().capitalize())
                        else:
                            nsegment.append(token.lower().capitalize())
                    else:
                        if has_joiner:
                            nsegment.append("￭"+token.lower())
                        else:
                            nsegment.append(token.lower())
            except:
                nsegment.append(token)
                    
        return(" ".join(nsegment))


def print_help():
    print("MTUOC Truecaser: truecases a text using a model learnt using MTUOC_train_truecaser:")
    print("      python3 MTUOC_truecaser..py tcmodel.xx < corpus.tok > corpus.true")
    sys.exit()


if __name__ == "__main__":
    if len(sys.argv)==1:
        print_help()
    if len(sys.argv)>1:
        if sys.argv[1]=="-h" or sys.argv[1]=="--help":
            print_help()
    model=sys.argv[1]
    tc_model=load_model(model)
    for line in sys.stdin:
        line=line.strip()
        tcline=truecase(tc_model,line)
        tcline=tcline[0].upper()+"".join(tcline[1:])
        print(tcline)
    
