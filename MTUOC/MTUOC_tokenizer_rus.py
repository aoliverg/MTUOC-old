#    MTUOC_tokenizer_rus
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

import pyonmttok
import sys
import html
import re


#subs=['кое￭-￭кем', 'кое￭-￭кого', 'кое￭-￭ком', 'кое￭-￭кому', 'кое￭-￭кто', 'кое￭-￭чего', 'кое￭-￭чем', 'кое￭-￭чему', 'кое￭-￭что', 'кой￭-￭кем', 'кой￭-￭кого', 'кой￭-￭ком', 'кой￭-￭кому', 'кой￭-￭кто', 'кой￭-￭чего', 'кой￭-￭чем', 'кой￭-￭чему', 'кой￭-￭что', 'чего￭-￭то', 'что￭-￭либо', 'что￭-￭нибудь', 'что￭-￭то', 'как￭-￭либо', 'как￭-￭нибудь', 'как￭-￭никак', 'как￭-￭то', 'то￭-￭то', 'тот￭-￭то', 'чей￭-￭либо', 'чей￭-￭нибудь', 'чей￭-￭то', 'а￭-￭ля', 'из￭-￭за', 'из￭-￭под', 'из￭-￭подо', 'по￭-￭за', 'по￭-￭над', 'вот￭-￭вот', 'все￭-￭таки', 'едва￭-￭едва', 'еле￭-￭еле', 'на￭-￭ка', 'нате￭-￭ка', 'ни￭-￭ни', 'сем￭-￭ка', 'так￭-￭таки', 'так￭-￭то', 'то￭-￭то', 'все￭-￭таки', 'только￭-￭только', 'ва￭-￭банк', 'в￭-￭восьмых', 'в￭-￭девятых', 'в￭-￭десятых', 'видимо￭-￭невидимо', 'во￭-￭вторых', 'волей￭-￭неволей', 'воленс￭-￭ноленс', 'волоконно￭-￭оптически', 'во￭-￭первых', 'вот￭-￭вот', 'в￭-￭пятых', 'всего￭-￭навсего', 'всего￭-￭то', 'в￭-￭седьмых', 'в￭-￭третьих', 'в￭-￭четвертых', 'в￭-￭шестых', 'где￭-￭либо', 'где￭-￭нибудь', 'где￭-￭то', 'давным￭-￭давно', 'день￭-￭деньской', 'де￭-￭факто', 'де￭-￭юре', 'дизель￭-￭электрически', 'довольно￭-￭таки', 'едва￭-￭едва', 'еле￭-￭еле', 'зачем￭-￭либо', 'зачем￭-￭нибудь', 'зачем￭-￭то', 'инженерно￭-￭физически', 'ин￭-￭кварто', 'ин￭-￭октаво', 'ин￭-￭фолио', 'как￭-￭либо', 'как￭-￭нибудь', 'как￭-￭никак', 'как￭-￭то', 'когда￭-￭либо', 'когда￭-￭нибудь', 'когда￭-￭то', 'кое￭-￭где', 'кое￭-￭как', 'кое￭-￭когда', 'кое￭-￭куда', 'кой￭-￭где', 'кой￭-￭как', 'кой￭-￭когда', 'кой￭-￭куда', 'крепко￭-￭накрепко', 'крест￭-￭накрест', 'куда￭-￭либо', 'куда￭-￭нибудь', 'куда￭-￭то', 'лиро￭-￭эпически', 'логико￭-￭математически', 'мало￭-￭мальски', 'мало￭-￭помалу', 'на￭-￭гора', 'на￭-￭ка', 'народно￭-￭демократически', 'нате￭-￭ка', 'научно￭-￭технически', 'научно￭-￭фантастически', 'нежданно￭-￭негаданно', 'ни￭-￭ни', 'оптико￭-￭механически', 'опять￭-￭таки', 'откуда￭-￭либо', 'откуда￭-￭нибудь', 'откуда￭-￭то', 'отчего￭-￭либо', 'отчего￭-￭нибудь', 'отчего￭-￭то', 'перво￭-￭наперво', 'по￭-￭английски', 'по￭-￭бабьи', 'по￭-￭барски', 'по￭-￭божески', 'по￭-￭братски', 'по￭-￭вашему', 'по￭-￭весеннему', 'по￭-￭видимому', 'по￭-￭военному', 'по￭-￭волчьи', 'по￭-￭воровски', 'по￭-￭всякому', 'по￭-￭городски', 'по￭-￭деловому', 'по￭-￭деревенски', 'по￭-￭детски', 'по￭-￭джентльменски', 'подобру￭-￭поздорову', 'по￭-￭домашнему', 'по￭-￭другому', 'по￭-￭дружески', 'по￭-￭дурацки', 'по￭-￭женски', 'по￭-￭заячьи', 'по￭-￭зимнему', 'по￭-￭иному', 'по￭-￭каковски', 'по￭-￭квакерски', 'по￭-￭королевски', 'по￭-￭кошачьи', 'по￭-￭летнему', 'политико￭-￭экономически', 'полным￭-￭полно', 'по￭-￭любительски', 'по￭-￭людски', 'по￭-￭лягушачьи', 'по￭-￭мальчишески', 'по￭-￭мальчишечьи', 'по￭-￭матерински', 'по￭-￭медвежьи', 'по￭-￭моему', 'по￭-￭молодецки', 'по￭-￭моряцки', 'по￭-￭мужски', 'по￭-￭настоящему', 'по￭-￭нашему', 'по￭-￭немецки', 'по￭-￭нищенски', 'по￭-￭новому', 'по￭-￭нынешнему', 'по￭-￭осеннему', 'по￭-￭отечески', 'по￭-￭отцовски', 'по￭-￭поросячьи', 'по￭-￭прежнему', 'по￭-￭простецки', 'по￭-￭птичьи', 'по￭-￭пустому', 'по￭-￭разному', 'по￭-￭ребячески', 'по￭-￭ребячьи', 'по￭-￭русски', 'по￭-￭рыцарски', 'по￭-￭светски', 'по￭-￭свински', 'по￭-￭своему', 'по￭-￭свойски', 'по￭-￭сиротски', 'по￭-￭скотски', 'по￭-￭собачьи', 'по￭-￭стариковски', 'по￭-￭старинному', 'по￭-￭старому', 'по￭-￭студенчески', 'по￭-￭твоему', 'по￭-￭товарищески', 'по￭-￭турецки', 'по￭-￭флотски', 'по￭-￭французски', 'по￭-￭хамски', 'по￭-￭хозяйски', 'по￭-￭хорошему', 'по￭-￭царски', 'по￭-￭человечески', 'по￭-￭человечьи', 'почему￭-￭либо', 'почему￭-￭нибудь', 'почему￭-￭то', 'по￭-￭шутовски', 'по￭-￭щегольски', 'просто￭-￭напросто', 'прямо￭-￭таки', 'римско￭-￭католически', 'сам￭-￭двадцать', 'сам￭-￭девят', 'сам￭-￭десят', 'сам￭-￭друг', 'сам￭-￭осьмой', 'сам￭-￭пят', 'сам￭-￭сем', 'сам￭-￭третей', 'сам￭-￭четверт', 'сам￭-￭шест', 'силлабо￭-￭тонически', 'сколько￭-￭нибудь', 'сколько￭-￭то', 'социал￭-￭демократически', 'сравнительно￭-￭исторически', 'строго￭-￭настрого', 'так￭-￭то', 'темным￭-￭темно', 'тет￭-￭а￭-￭тет', 'тихо￭-￭смирно', 'тогда￭-￭то', 'только￭-￭только', 'точь￭-￭в￭-￭точь', 'трын￭-￭трава', 'туда￭-￭сюда', 'туда￭-￭то', 'тут￭-￭то', 'ура￭-￭патриотически', 'физико￭-￭математически', 'физико￭-￭технически', 'физико￭-￭химически', 'худо￭-￭бедно', 'цап￭-￭царап', 'цирлих￭-￭манирлих', 'чего￭-￭то', 'чуть￭-￭чуть', 'шаляй￭-￭валяй', 'шиворот￭-￭навыворот']
subs=[]

