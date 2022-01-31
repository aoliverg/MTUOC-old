#    MTUOC_tags
#    Copyright (C) 2022  Antoni Oliver
#    v. 14/01/2022
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

import re
import io
import lxml.etree as ET
import itertools
import sys
from collections import Counter

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
    
def deapply_BPE(segment, joiner="@@"):
    regex = r"(" + re.escape(joiner) + " )|("+ re.escape(joiner) +" ?$)"
    segment=re.sub(regex, '', segment)
    regex = r"( " + re.escape(joiner) + ")|(^ $"+ re.escape(joiner) +")"
    segment=re.sub(regex, '', segment)
    return(segment)

class TagRestorer():
    def __init__(self):
        self.sentencepiece=False
        
        
    #get_mappings and convert adapted from https://github.com/lilt/alignment-scripts/blob/master/scripts/sentencepiece_to_word_alignments.py
            
    def set_sentencepiece(self):
        self.sentencepiece=True
        
    def get_mappingSP(self,l,sp_splitter="▁", bos="<s>", eos="</s>"):
        subwordsaux = l.strip().split()
        subwords=[]
        #subwords = l.strip().split()  
        for sw in subwordsaux:
            if not sw.startswith(sp_splitter) and not sw.endswith(sp_splitter) and not sw==bos and not sw==eos:
                sw2=sp_splitter+str(sw)
                subwords.append(sw2)
            else:
                sw2=sw
                subwords.append(sw)
        return(list(itertools.accumulate([int(sp_splitter in x) for x in subwords])))

    def get_mappingBPE(self,l,bpe_joiner="@@", bos="<s>", eos="</s>"):
        subwordsaux = l.strip().split()
        subwords=[]
        #subwords = l.strip().split()  
        for sw in subwordsaux:
            if not sw.startswith(bpe_joiner) and not sw.endswith(bpe_joiner) and not sw==bos and not sw==eos:
                sw2=str(sw)+bpe_joiner
                subwords.append(sw2)
            else:
                sw2=sw
                subwords.append(sw)
        
        return(list(itertools.accumulate([int(bpe_joiner in x) for x in subwords])))

    def convertSP(self,srcSTR,tgtSTR,aliSTR,sp_splitter="▁", bos="<s>", eos="</s>"):
        src_map=self.get_mappingSP(srcSTR,sp_splitter)
        tgt_map=self.get_mappingSP(tgtSTR,sp_splitter)
        subword_alignments = {(int(a), int(b)) for a, b in (x.split("-") for x in aliSTR.split())}
        word_alignments=[]
        for a,b in subword_alignments:
            try:
                word_alignments.append(str(src_map[a])+"-"+str(tgt_map[b]))
            except:
                pass
        word_alignments=" ".join(word_alignments)
        ssW=srcSTR.replace(" ","").replace(sp_splitter," ")
        tsW=tgtSTR.replace(" ","").replace(sp_splitter," ")
        
        return(ssW,tsW,word_alignments)
        
    def convertBPE(self,srcSTR,tgtSTR,aliSTR,bpe_joiner="@@", bos="<s>", eos="</s>"):

        src_map=self.get_mappingBPE(srcSTR,bpe_joiner)
        tgt_map=self.get_mappingBPE(tgtSTR,bpe_joiner)
        subword_alignments = {(int(a), int(b)) for a, b in (x.split("-") for x in aliSTR.split())}
        word_alignments=[]
        for a,b in subword_alignments:
            try:
                word_alignments.append(str(src_map[a])+"-"+str(tgt_map[b]))
            except:
                pass
        word_alignments=" ".join(word_alignments)
        ssW=deapply_BPE(srcSTR,bpe_joiner)
        tsW=deapply_BPE(tgtSTR,bpe_joiner)
        return(ssW,tsW,aliSTR)
        
    def get_name(self, tag):
        name=tag.split(" ")[0].replace("<","").replace(">","").replace("/","")
        return(name)
        
    def has_tags(self, segment):
        response=False
        tagsA = re.findall(r'</?.+?/?>', segment)
        tagsB = re.findall(r'\{[0-9]+\}', segment)
        if len(tagsA)>0 or len(tagsB)>0:
            response=True
        return(response)
        
    def is_tag(self, token):
        response=False
        tagsA = re.match(r'</?.+?/?>', token)
        tagsB = re.match(r'\{[0-9]+\}', token)
        if tagsA or tagsB:
            response=True
        return(response)
        
    def remove_tags(self, segment):
        segmentnotags=re.sub('(<[^>]+>)', "",segment)
        segmentnotags=re.sub('({[0-9]+})', "",segmentnotags)
        segmentnotags=" ".join(segmentnotags.split())
        return(segmentnotags)
        
    def get_tags(self, segment):
        tagsA = re.findall(r'</?.+?/?>', segment)
        tagsB = re.findall(r'\{[0-9]+\}', segment)
        tags=tagsA.copy()
        tags.extend(tagsB)
        return(tags)
        
    def group_tags(self, segment):
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
            
    def replace_tags(self, segment):
        equil={}
        if self.has_tags(segment):
            tagsA = re.findall(r'</?.+?/?>', segment)
            tagsB = re.findall(r'\{[0-9]+\}', segment)
            tags=tagsA.copy()
            tags.extend(tagsB)
            conttag=0
            for tag in tags:
                if tag.find("</")>-1:
                    tagrep="</tag"+str(conttag)+">"
                else:
                    tagrep="<tag"+str(conttag)+">"
                segment=segment.replace(tag,tagrep,1)
                equil[tagrep]=tag
                if tag in tagsA:
                    tagclose="</"+self.get_name(tag)+">"
                    tagcloserep="</tag"+str(conttag)+">"
                    if segment.find(tagclose)>-1:
                        segment=segment.replace(tagclose,tagcloserep,1)
                        equil[tagcloserep]=tagclose
                        tags.remove(tagclose)
                conttag+=1
                
            return(segment,equil)
            
        else:
            return(segment,equil)
            
    def removeSpeChar(self, llista,spechar):
        for i in range(0,len(llista)):
            llista[i]=llista[i].replace(spechar,"")
        return(llista)

    def remove_start_end_tag(self, segment):
        try:
            starttag=re.match("</?tag[0-9]+>",segment)
            starttag=starttag.group()
        except:            
            starttag=""
        try:
            endtag=re.search("</?tag[0-9]+>$",segment)
            endtag=endtag.group()
        except:
            endtag=""
        if starttag:
            segment=lreplace(starttag,"",segment)
        if endtag:
            segment=rreplace(endtag,"",segment)
        return(segment,starttag,endtag)
    
    def isSTag(self,tok):
        if re.match("<tag[0-9]+>", tok):return(True)
        else: return(False)
    def isSClosingTag(self,tok):
        if re.match("<\/tag[0-9]+>", tok):return(True)
        else: return(False)
    def toClosingTag(self,tag):
        closingTag=tag.replace("<","</")
        return(closingTag)    
    
    def upper(self,segment):
        tags=self.get_tags(segment)
        segment=segment.upper()
        for tag in tags:
            segment=segment.replace(tag.upper(),tag)
        return(segment)
    
    def upperFirst(self,segment):
        #UPPERCASES the first letter after tags and symbols
        symbols=["(","[","¿","¡","'",'"',"«","‹","„","“","‟","❝","❮","⹂","〝","〟","＂","‚","‚","‘","❛","-","—","{"]
        inTag=False
        pos=0
        segmentL=list(segment)
        for car in segmentL:
            if car=="<":
                inTag=True
            elif car==">":
                inTag=False
            elif not car in symbols and not inTag and car.isalpha():
                segmentL[pos]=segmentL[pos].upper()
                break
            pos+=1
        segment="".join(segmentL)
        return(segment)
        
    def isFirstUpperCase(self,segment):
        #UPPERCASES the first letter after tags and symbols
        symbols=["(","[","¿","¡","'",'"',"«","‹","„","“","‟","❝","❮","⹂","〝","〟","＂","‚","‚","‘","❛","-","—","{"]
        isUC=False
        inTag=False
        pos=0
        segmentL=list(segment)
        for car in segmentL:
            if car=="<":
                inTag=True
            elif car==">":
                inTag=False
            elif not car in symbols and not inTag and car.isupper():
                isUC=True
                break
            pos+=1
        return(isUC)

    def restore_tags(self,SOURCENOTAGSTOK, SOURCETAGSTOK, SELECTEDALIGNMENT, TARGETNOTAGSTOK, bos="<s>", eos="</s>"):
        #if not bos=="": bos=bos+" "
        #if not eos=="": eos=" "+eos
        #SOURCETAGSTOK=bos+SOURCETAGSTOK+eos
        TARGETTAGLIST=TARGETNOTAGSTOK.split(" ")
        ali={}
        for a in SELECTEDALIGNMENT.split():
            (a1,a2)=a.split("-")
            a1=int(a1)
            a2=int(a2)
            ali[a1]=a2
        position=0
        tagpos={}
        posacu=0
        SOURCETAGSTOKLIST=SOURCETAGSTOK.split()
        SOURCENOTAGSTOKLIST=SOURCENOTAGSTOK.split()
        position=0
        
        for i in range(0, len(SOURCETAGSTOKLIST)+1):
            try:
                stok=SOURCETAGSTOKLIST[i]
                if self.isSTag(stok) or self.isSClosingTag(stok):
                    
                    if self.isSTag(stok):
                        tagpos[stok]=position
                    elif self.isSClosingTag(stok):
                        tagpos[stok]=position-1
                            
                    
                else:
                    position+=1
            except:
                pass
        posacu=0
        alreadydone=[]
        for tag in tagpos:
            try:
                if not tag in alreadydone:
                    if self.isSTag(tag):
                        closingTag=self.toClosingTag(tag)
                        if closingTag in tagpos:
                            posOpening=tagpos[tag]
                            posClosing=tagpos[closingTag]
                            posmax=0
                            posmin=1000000
                            for i in range(posOpening,posClosing+1):
                                if ali[i]>posmax:posmax=ali[i]
                                if ali[i]<posmin:posmin=ali[i]
                            newtok=tag+" "+TARGETTAGLIST[posmin]
                            TARGETTAGLIST[posmin]=newtok
                            newtok=TARGETTAGLIST[posmax]+" "+closingTag
                            TARGETTAGLIST[posmax]=newtok
                            alreadydone.append(tag)
                            alreadydone.append(closingTag)
                    if not tag in alreadydone:        
                        pos=tagpos[tag]
                        if self.isSTag(tag):
                            newtok=tag+" "+TARGETTAGLIST[ali[pos]]
                            TARGETTAGLIST[ali[pos]]=newtok
                        elif self.isSClosingTag(tag):
                            newtok=TARGETTAGLIST[ali[pos]]+" "+tag
                            TARGETTAGLIST[ali[pos]]=newtok
                        posacu+=1
            except:
                pass
        targettags=" ".join(TARGETTAGLIST)
        targettags=targettags.replace(" .",".").replace(" ;",";").replace(" ,",",").replace(" :",":")
        return(targettags)
        
    def splitTags(self, segment):
        tags=re.findall('(<[^>]+>)', segment)
        for tag in tags:
            tagmod=tag.replace(" ","_")
            segment=segment.replace(tag,tagmod)
        slist=segment.split(" ")
        for i in range(0,len(slist)):
            slist[i]=slist[i].replace("_"," ")
        return(slist)

    def repairSpacesTags(self,slsegment,tlsegment,delimiters=[" ",".",",",":",";","?","!"]):
        sltags=self.get_tags(slsegment)
        tltags=self.get_tags(tlsegment)
        commontags= list((Counter(sltags) & Counter(tltags)).elements())
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
                pass
        return(tlsegment)

    def restoreCase(self, segment, segmentPRENOTAGS, selectedalignment, selectedtranslationPre, selectedtranslation,sltokenizer,tltokenizer):
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
                    sltok=slList[i].strip()
                    tltoks=[]
                    for r in relations[i]:
                        tltoks.append(tlList[r])
                    relationToks[sltok]="".join(tltoks).strip()
                    
                    
                except:
                    pass
        if not sltokenizer==None:            
            sltokens=sltokenizer.tokenize(segment)
        else:
            sltokens=segment
        resultat=selectedtranslation
        for sltok in sltokens.split(" "):
            if sltok==sltok.upper() and not sltok==sltok.lower():
                if sltok.lower() in relationToks:
                    tltok=relationToks[sltok.lower()]
                    resultat=resultat.replace(tltok,tltok.upper(),1)
        return(resultat)
