#    MTUOC-server-SP v 4  
#    Description: an MTUOC server using Sentence Piece as preprocessing step
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

###GENERIC IMPORTS

###GENERIC IMPORTS
import sys
import threading
import os
import socket
import time
import re
from datetime import datetime
import importlib
import codecs
import xmlrpc.client
import json
import pickle
import sentencepiece as spm

import io
import lxml
import lxml.etree as ET
import html

###YAML IMPORTS
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    
    
def startMTEngineThread(startMTEngineCommand):
    if not startMTEngineCommand.endswith("&"):
        command=startMTEngineCommand +" &"
    else:
        command=startMTEngineCommand
    os.system(command)

def get_IP_info(): 
    try: 
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name) 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        return(IP)
    except: 
        IP = '127.0.0.1'
        return(IP)
    finally:
        s.close()    

def has_tags(segment):
    response=False
    tagsA = re.findall(r'</?.+?/?>', segment)
    tagsB = re.findall(r'\{[0-9]+\}', segment)
    if len(tagsA)>0 or len(tagsB)>0:
        response=True
    return(response)
    
def is_tag(token):
    response=False
    tagsA = re.match(r'</?.+?/?>', token)
    tagsB = re.match(r'\{[0-9]+\}', token)
    if tagsA or tagsB:
        response=True
    return(response)
    
def remove_tags(segment):
    segmentnotags=re.sub('(<[^>]+>)', "",segment)
    segmentnotags=re.sub('({[0-9]+})', "",segmentnotags)
    return(segmentnotags)
    
def get_tags(segment):
    tagsA = re.findall(r'</?.+?/?>', segment)
    tagsB = re.findall(r'\{[0-9]+\}', segment)
    tags=tagsA.copy()
    tags.extend(tagsB)
    return(tags)

###URLs EMAILs

def findEMAILs(string): 
    email=re.findall('\S+@\S+', string)   
    return email
    
def findURLs(string): 
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,string)       
    return [x[0] for x in url] 

def replace_EMAILs(string,code="@EMAIL@"):
    EMAILs=findEMAILs(string)
    cont=0
    for EMAIL in EMAILs:
        string=string.replace(EMAIL,code)
    return(string)

def replace_URLs(string,code="@URL@"):
    URLs=findURLs(string)
    cont=0
    for URL in URLs:
        string=string.replace(URL,code)
    return(string)
    
def restore_EMAILs(stringA,stringB,code="@EMAIL@"):
    EMAILs=findEMAILs(stringA)
    for email in EMAILs:
        stringB=stringB.replace(code,email,1)
    return(stringB)
    
def restore_URLs(stringA,stringB,code="@URL@"):
    URLs=findURLs(stringA)
    for url in URLs:
        stringB=stringB.replace(code,url,1)
    return(stringB)

###TRUECASING###

def load_tc_model(model):
    if not model=="None":
        tc_model = pickle.load(open(model, "rb" ) )
    else:
        tc_model={}
    return(tc_model)
    
def truecase(tc_model,tokenizer,line):
    if tokenizer:
        tokens=tokenizer.tokenize_j(line).split(" ")
    else:
        tokens=splitTags(line)
    nsegment=[]
    cont=0
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
        
        nsegment=tokenizer.detokenize_j(" ".join(nsegment))     
    else:
        nsegment=" ".join(nsegment)
    return(nsegment)

def detruecase(line,tokenizer):
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

#PREPROCESSING AND POSTPROCESSING

def to_MT_SP(segment,tokenizer,tcmodel,spmodel, vocab, bos="<s>", eos='</s>'):
    hastags=has_tags(segment)
    segment=segment.strip()
    if not tcmodel==None:        
        segmenttrue=truecase(tcmodel,tokenizer,segment)
    else:
        segmenttrue=segment
    
    if not hastags:
        output=sp.encode(segmenttrue)
    else:
        output=[]
        if not bos==None: output.append("<s>")
        segmenttrue=tokenizer.tokenize(segmenttrue)
        for t in splitTags(segmenttrue):
            if not is_tag(t):
                sptok=" ".join(sp2.encode(t))
                output.append(sptok)
            else:
                output.append(t)
        if not eos==None: output.append("</s>")
    output=" ".join(output)
    return(output)