sorted_subs = sorted(subs, key=len, reverse=True)
subs=sorted_subs

def protect_tags(segment):
    protectedsegment=re.sub(r'(<[^>]+>)', r'｟\1｠',segment)
    return(protectedsegment)

def protect(segment):
    segment=protect_tags(segment)
    segmentList=segment.split(" ")
    segment2List=segment.split(" ")
    for i in range(0,len(segment2List)):
        for sub in subs:
            sub=sub.replace("￭","")
            replace="｟"+sub+"｠"
            replaceUC="｟"+sub.upper()+"｠"
            replaceCAP="｟"+sub.capitalize()+"｠"
            if segment2List[i].find(sub)>-1:
                segment2List[i]=segment2List[i].replace(sub,"")
                segmentList[i]=segmentList[i].replace(sub,replace)
            if segment2List[i].find(sub.upper())>-1:
                segment2List[i]=segment2List[i].replace(sub.upper(),"")
                segmentList[i]=segmentList[i].replace(sub.upper(),replaceUC)
            if segment2List[i].find(sub.upper())>-1:
                segment2List[i]=segment2List[i].replace(sub.upper(),"")
                segmentList[i]=segmentList[i].replace(sub.upper(),replaceUC)
            if segment2List[i].find(sub.capitalize())>-1:
                segment2List[i]=segment2List[i].replace(sub.capitalize(),"")
                segmentList[i]=segmentList[i].replace(sub.capitalize(),replaceCAP)
    segment=" ".join(segmentList)
    return(segment)
    
def unprotect(segment):
    segment=segment.replace("｟","")
    segment=segment.replace("｠","")
    return(segment)

def tokenize(segment):
    tokenizer = pyonmttok.Tokenizer("aggressive", segment_numbers=False, joiner_annotate=True)#this is an special case for Russian
    segment=protect(segment)
    tokens, features = tokenizer.tokenize(segment)
    tokenized=" ".join(tokens)    
    unprotected=tokenized.replace(" ￭-￭ ","-")   
    unprotected=unprotected.replace("￭","")   
    unprotected=unprotect(unprotected).replace("％0020"," ")
    return(unprotected) 

def tokenize_m(segment):
    tokenizer = pyonmttok.Tokenizer("aggressive", segment_numbers=False, joiner_annotate=True)
    segment=protect(segment)
    tokens, features = tokenizer.tokenize(segment)
    tokenized=" ".join(tokens)       
    unprotected=unprotect(tokenized).replace("％0020"," ")
    unprotected=unprotected.replace(" ￭-￭ ","-")
    return(unprotected) 
    
def tokenize_mn(segment):
    tokenizer = pyonmttok.Tokenizer("aggressive", segment_numbers=True, joiner_annotate=True)
    segment=protect(segment)
    tokens, features = tokenizer.tokenize(segment)
    tokenized=" ".join(tokens)       
    unprotected=unprotect(tokenized).replace("％0020"," ")
    unprotected=unprotected.replace(" ￭-￭ ","-")
    return(unprotected) 
    
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
