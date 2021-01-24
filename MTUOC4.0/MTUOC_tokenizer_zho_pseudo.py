#    MTUOC_tokenizer_zho_pseudo 3.1
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

import string
import re
import sys
import os
import html

#' &#39;
#" &#34;
#- &#45;
#< &#60;
#> &#62;
#= &#61;
#space &#32;
#/ &#47;
#{ &#123;
#} &#125;

subs=[]

re_num = re.compile(r'[\d\,\.]+')

def spliteKeyWord(str):
       regex = r"[\u4e00-\ufaff]|[0-9]+|[a-zA-Z]+\'*[a-z]*|."
       matches = re.findall(regex, str, re.UNICODE)
       return matches

def split_numbers(segment):
    xifres = re.findall(re_num,segment)
    for xifra in xifres:
        xifrastr=str(xifra)
        xifrasplit=xifra.split()
        xifra2="￭ ".join(xifra)
        segment=segment.replace(xifra,xifra2)
    return(segment)



def protect_tags(segment):
    tags=re.findall(r'<[^>]+>',segment)
    for tag in tags:
        ep=False
        ef=False
        if segment.find(" "+tag)==-1:ep=True
        if segment.find(tag+" ")==-1:ef=True
        tagmod=tag.replace("<","&#60;").replace(">","&#62;").replace("=","&#61;").replace("'","&#39;").replace('"',"&#34;").replace("/","&#47;").replace(" ","&#32;")
        if ep: tagmod=" ￭"+tagmod
        if ef: tagmod=tagmod+"￭ "
        segment=segment.replace(tag,tagmod)
    tags=re.findall(r'\{[0-9]+\}',segment)
    for tag in tags:
        ep=False
        ef=False
        if segment.find(" "+tag)==-1:ep=True
        if segment.find(tag+" ")==-1:ef=True
        tagmod=tag.replace("{","&#123;").replace("}","&#125;")
        if ep: tagmod=" ￭"+tagmod
        if ef: tagmod=tagmod+"￭ "
        segment=segment.replace(tag,tagmod)
    return(segment) 

def unprotect(cadena):
    cadena=cadena.replace("&#39;","'").replace("&#45;","-").replace("&#60;","<").replace("&#62;",">").replace("&#34;",'"').replace("&#61;","=").replace("&#32;","▁").replace("&#47;","/").replace("&#123;","{").replace("&#125;","}")
    return(cadena)

def tokenize(segment):
    seg_list=spliteKeyWord(segment)
    tokenized = " ".join(list(seg_list))
    return(tokenized)
    
def detokenize(segment):
    desegment=segment.replace(" ","")
    return(desegment)

def tokenize_j(segment):
    seg_list=spliteKeyWord(segment)
    tokenized = " ￭".join(list(seg_list))
    return(tokenized) 

def detokenize_j(segment):
    segment=segment.replace(" ￭","")
    segment=segment.replace("￭ ","")
    segment=segment.replace("￭","")
    detok=segment
    return(detok)
    
def tokenize_jn(segment):
    seg_list=spliteKeyWord(segment)
    tokenized = " ￭".join(list(seg_list))
    tokenized=split_numbers(tokenized)
    return(tokenized)

def detokenize_jn(segment):
    segment=detokenize_j(segment)
    return(segment)
    
def tokenize_s(segment):
    seg_list=spliteKeyWord(segment)
    tokenized = " ￭".join(list(seg_list))
    tokenized=tokenized.replace("￭ ","￭")
    tokenized=tokenized.replace(" ￭","￭")
    tokenized=tokenized.replace(" "," ▁")
    tokenized=tokenized.replace("￭"," ")
    return(tokenized)
    
def detokenize_s(segment):
    segment=segment.replace(" ","")
    segment=segment.replace("▁"," ")
    detok=segment
    return(detok)

def tokenize_sn(segment):
    seg_list=spliteKeyWord(segment)
    tokenized = " ￭".join(list(seg_list))
    tokenized=split_numbers(tokenized)
    tokenized=tokenized.replace("￭ ","￭")
    tokenized=tokenized.replace(" ￭","￭")
    tokenized=tokenized.replace(" "," ▁")
    tokenized=tokenized.replace("￭"," ")
    return(tokenized)

def detokenize_sn(segment):
    segment=detokenize_s(segment)
    return(segment)

def print_help():
    print("MTUOC_tokenizer_zho_jieba.py A pseduo tokenizer for Chinese, usage:")
    print("Simple tokenization:")
    print('    cat "sentence to tokenize." | python3 MTUOC_tokenizer_zho_pseudo.py tokenize')
    print('    python3 MTUOC_tokenizer_zho_pseudo.py tokenize < file_to_tokenize > tokenized_file')
    print()
    print("Simple detokenization:")
    print('    cat "sentence to tokenize." | python3 MTUOC_tokenizer_zho_pseudo.py detokenize')
    print('    python3 MTUOC_tokenizer_zho_pseudo.py detokenize < file_to_detokenize > detokenized_file')
    print()
    print("Advanced options:")
    print("    tokenization/detokenization with joiner marks (￭): tokenize_j / detokenize_j")
    print("    tokenization/detokenization with joiner marks (￭) and number splitting: tokenize_jn / detokenize_jn")
    print("    tokenization/detokenization with splitter marks (▁): tokenize_s / detokenize_s")
    print("    tokenization/detokenization with splitter marks (▁) and number splitting: tokenize_sn / detokenize_sn")
        

if __name__ == "__main__":
    if len(sys.argv)>1:
        if sys.argv[1]=="-h" or sys.argv[1]=="--help":
            print_help()
            sys.exit()
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
        elif action=="detokenize":
            outsegment=detokenize(line)
        
        elif action=="tokenize_s":
            outsegment=tokenize_s(line)
        elif action=="detokenize_s":
            outsegment=detokenize_s(line)
        elif action=="tokenize_sn":
            outsegment=tokenize_sn(line)
        elif action=="detokenize_sn":
            outsegment=detokenize_sn(line)
        
        elif action=="tokenize_j":
            outsegment=tokenize_j(line)
        elif action=="detokenize_j":
            outsegment=detokenize_j(line)
        elif action=="tokenize_jn":
            outsegment=tokenize_jn(line)
        elif action=="detokenize_jn":
            outsegment=detokenize_jn(line)
        
        print(outsegment)
