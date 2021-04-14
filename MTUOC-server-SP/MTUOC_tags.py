#    MTUOC_tags
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

import re
import io
import lxml.etree as ET

class TagRestorer():
    def __init__(self):
        pass
        
    def lreplace(self, pattern, sub, string):
        """
        Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
        """
        return re.sub('^%s' % pattern, sub, string)

    def rreplace(self, pattern, sub, string):
        """
        Replaces 'pattern' in 'string' with 'sub' if 'pattern' ends 'string'.
        """
        return re.sub('%s$' % pattern, sub, string)    
        
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
                tagrep="<tag"+str(conttag)+">"
                segment=segment.replace(tag,tagrep,1)
                equil[tagrep]=tag
                if tag in tagsA:
                    tagclose="</"+self.get_name(tag)+">"
                    tagcloserep="</tag"+str(conttag)+">"
                    if segment.find(tagclose)>-1:
                        segment=segment.replace(tagclose,tagcloserep)
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
            starttag=None
        try:
            endtag=re.search("</?tag[0-9]+>$",segment)
            endtag=endtag.group()
        except:
            endtag=None
        if starttag:
            segment=self.lreplace(starttag,"",segment)
        if endtag:
            segment=self.rreplace(endtag,"",segment)
        return(segment,starttag,endtag)

    def restore_tags(self,SOURCENOTAGSTOKSP, SOURCETAGSTOKSP, SELECTEDALIGNMENT, TARGETNOTAGSTOKSP, spechar="▁", bos="<s>", eos="</s>"):
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
        LISTSOURCETAGSTOKSP=self.splitTags(SOURCETAGSTOKSP)
        LISTSOURCETAGSTOK=self.removeSpeChar(LISTSOURCETAGSTOKSP,spechar)
        LISTSOURCENOTAGSTOKSP=self.splitTags(SOURCENOTAGSTOKSP)
        LISTTARGETNOTAGSTOKSP=self.splitTags(TARGETNOTAGSTOKSP)
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
