#    MTUOC_tokenizer_zho_jieba 4.0
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
import jieba
    

class Tokenizer():
    def __init__(self):
        self.specialchars=["«","»","—","‘","’","“","”","„",]
        self.subs=["￭'s","￭'ll","￭'t","￭'cause","￭'d","￭'em","￭'ve","￭'dn","￭'m","￭'n","￭'re","￭'til","￭'tween","￭'all","ol'￭"]
        self.re_num = re.compile(r'[\d\,\.]+')
        jieba.set_dictionary('dict.txt.big')

    def split_numbers(self,segment):
        xifres = re.findall(self.re_num,segment)
        for xifra in xifres:
            xifrastr=str(xifra)
            xifrasplit=xifra.split()
            xifra2="￭ ".join(xifra)
            segment=segment.replace(xifra,xifra2)
        return(segment)



    def protect_tags(self, segment):
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

    def unprotect(self, cadena):
        cadena=cadena.replace("&#39;","'").replace("&#45;","-").replace("&#60;","<").replace("&#62;",">").replace("&#34;",'"').replace("&#61;","=").replace("&#32;","▁").replace("&#47;","/").replace("&#123;","{").replace("&#125;","}")
        return(cadena)


    def tokenize(self, segment):
        seg_list = jieba.cut(segment, cut_all=False)
        tokenized = " ".join(list(seg_list))
        return(tokenized)
        
    def detokenize(self, segment):
        desegment=segment.replace(" ","")
        return(desegment)

    def tokenize_j(self, segment):
        seg_list = jieba.cut(segment, cut_all=False)
        tokenized = " ￭".join(list(seg_list))
        return(tokenized) 

    def detokenize_j(self, segment):
        segment=segment.replace(" ￭","")
        segment=segment.replace("￭ ","")
        segment=segment.replace("￭","")
        detok=segment
        return(detok)
        
    def tokenize_jn(self, segment):
        seg_list = jieba.cut(segment, cut_all=False)
        tokenized = " ￭".join(list(seg_list))
        tokenized=self.split_numbers(tokenized)
        return(tokenized)

    def detokenize_jn(self, segment):
        segment=self.detokenize_j(segment)
        return(segment)
        
    def tokenize_s(self, segment):
        seg_list = jieba.cut(segment, cut_all=False)
        #seg_list=self.remove_spaces_from_list(seg_list)
        tokenized = " ￭".join(seg_list)
        tokenized=tokenized.replace("￭ ","￭")
        tokenized=tokenized.replace(" ￭","￭")
        tokenized=tokenized.replace(" "," ▁")
        tokenized=tokenized.replace("￭"," ")
        return(tokenized)
        
    def detokenize_s(self, segment):
        segment=segment.replace(" ","")
        segment=segment.replace("▁"," ")
        detok=segment
        return(detok)

    def tokenize_sn(self, segment):
        seg_list = jieba.cut(segment, cut_all=False)
        tokenized = " ￭".join(list(seg_list))
        tokenized=self.split_numbers(tokenized)
        tokenized=tokenized.replace("￭ ","￭")
        tokenized=tokenized.replace(" ￭","￭")
        tokenized=tokenized.replace(" "," ▁")
        tokenized=tokenized.replace("￭"," ")
        return(tokenized)

    def detokenize_sn(self, segment):
        segment=self.detokenize_s(segment)
        return(segment)     

    
def print_help():
    print("MTUOC_tokenizer_zho_jieba.py A tokenizer for Chinese (using jieba), usage:")
    print("Simple tokenization:")
    print('    cat "sentence to tokenize." | python3 MTUOC_tokenizer_zho_jieba.py tokenize')
    print('    python3 MTUOC_tokenizer_zho_jieba.py tokenize < file_to_tokenize > tokenized_file')
    print()
    print("Simple detokenization:")
    print('    cat "sentence to tokenize." | python3 MTUOC_tokenizer_zho_jieba.py detokenize')
    print('    python3 MTUOC_tokenizer_zho_jieba.py detokenize < file_to_detokenize > detokenized_file')
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
    tokenizer=Tokenizer()
    for line in sys.stdin:
        line=line.strip()
        #normalization of apostrophe
        line=line.replace("’","'")
        line=html.unescape(line)
        if action=="tokenize":
            outsegment=tokenizer.tokenize(line)
        elif action=="detokenize":
            outsegment=tokenizer.detokenize(line)
        
        elif action=="tokenize_s":
            outsegment=tokenizer.tokenize_s(line)
        elif action=="detokenize_s":
            outsegment=tokenizer.detokenize_s(line)
        elif action=="tokenize_sn":
            outsegment=tokenizer.tokenize_sn(line)
        elif action=="detokenize_sn":
            outsegment=tokenizer.detokenize_sn(line)
        
        elif action=="tokenize_j":
            outsegment=tokenizer.tokenize_j(line)
        elif action=="detokenize_j":
            outsegment=tokenizer.detokenize_j(line)
        elif action=="tokenize_jn":
            outsegment=tokenizer.tokenize_jn(line)
        elif action=="detokenize_jn":
            outsegment=tokenizer.detokenize_jn(line)
        
        print(outsegment)