def from_MT_SP(segment, tokenizer, joiner="▁",bos="<s>", eos="</s>"):
    if not bos=="None":
        segment=segment.replace(bos,"")
    if not eos=="None":
        segment=segment.replace(eos,"")
    
    #protect spaces in tags
    tags=re.findall(r'<[^>]+>',segment)
    for tag in tags:
        if tag.find(" ")>-1:
            tagmod=joiner+tag.replace(" ","&#32;")
            segment=segment.replace(tag,tagmod,1)
    segment=segment.replace(" ","")
    segment=segment.replace(joiner," ")
    for tag in tags:
        if tag.find("&#32;")>-1:
            tagmod=tag.replace(" ","&#32;")
            segment=segment.replace(tagmod,tag,1)
    segment=segment.strip()
    segmenttrue=detruecase(segment,tokenizer)
    segmentdetok=tokenizer.detokenize_j(segmenttrue)
    tags=re.findall(r'<[^>]+>',segmentdetok)
    for tag in tags:
        if tag.find("▁")>-1:
            tagmod=tag.replace("▁"," ")
            segmentdetok=segmentdetok.replace(tag,tagmod,1)
    segmentdetok=segmentdetok.strip()
    return(segmentdetok)

###

def splitTags(segment):
    tags=re.findall('(<[^>]+>)', segment)
    for tag in tags:
        tagmod=tag.replace(" ","_")
        segment=segment.replace(tag,tagmod)
    slist=segment.split(" ")
    for i in range(0,len(slist)):
        slist[i]=slist[i].replace("_"," ")
    return(slist)
    
def removeSpeChar(llista,spechar):
    for i in range(0,len(llista)):
        llista[i]=llista[i].replace(spechar,"")
    return(llista)
        

