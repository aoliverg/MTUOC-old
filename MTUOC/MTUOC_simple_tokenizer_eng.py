#    MTUOC_tokenizer_eng
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

try:
    import pyonmttok
    pt=True
except:
    pt=False
    
print("PT",pt)

from nltk import word_tokenize
import sys
import html
import re

subs=["￭'s","￭'ll","￭'t","￭'cause","￭'d","￭'em","￭'ve","￭'dn","￭'m","￭'n","￭'re","￭'til","￭'tween","￭'all","ol'￭"]
sorted_subs = sorted(subs, key=len, reverse=True)
subs=sorted_subs

def tokenize(segment):
    for sub in subs:
        pA=sub.replace("￭","")
        pB=sub.replace("￭"," ")
        pAUp=pA.upper()
        pBUp=pB.upper()
        segment=segment.replace(pA,pB)
        segment=segment.replace(pAUp,pBUp)
        
        
    tokens = word_tokenize(segment)
    print(tokens)
    tokenized=" ".join(tokens)       
    return(tokenized) 

   
def detokenize(segment):
    for sub in subs:
        sub1=sub.replace("￭"," ")
        sub2=sub.replace("￭","")
        segment=segment.replace(sub1,sub2)
    segment=segment.replace(" .",".")
    segment=segment.replace(" ,",",")
    segment=segment.replace(" :",":")
    segment=segment.replace(" ;",";")
    segment=segment.replace(" :",":")
    segment=segment.replace(" )",")")
    segment=segment.replace("( ","(")
    segment=segment.replace(" ]","]")
    segment=segment.replace("[ ","[")
    segment=segment.replace(" }","}")
    segment=segment.replace("{ ","{")
    segment=segment.replace(" !","!")
    segment=segment.replace("¡ ","¡")
    segment=segment.replace(" ?","?")
    segment=segment.replace("¿ ","¿")
    segment=segment.replace(" »","»")
    segment=segment.replace("« ","«")
    segment=segment.replace("‘ ","‘")
    segment=segment.replace(" ’","’")
    segment=segment.replace("“ ","“")
    segment=segment.replace(" ”","”")
    detok=segment
    return(detok)

def detokenize_m(segment):
    tokenizer = pyonmttok.Tokenizer("aggressive", segment_numbers=False, joiner_annotate=False)
    segment=tokenizer.detokenize(segment.split(" "))
    for sub in subs:
        sub1=sub.replace("￭"," ")
        sub2=sub.replace("￭","")
        segment=segment.replace(sub1,sub2)
    detok=segment
    return(detok)
    
def detokenize_mn(segment):
    tokenizer = pyonmttok.Tokenizer("aggressive", segment_numbers=True, joiner_annotate=False)
    segment=tokenizer.detokenize(segment.split(" "))
    detok=segment
    return(detok)
        

if __name__ == "__main__":
    if len(sys.argv)>1:
        action=sys.argv[1]
    else:
        action="tokenize"
    for line in sys.stdin:
        line=line.strip()
        #normalization of apostrophe
        line=line.replace("’","'")
        line=html.unescape(line)
        if action=="tokenize":
            outsegment=tokenize(line)
        elif action=="tokenize_m":
            outsegment=tokenize_m(line)
        elif action=="tokenize_mn":
            outsegment=tokenize_mn(line)
        elif action=="detokenize":
            outsegment=detokenize(line)
        elif action=="detokenize_m":
            outsegment=detokenize_m(line)
        elif action=="detokenize_mn":
            outsegment=detokenize_mn(line)
        print(outsegment)
        