def restore_tags(SOURCENOTAGSTOKSP, SOURCETAGSTOKSP, SELECTEDALIGNMENT, TARGETNOTAGSTOKSP, spechar="▁", bos="<s>", eos="</s>"):
    relations={}
    for t in SELECTEDALIGNMENT.split(" "):
        camps=t.split("-")
        if not int(camps[0]) in relations:
            relations[int(camps[0])]=[]
        relations[int(camps[0])].append(int(camps[1]))
    f = io.BytesIO(SOURCETAGSTOKSP.encode('utf-8'))
    events = ("start", "end")
    context = ET.iterparse(f, events=events,recover=True)
    cont_g=-1
    tags=[]
    tagpairs=[]
    LISTSOURCETAGSTOKSP=splitTags(SOURCETAGSTOKSP)
    LISTSOURCETAGSTOK=removeSpeChar(LISTSOURCETAGSTOKSP,spechar)
    LISTSOURCENOTAGSTOKSP=splitTags(SOURCENOTAGSTOKSP)
    LISTTARGETNOTAGSTOKSP=splitTags(TARGETNOTAGSTOKSP)
    TEMPLIST=LISTSOURCETAGSTOKSP
    charbefore={}
    charafter={}
    for event, elem in context:
        if not elem.tag=="s":
            tag=elem.tag
            attr=elem.items()
            if event=="start":
                if len(attr)==0:
                    xmltag="<"+tag+">"
                    if SOURCETAGSTOKSP.find(xmltag)>-1: tags.append(xmltag)
                else:
                    lat=[]
                    for at in attr:
                        cadena=at[0]+"='"+str(at[1])+"'"
                        lat.append(cadena)
                    cat=" ".join(lat)
                    xmltag1="<"+tag+" "+cat+">"
                    if SOURCETAGSTOKSP.find(xmltag1)>-1: 
                        tags.append(xmltag1)
                        xmltag=xmltag1
                        
                    lat=[]
                    for at in attr:
                        cadena=at[0]+'="'+str(at[1])+'"'
                        lat.append(cadena)
                    cat=" ".join(lat)
                    xmltag2="<"+tag+" "+cat+">"
                    if SOURCETAGSTOKSP.find(xmltag2)>-1: 
                        tags.append(xmltag2)
                        xmltag=xmltag2
                        
                closingtag="</"+tag+">"
                if SOURCETAGSTOKSP.find(closingtag)>-1: 
                    tripleta=(xmltag,closingtag,elem.text)
                    tagpairs.append(tripleta)
                    
            elif event=="end":
                    xmltag="</"+tag+">"
                    if SOURCETAGSTOKSP.find(xmltag)>-1: 
                        tags.append(xmltag)
                        
                    xmltag="<"+tag+"/>"
                    if SOURCETAGSTOKSP.find(xmltag)>-1: 
                        tags.append(xmltag)
                
    preTags=[]
    postTags=[]
    for xmltag in tags:
        if SOURCETAGSTOKSP.find(xmltag)>-1: 
            chbf=SOURCETAGSTOKSP[SOURCETAGSTOKSP.index(xmltag)-1]
            charbefore[xmltag]=chbf
            chaf=SOURCETAGSTOKSP[SOURCETAGSTOKSP.index(xmltag)+len(xmltag)]
            charafter[xmltag]=chaf
    
    tagsCHAR={}
    
    for tag in tags:
        tagC=tag
        if tag in charbefore:
            cb=charbefore[tag].strip()
            tagC=cb+tag
            
        if tag in charafter:
            ca=charafter[tag].strip()
            tagC=tagC+ca
        tagsCHAR[tag]=tagC
    
    for i in range(0,len(LISTTARGETNOTAGSTOKSP)+1):
        preTags.insert(i,None)
        postTags.insert(i,None)
    
    for tripleta in tagpairs:
        #source positions
        sourcepositions=[]
        for ttrip in tripleta[2].strip().split(" "):
            try:
                postemp=LISTSOURCENOTAGSTOKSP.index(ttrip.strip())
                sourcepositions.append(postemp)
            except:
                pass
        try:
            tags.remove(tripleta[0])
            TEMPLIST.remove(tripleta[0])
                    
        except:
            pass
        try:
            tags.remove(tripleta[1])
            TEMPLIST.remove(tripleta[1])
        except:
            pass
        #target positions
        targetpositions=[]
        for position in sourcepositions:
            if position in relations: targetpositions.extend(relations[position])
            
        
        preTags[min(targetpositions)]=tagsCHAR[tripleta[0]]
        
        postTags[max(targetpositions)]=tagsCHAR[tripleta[1]]

    #isolated tags
    for tag in tags:
        try:
            preTags[relations[TEMPLIST.index(tag)][0]]=tag
            TEMPLIST.remove(tag)
        except:
            pass
    
    LISTTARGETTAGSTOKSP=[]
    for i in range(0,len(LISTTARGETNOTAGSTOKSP)):
        try:
            if preTags[i]:
                LISTTARGETTAGSTOKSP.append(preTags[i])
            LISTTARGETTAGSTOKSP.append(LISTTARGETNOTAGSTOKSP[i])
            if postTags[i]:
                LISTTARGETTAGSTOKSP.append(postTags[i])
        except:
            pass
    translationTagsSP=" ".join(LISTTARGETTAGSTOKSP)
    return(translationTagsSP)

def repairSpacesTags(slsegment,tlsegment,delimiters=[" ",".",",",":",";","?","!"]):
    sltags=get_tags(slsegment)
    tltags=get_tags(tlsegment)
    commontags=list(set(sltags).intersection(tltags))
    for tag in commontags:
        try:
            tagaux=tag
            chbfSL=slsegment[slsegment.index(tag)-1]
            chbfTL=tlsegment[tlsegment.index(tag)-1]
            tagmod=tag
            if chbfSL in delimiters and chbfTL not in delimiters:
                tagmod=" "+tagmod
            if not chbfSL in delimiters and chbfTL in delimiters:
                tagaux=" "+tagaux
            try:
                chafSL=slsegment[slsegment.index(tag)+len(tag)]
            except:
                pass
            try:
                chafTL=tlsegment[tlsegment.index(tag)+len(tag)]
            except:
                pass
            if chafSL in delimiters and not chafTL in delimiters:
                tagmod=tagmod+" "
            if not chafSL in delimiters and chafTL in delimiters:
                tagaux=tagaux+" "
            #slsegment=slsegment.replace(tagaux,tagmod,1)
            tlsegment=tlsegment.replace(tagaux,tagmod,1)
            tlsegment=tlsegment.replace("  "+tag," "+tag,1)
            tlsegment=tlsegment.replace(tag+"  ",tag+" ",1)
            
        except:
            print("ERROR in tag:",tag)
    return(tlsegment)

###

def lreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % pattern, sub, string)

def rreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' ends 'string'.
    """
    return re.sub('%s$' % pattern, sub, string)


def has_tags(segment):
    response=False
    tagsA = re.findall(r'</?.+?/?>', segment)
    tagsB = re.findall(r'\{[0-9]+\}', segment)
    if len(tagsA)>0 or len(tagsB)>0:
        response=True
    return(response)
    
def is_tag(token):
    response=False
    tagsA = re.match(r'</?.+?/?>', token)
    tagsB = re.match(r'\{[0-9]+\}', token)
    if tagsA or tagsB:
        response=True
    return(response)
    
def remove_tags(segment):
    segmentnotags=re.sub('(<[^>]+>)', "",segment)
    segmentnotags=re.sub('({[0-9]+})', "",segmentnotags)
    return(segmentnotags)
    
def get_name(tag):
    name=tag.split(" ")[0].replace("<","").replace(">","").replace("/","")
    return(name)

def group_tags(segment):
    tagsGAaux= re.findall(r'((</?[^>]+?/?>\s?){2,})', segment)
    tagsG=[]
    for t in tagsGAaux:
        tagsG.append(t[0])
    tagsGBaux= re.findall(r'((\{[0-9]+\}\s?){2,})', segment)
    for t in tagsGBaux:
        tagsG.append(t[0])
    
    conttag=0
    equil={}
    for t in tagsG:
        trep="<tagG"+str(conttag)+">"
        segment=segment.replace(t,trep)
        equil[trep]=t
        conttag+=1
    
    
    return(segment,equil)

def replace_tags(segment):
    equil={}
    if has_tags(segment):
        tagsA = re.findall(r'</?.+?/?>', segment)
        tagsB = re.findall(r'\{[0-9]+\}', segment)
        tags=tagsA.copy()
        tags.extend(tagsB)
        conttag=0
        for tag in tags:
            tagrep="<tag"+str(conttag)+">"
            segment=segment.replace(tag,tagrep,1)
            equil[tagrep]=tag
            if tag in tagsA:
                tagclose="</"+get_name(tag)+">"
                tagcloserep="</tag"+str(conttag)+">"
                if segment.find(tagclose)>-1:
                    segment=segment.replace(tagclose,tagcloserep)
                    equil[tagcloserep]=tagclose
                    tags.remove(tagclose)
            conttag+=1
            
        return(segment,equil)
        
    else:
        return(segment,equil)
        
def remove_start_end_tag(segment):
    try:
        starttag=re.match("</?tag[0-9]+>",segment)
        starttag=starttag.group()
    except:
        starttag=None
    try:
        endtag=re.search("</?tag[0-9]+>$",segment)
        endtag=endtag.group()
    except:
        endtag=None
    if starttag:
        segment=lreplace(starttag,"",segment)
    if endtag:
        segment=rreplace(endtag,"",segment)
    return(segment,starttag,endtag)
###


def translate(segment):
    #function for Moses server
    print("Translating: ",segment['text'])
    translation=translate_segment(segment['text'])
    print("Translation: ",translation)
    translationdict={}
    translationdict["text"]=translation
    return(translationdict)

def translate_segment(segment):
    try:
        if unescape_html:
            segment=html.unescape(segment)
        if MTUOCServer_verbose: print(str(datetime.now())+"\t"+"SL segment: "+"\t"+segment)
        #leading and trailing spaces
        leading_spaces=len(segment)-len(segment.lstrip())
        trailing_spaces=len(segment)-len(segment.rstrip())-1
        segment=segment.lstrip().rstrip()
        ###Pretractament dels tags
        (segmentTAGS,equilG)=group_tags(segment)
        print(segmentTAGS)
        print("EQUILG",equilG)
        (segmentTAGS,equil)=replace_tags(segmentTAGS)
        print(segmentTAGS)
        print("EQUILG",equil)
        
        tagInici=""
        tagFinal=""
        (segmentTAGS,tagInici,tagFinal)=remove_start_end_tag(segmentTAGS)
        
        segmentNOTAGS=remove_tags(segment)
        if MTUOCServer_EMAILs:
            segmentNOTAGS=replace_EMAILs(segmentNOTAGS)
        if MTUOCServer_URLs:
            segmentNOTAGS=replace_URLs(segmentNOTAGS)
        if MTUOCServer_verbose and not segmentNOTAGS==segment: print(str(datetime.now())+"\t"+"SL segment NO TAGS: "+"\t"+segmentNOTAGS)
        segmentPRENOTAGS=to_MT_SP(segmentNOTAGS,tokenizer,ltcmodel,spmodel,vocab)
        if MTUOCServer_verbose: print(str(datetime.now())+"\t"+"SL segment PRE NO TAGS: "+"\t"+segmentPRENOTAGS)
        segmentPRETAGS=to_MT_SP(segmentTAGS,tokenizer,ltcmodel,spmodel,vocab)
        if MTUOCServer_verbose and not segmentPRENOTAGS==segmentPRETAGS: print(str(datetime.now())+"\t"+"SL segment PRE TAGS: "+"\t"+segmentPRETAGS)
        hastags=has_tags(segment)
        if MTUOCServer_MTengine=="Marian":
                (selectedtranslationPre, selectedalignment)=translate_segment_Marian(segmentPRENOTAGS)
        if MTUOCServer_verbose: print(str(datetime.now())+"\t"+"translation PRE: "+"\t"+selectedtranslationPre)
        if MTUOCServer_verbose: print(str(datetime.now())+"\t"+"alignment: "+"\t"+selectedalignment)
        #restoring tags
        if MTUOCServer_restore_tags and hastags:
            selectedtranslationTags=restore_tags(segmentPRENOTAGS, segmentPRETAGS, selectedalignment, selectedtranslationPre, spechar="▁")
            if MTUOCServer_verbose: print(str(datetime.now())+"\t"+"translation PRE TAGS: "+"\t"+selectedtranslationTags)
        else:
            selectedtranslationTags=selectedtranslationPre
            if MTUOCServer_verbose: print(str(datetime.now())+"\t"+"translation PRE: "+"\t"+selectedtranslationTags)
        
        

        
        
        #Leading and trailing tags
        selectedtranslationTags=from_MT_SP(selectedtranslationTags,detokenizer)
        if MTUOCServer_verbose: print(str(datetime.now())+"\t"+"translation: "+"\t"+selectedtranslationTags)
        if tagInici:
            selectedtranslationTags=tagInici+selectedtranslationTags
        if tagFinal:
            selectedtranslationTags=selectedtranslationTags+tagFinal
        #Restoring real tags
        for t in equil:
            print("***",t,equil[t])
            selectedtranslationTags=selectedtranslationTags.replace(t,equil[t])
        print("***",selectedtranslationTags)
        for t in equilG:
            print("***",t,equilG[t])
            selectedtranslationTags=selectedtranslationTags.replace(t,equilG[t])
        print("***",selectedtranslationTags)
        #restoring/removing spaces before and after tags
        if MTUOCServer_restore_tags and hastags:
            selectedtranslationTags=repairSpacesTags(segment,selectedtranslationTags)
            if MTUOCServer_verbose: print(str(datetime.now())+"\t"+"translation restored spaces: "+"\t"+selectedtranslationTags)
        #restoring leading and trailing spaces
        lSP=leading_spaces*" "
        tSP=trailing_spaces*" "
        selectedtranslation=lSP+selectedtranslationTags+tSP
        #restoring case
        if segment==segment.upper():
            selectedtranslation=selectedtranslation.upper()
        else:
            selectedtranslation=restoreCase(segment, segmentPRENOTAGS, selectedalignment, selectedtranslationPre, selectedtranslation,tokenizer,detokenizer)
        
        if MTUOCServer_EMAILs:
            selectedtranslation=restore_EMAILs(segment,selectedtranslation)
        if MTUOCServer_URLs:
            selectedtranslation=restore_URLs(segment,selectedtranslation)
        
        if MTUOCServer_verbose: print(str(datetime.now())+"\t"+"translation restored case: "+"\t"+selectedtranslationTags)
                
    except:
        print("ERROR:",sys.exc_info())
        
    if add_trailing_space:
        selectedtranslation=selectedtranslation+" "
    
    return(selectedtranslation)

def translate_segment_Marian(segmentPre):
    lseg=len(segmentPre)
    ws.send(segmentPre)
    translations = ws.recv()
    cont=0
    firsttranslationPre=""
    selectedtranslation=""
    selectedalignment=""
    candidates=translations.split("\n")
    translation=""
    alignments=""
    for candidate in candidates:
        camps=candidate.split(" ||| ")
        if len(camps)>2:
            translation=camps[1]
            alignments=camps[2]
            if cont==0:
                if not len(translation.strip())==0:
                    selectedtranslationPre=translation
                    selectedalignment=alignments
                else:
                    cont-=1
            ltran=len(translation)
            if ltran>=lseg*min_len_factor:
                selectedtranslationPre=translation
                selectedalignment=alignments
                break
            cont+=1
    
    return(selectedtranslationPre, selectedalignment)

def translate_segment_OpenNMT(segmentPre):
    params = [{ "src" : segmentPre}]

    response = requests.post(url, json=params, headers=headers)
    target = response.json()
    selectedtranslationPre=target[0][0]["tgt"]
    if "align" in target[0][0]:
        selectedalignment=target[0][0]["align"][0]
    else:
        selectedalignments=""
    
    
    return(selectedtranslationPre, selectedalignment)
    

###RESTORE CASE
def restoreCase(segment, segmentPRENOTAGS, selectedalignment, selectedtranslationPre, selectedtranslation,sltokenizer,tltokenizer):
    relations={}
    for t in selectedalignment.split(" "):
        camps=t.split("-")
        if not int(camps[0]) in relations:
            relations[int(camps[0])]=[]
        relations[int(camps[0])].append(int(camps[1]))
        slList=segmentPRENOTAGS.split(" ")
        tlList=selectedtranslationPre.split(" ")
        relationToks={}
        for i in range(0,len(slList)):
            try:
                sltok=slList[i].replace("▁"," ").strip()
                tltoks=[]
                for r in relations[i]:
                    tltoks.append(tlList[r])
                relationToks[sltok]="".join(tltoks).replace("▁"," ").strip()
                
                
            except:
                pass
                
    sltokens=sltokenizer.tokenize(segment)
    resultat=selectedtranslation
    for sltok in sltokens.split(" "):
        if sltok==sltok.upper() and not sltok==sltok.lower():
            if sltok.lower() in relationToks:
                tltok=relationToks[sltok.lower()]
                resultat=resultat.replace(tltok,tltok.upper(),1)
    return(resultat)

if len(sys.argv)==1:
    configfile="config-server.yaml"
else:
    configfile=sys.argv[1]

stream = open(configfile, 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)

MTUOCServer_MTengine=config["MTEngine"]["MTengine"]
startMTEngine=config["MTEngine"]["startMTEngine"]
startMTEngineCommand=config["MTEngine"]["startCommand"]
MTEngineIP=config["MTEngine"]["IP"]
MTEnginePort=config["MTEngine"]["port"]
min_len_factor=config["MTEngine"]["min_len_factor"]

if startMTEngine:
    x = threading.Thread(target=startMTEngineThread, args=(startMTEngineCommand,))
    x.start()

MTUOCServer_port=config["MTUOCServer"]["port"]
MTUOCServer_type=config["MTUOCServer"]["type"]
MTUOCServer_verbose=config["MTUOCServer"]["verbose"]
MTUOCServer_restore_tags=config["MTUOCServer"]["restore_tags"]
MTUOCServer_restore_case=config["MTUOCServer"]["restore_case"]
MTUOCServer_URLs=config["MTUOCServer"]["URLs"]
MTUOCServer_EMAILs=config["MTUOCServer"]["EMAILs"]
add_trailing_space=config["MTUOCServer"]["add_trailing_space"]
unescape_html=config["MTUOCServer"]["EMAILs"]
MTUOCServer_ONMT_url_root=config["MTUOCServer"]["ONMT_url_root"]

sllang=config["Preprocess"]["sl_lang"]
tllang=config["Preprocess"]["tl_lang"]
MTUOCtokenizer=config["Preprocess"]["sl_tokenizer"]
MTUOCdetokenizer=config["Preprocess"]["tl_tokenizer"]
spmodel=config["Preprocess"]["sp_model_SL"]
spvocab=config["Preprocess"]["sp_vocabulary_SL"]
spvocabulary_threshold=config["Preprocess"]["sp_vocabulary_threshold"]
tcmodel=config["Preprocess"]["tcmodel"]
bos_annotate=config["Preprocess"]["bos_annotate"]
eos_annotate=config["Preprocess"]["eos_annotate"]
sp_joiner=config["Preprocess"]["sp_joiner"]


if not MTUOCServer_MTengine=="ModernMT":
    spec = importlib.util.spec_from_file_location('', MTUOCtokenizer)
    tokenizer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tokenizer)
    
    spec = importlib.util.spec_from_file_location('', MTUOCdetokenizer)
    detokenizer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(detokenizer)
    
    #loading truecasing model
    if not tcmodel==None:
        ltcmodel=load_tc_model(tcmodel)

    #vocabulary restriction
    if not spvocabulary_threshold==None:
        vocab=[]
        entrada=codecs.open(spvocab,"r",encoding="utf-8")
        for linia in entrada:
            linia=linia.strip()
            camps=linia.split("\t")
            if float(camps[1])>=spvocabulary_threshold:
                vocab.append(camps[0])
        vocab=list(vocab)
    
    sp= spm.SentencePieceProcessor(model_file=spmodel, out_type=str, add_bos=bos_annotate, add_eos=eos_annotate)
    sp2= spm.SentencePieceProcessor(model_file=spmodel, out_type=str)
    
    if vocab and not spvocabulary_threshold==None:
        sp.set_vocabulary(vocab)
        sp2.set_vocabulary(vocab)
    
if MTUOCServer_MTengine=="Marian":
    from websocket import create_connection
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        conn=s.connect_ex((MTEngineIP, MTEnginePort))
        if conn == 0:marianstarted=True
    service="ws://"+MTEngineIP+":"+str(MTEnginePort)+"/translate"
    error=True
    while error:
        try:
            ws = create_connection(service)
            print("Connection with Marian Server created")
            error=False
        except:
            print("Error: waiting for Marian server to start. Retrying in 5 seconds.")
            time.sleep(5)
            error=True
            
elif MTUOCServer_MTengine=="OpenNMT":
    import requests
    url = "http://"+MTEngineIP+":"+str(MTEnginePort)+"/translator/translate"
    headers = {'content-type': 'application/json'}
    
    
#STARTING MTUOC SERVER

if MTUOCServer_type=="MTUOC":
    from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
    
    class MTUOC_server(WebSocket):
        def handleMessage(self):
            if MTUOCServer_verbose: print("--------------------")
            if MTUOCServer_verbose: print(str(datetime.now())+"\t"+"Start: "+"\t"+self.data)
            self.translation=translate_segment(self.data)
            self.sendMessage(self.translation)

        def handleConnected(self):
            if MTUOCServer_verbose:
                print(str(datetime.now())+"\t"+'Connected to: '+"\t"+self.address[0].split(":")[-1])
            else:
                pass

        def handleClose(self):
            if MTUOCServer_verbose:
                print(str(datetime.now())+"\t"+'Disconnected from:'+"\t"+self.address[0].split(":")[-1])
            else:
                pass
    server = SimpleWebSocketServer('', MTUOCServer_port, MTUOC_server)
    ip=get_IP_info()
    print("MTUOC server IP:",ip," port:",MTUOCServer_port)
    server.serveforever()

elif MTUOCServer_type=="OpenNMT":
    from flask import Flask, jsonify, request
    MTUOCServer_ONMT_url_root=config["MTUOCServer"]["ONMT_url_root"]
    STATUS_OK = "ok"
    STATUS_ERROR = "error"
    out={}
    def start(url_root="./translator",
              host="0.0.0.0",
              port=5000,
              debug=True):
        def prefix_route(route_function, prefix='', mask='{0}{1}'):
            def newroute(route, *args, **kwargs):
                return route_function(mask.format(prefix, route), *args, **kwargs)
            return newroute

        app = Flask(__name__)
        app.route = prefix_route(app.route, url_root)

        @app.route('/translate', methods=['POST'])
        def translateONMT():
            inputs = request.get_json(force=True)
            inputs0=inputs[0]
            out = {}
            try:
                out = [[]]
                ss=inputs0['src']
                ts=translate_segment(ss)
                response = {"src": ss, "tgt": ts,
                                "n_best": 0, "pred_score": 0}
                    
                out[0].append(response)
            except:
                out['error'] = "Error"
                out['status'] = STATUS_ERROR

            return jsonify(out)
            
        
        app.run(debug=debug, host=host, port=port, use_reloader=False,
            threaded=True)
    url_root=MTUOCServer_ONMT_url_root
    ip="0.0.0.0"
    ip=get_IP_info()
    debug="store_true"
    start(url_root=MTUOCServer_ONMT_url_root, host=ip, port=MTUOCServer_port,debug=debug)

elif MTUOCServer_type=="NMTWizard":
    from flask import Flask, jsonify, request
    STATUS_OK = "ok"
    STATUS_ERROR = "error"
    out={}
    def start(url_root="",
              host="0.0.0.0",
              port=5000,
              debug=True):
        def prefix_route(route_function, prefix='', mask='{0}{1}'):
            def newroute(route, *args, **kwargs):
                return route_function(mask.format(prefix, route), *args, **kwargs)
            return newroute

        app = Flask(__name__)
        app.route = prefix_route(app.route, url_root)

        @app.route('/translate', methods=['POST'])
        def translateONMT():
            inputs = request.get_json(force=True)
            sourcetext=inputs["src"][0]["text"]
            if MTUOCServer_verbose:print("Translating",sourcetext)
            try:
                targettext=translate_segment(sourcetext)
                out={"tgt": [[{"text": targettext}]]}
            except:
                out['error'] = "Error"
                out['status'] = STATUS_ERROR
            return jsonify(out)
        app.run(debug=debug, host=host, port=port, use_reloader=False,
                threaded=True)
    url_root=""
    ip="0.0.0.0"
    ip=get_IP_info()
    debug="store_true"
    start(url_root=url_root, host=ip, port=MTUOCServer_port,debug=debug)
    
elif MTUOCServer_type=="ModernMT":
    from flask import Flask, jsonify, request
    STATUS_OK = "ok"
    STATUS_ERROR = "error"
    def start(
              url_root="",
              host="",
              port=8000,
              debug=True):
        def prefix_route(route_function, prefix='', mask='{0}{1}'):
            def newroute(route, *args, **kwargs):
                return route_function(mask.format(prefix, route), *args, **kwargs)
            return newroute
        app = Flask(__name__)
        app.route = prefix_route(app.route, url_root)
        @app.route('/translate', methods=['GET'])
        def translateModernMT():
            out = {}
            try:
                out['data']={}
                segment=request.args['q']
                translation=translate_segment(segment)
                out['data']['translation']=translation
            except:
                out['status'] = STATUS_ERROR
            return jsonify(out)
        ip=get_IP_info()
        app.run(debug=True, host=ip, port=MTUOCServer_port, use_reloader=False,
                threaded=True)
    start()


elif MTUOCServer_type=="Moses":
    from xmlrpc.server import SimpleXMLRPCServer
    server = SimpleXMLRPCServer(
    ("", MTUOCServer_port),
    logRequests=True,)
    server.register_function(translate)
    server.register_introspection_functions()
    # Start the server
    try:
        ip=get_IP_info()
        print("Moses server IP:",ip," port:",MTUOCServer_port)
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
