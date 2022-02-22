#    MTUOC-server v 5
#    Description: an MTUOC server using Sentence Piece as preprocessing step
#    Copyright (C) 2022  Antoni Oliver
#    v. 05/01/2022
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
import sys
import threading
import os
import socket
import time
import re
from datetime import datetime
import importlib
import importlib.util
import codecs
import xmlrpc.client
import json
import pickle
import sentencepiece as spm
from subword_nmt import apply_bpe
import collections

import lxml

import html

import csv

###YAML IMPORTS
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    
from getWordAlignments import *
from WACalculatorEflomal import WACalculatorEflomal


def printLOG(vlevel,m1,m2=""):
    cadena=str(m1)+"\t"+str(m2)+"\t"+str(datetime.now())
    if vlevel<=verbosity_level:
        print(cadena)
        if log_file:
            sortidalog.write(cadena+"\n")

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

###BPE subword-nmt
def processBPE(bpeobject,segment):
    segmentBPE=bpeobject.process_line(segment)
    return(segmentBPE)
    
def deprocessBPE(segment, joiner="@@"):
    regex = r"(" + re.escape(joiner) + " )|("+ re.escape(joiner) +" ?$)"
    segment=re.sub(regex, '', segment)
    regex = r"( " + re.escape(joiner) + ")|(^ $"+ re.escape(joiner) +")"
    segment=re.sub(regex, '', segment)
    return(segment)

###URLs EMAILs

def findEMAILs(string): 
    email=re.findall('\S+@\S+', string)
    email2=[]
    for em in email: 
        if em[-1] in stringmodule.punctuation: em=em[0:-1]
        email2.append(em)
    return email2
    
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

    printLOG(2,"Selected translation from Marian:",selectedtranslationPre)
    printLOG(2,"Selected alignment from Marian:",selectedalignment)
    return(selectedtranslationPre, selectedalignment)
    
def translate_segment_OpenNMT(segmentPre):
    params = [{ "src" : segmentPre}]

    response = requests.post(url, json=params, headers=headers)
    target = response.json()
    selectedtranslationPre=target[0][0]["tgt"]
    if "align" in target[0][0]:
        selectedalignments=target[0][0]["align"][0]
    else:
        selectedalignments=""
    return(selectedtranslationPre, selectedalignments)

def translateAliMoses(aliBRUT):
    newali=[]
    for a in aliBRUT:
        at=str(a['source-word'])+"-"+str(a['target-word'])
        newali.append(at)
    newali=" ".join(newali)

    return(newali)

def translate_segment_Moses(segmentPre):
    param = {"text": segmentPre}
    result = proxyMoses.translate(param)
    translationREP=result['text']
    alignmentBRUT=result['word-align']
    alignments=translateAliMoses(alignmentBRUT)
    return(translationREP, alignments)  
    

def translate_segment(segment):
    try:
        printLOG(1,"segment:",segment)
        #leading and trailing spaces
        leading_spaces=len(segment)-len(segment.lstrip())
        trailing_spaces=len(segment)-len(segment.rstrip())-1
        segment=segment.lstrip().rstrip()
        ###Pretractament dels tags
        (segmentTAGS,equilG)=tagrestorer.group_tags(segment)
        (segmentTAGS,equil)=tagrestorer.replace_tags(segmentTAGS)
        if not bos_annotate=="": segmentTAGS=bos_annotate+" "+segmentTAGS
        if not eos_annotate=="": segmentTAGS=segmentTAGS+" "+eos_annotate
        segmentTAGSrepair=segmentTAGS
        (segmentTAGS,tagInici,tagFinal)=tagrestorer.remove_start_end_tag(segmentTAGS)
        if not tagInici=="": printLOG(3,"Starting tag:",tagInici)
        if not tagFinal=="": printLOG(3,"Ending tag:",tagFinal)
        segmentNOTAGS=tagrestorer.remove_tags(segment)
        if MTUOCServer_EMAILs:
            segmentNOTAGS=replace_EMAILs(segmentNOTAGS)
        if MTUOCServer_URLs:
            segmentNOTAGS=replace_URLs(segmentNOTAGS)
        if not truecaser==None:        
            segmentNOTAGS=truecaser.truecase(segmentNOTAGS)
        if not tokenizerSL==None:
            segmentNOTAGS=tokenizerSL.tokenize(segmentNOTAGS)
        printLOG(3,"Segment TC NO TAGS",segmentNOTAGS)
        
        ###sentencepiece###
        if sentencepiece:
            output=sp.encode(segmentNOTAGS)
            segmentPRENOTAGS=" ".join(output)
        elif BPE:
            segmentPRENOTAGS=processBPE(bpeobject,segmentNOTAGS)
        else:
            segmentPRENOTAGS=segmentNOTAGS
        
        
        printLOG(2,"Segment PRE NO TAGS",segmentPRENOTAGS)
        hastags=tagrestorer.has_tags(segment)
        printLOG(2,"HAS TAGS",hastags)
        if MTUOCServer_MTengine=="Marian":
            (selectedtranslationPre, selectedalignment)=translate_segment_Marian(segmentPRENOTAGS)
        elif MTUOCServer_MTengine=="OpenNMT":
            (selectedtranslationPre, selectedalignment)=translate_segment_OpenNMT(segmentPRENOTAGS)
        elif MTUOCServer_MTengine=="Moses":
            (selectedtranslationPre, selectedalignment)=translate_segment_Moses(segmentPRENOTAGS)
        
        if MTUOCServer_restore_strategy=="mtengine":
            if sentencepiece:
                (segmentWords,selectedtranslationWords,wordali)=tagrestorer.convertSP(segmentPRENOTAGS,selectedtranslationPre,selectedalignment,sp_splitter=sp_splitter, eos=eos_annotate, bos=bos_annotate)  
            elif BPE:
                (segmentWords,selectedtranslationWords,wordali)=tagrestorer.convertBPE(segmentPRENOTAGS,selectedtranslationPre,selectedalignment,bpe_joiner=bpe_joiner)              
            else:
                segmentWords=segmentPRENOTAGS
                selectedtranslationWords=selectedtranslationPre
                wordali=selectedalignment
        else:
            segmentWords=segmentPRENOTAGS
            selectedtranslationWords=selectedtranslationPre
            wordali=selectedalignment
            if sentencepiece:
                segmentWords=segmentPRENOTAGS.replace(" ","").replace(sp_splitter," ")
                selectedtranslationWords=selectedtranslationPre.replace(" ","").replace(sp_splitter," ")
            elif BPE:                
                selectedtranslationWords=deprocessBPE(selectedtranslationPre,bpe_joiner)
        if not tokenizerSL==None:
            segmentWordsTok=tokenizerSL.tokenize(segmentWords)
            segmentTAGSTok=tokenizerSL.tokenize(segmentTAGS)
        else:
            segmentWordsTok=segmentWords
            segmentTAGSTok=segmentTAGS        
        if not tokenizerTL==None:
            selectedtranslationWordsTok=tokenizerTL.tokenize(selectedtranslationWords)
        else:
            selectedtranslationWordsTok=selectedtranslationWords
        if hastags and MTUOCServer_restore_strategy=="eflomal":
            wordali=WAC.getWordAlignments(segmentWordsTok,selectedtranslationWordsTok)
        if hastags and MTUOCServer_restore_tags and MTUOCServer_restore_strategy=="mtengine":
            selectedtranslationTags=tagrestorer.restore_tags(segmentWordsTok, segmentTAGSTok, wordali, selectedtranslationWordsTok, bos=bos_annotate, eos=eos_annotate)
        elif MTUOCServer_restore_tags and hastags and MTUOCServer_restore_strategy=="eflomal":
            selectedtranslationTags=tagrestorer.restore_tags(segmentWordsTok, segmentTAGSTok, wordali, selectedtranslationWordsTok, bos=bos_annotate, eos=eos_annotate)
        else:
            selectedtranslationTags=selectedtranslationWords
        
        if not bos_annotate=="" and selectedtranslationTags.startswith(bos_annotate+" "):selectedtranslationTags=selectedtranslationTags.replace(bos_annotate+" ","").strip()
        if not eos_annotate=="" and selectedtranslationTags.endswith(" "+eos_annotate):selectedtranslationTags=selectedtranslationTags.replace(" "+eos_annotate,"").strip()
        printLOG(1,"SELECTED TRANSLATION SIMPLE TAGS",selectedtranslationTags)
        if hastags:
            #Leading and trailing tags
            if tagInici:
                selectedtranslationTags=tagInici+selectedtranslationTags
            if tagFinal:
                selectedtranslationTags=selectedtranslationTags+tagFinal
            printLOG(2,"SELECTED TRANSLATION SIMPLE TAGS",selectedtranslationTags)
            
            if MTUOCServer_restore_tags:
                selectedtranslationTags=tagrestorer.repairSpacesTags(segmentTAGSrepair,selectedtranslationTags)
            #Restoring real tags
            for t in equil:
                selectedtranslationTags=selectedtranslationTags.replace(t,equil[t],1)
            for t in equilG:
                selectedtranslationTags=selectedtranslationTags.replace(t,equilG[t],1)
            printLOG(2,"Translation Restored Real Tags:",selectedtranslationTags)
            
            ####TAG VERIFICATION
            if strictTagRestoration:
                passTags=False
                tagsSource=tagrestorer.get_tags(segment)
                tagsTarget=tagrestorer.get_tags(selectedtranslationTags)
                printLOG(3,"TAG VERIFICATION, TAGS SOURCE:",tagsSource)
                printLOG(3,"TAG VERIFICATION, TAGS TARGET:",tagsTarget)            
                if collections.Counter(tagsSource) == collections.Counter(tagsTarget): passTags=True
                printLOG(2,"CORRECT TAG RESTORATION:",passTags)
                if not passTags:
                    selectedtranslationTags=selectedtranslationWords
                    
            #restoring leading and trailing spaces
        lSP=leading_spaces*" "
        tSP=trailing_spaces*" "
        selectedtranslation=lSP+selectedtranslationTags+tSP
        printLOG(2,"Translation Restored Real Tags and spaces:",selectedtranslation)
        #restoring case
        if MTUOCServer_restore_case:
            if tagrestorer.remove_tags(segment).isupper():
                selectedtranslation=tagrestorer.upper(selectedtranslation)
            elif tagrestorer.remove_tags(segment)[0].isupper():
                selectedtranslation=tagrestorer.upperFirst(selectedtranslation)
            if not selectedalignment=="":
                selectedtranslation=tagrestorer.restoreCase(segment, segmentWordsTok, wordali, selectedtranslationWordsTok, selectedtranslation,tokenizerSL,tokenizerTL)
            
        if MTUOCServer_EMAILs:
            selectedtranslation=restore_EMAILs(segment,selectedtranslation)
        if MTUOCServer_URLs:
            selectedtranslation=restore_URLs(segment,selectedtranslation)
        if finaldetokenization and not tokenizerTL==None:
            selectedtranslation=tokenizerTL.detokenize(selectedtranslation)
        printLOG(1,"FINAL TRANSLATION:",selectedtranslation)
        #verifying changes
        if not change_files[0]=="None":
            for change in changes:
                try:
                    source=change[0]
                    desired_target=change[1]
                    camps2=change[2].split("|")
                    for translated_target in camps2:
                        if segment.find(source)>-1 and selectedtranslation.find(translated_target)>-1:
                            #selectedtranslation=selectedtranslation.replace(translated_target,desired_target)
                            regexp="\\b"+translated_target+"\\b"
                            selectedtranslation=re.sub(regexp, desired_target, selectedtranslation)
                except:
                    print("ERROR:",sys.exc_info())
    except:
        printLOG(1,"ERROR:",sys.exc_info())
        return(segment)

    return(selectedtranslation)    

#YAML

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
    print("Starting MT engine...")
    x = threading.Thread(target=startMTEngineThread, args=(startMTEngineCommand,))
    x.start()
    
MTUOCServer_port=config["MTUOCServer"]["port"]
MTUOCServer_type=config["MTUOCServer"]["type"]
verbosity_level=int(config["MTUOCServer"]["verbosity_level"])
log_file=config["MTUOCServer"]["log_file"]
if log_file:
    sortidalog=codecs.open(log_file,"a",encoding="utf-8")
MTUOCServer_restore_tags=config["MTUOCServer"]["restore_tags"]
MTUOCServer_restore_strategy=config["MTUOCServer"]["restore_strategy"]
alimodel=config["MTUOCServer"]["alimodel"]
if alimodel=="None": alimodel=None
if not alimodel==None:
    WAC=WACalculatorEflomal()
    WAC.load_model(alimodel)
strictTagRestoration=config["MTUOCServer"]["strictTagRestoration"]
MTUOCServer_restore_case=config["MTUOCServer"]["restore_case"]

MTUOCServer_URLs=config["MTUOCServer"]["URLs"]
MTUOCServer_EMAILs=config["MTUOCServer"]["EMAILs"]
add_trailing_space=config["MTUOCServer"]["add_trailing_space"]
unescape_html=config["MTUOCServer"]["EMAILs"]
MTUOCServer_ONMT_url_root=config["MTUOCServer"]["ONMT_url_root"]

sllang=config["Preprocess"]["sl_lang"]
tllang=config["Preprocess"]["tl_lang"]
MTUOCtokenizerSL=config["Preprocess"]["sl_tokenizer"]
MTUOCtokenizerTL=config["Preprocess"]["tl_tokenizer"]
tcmodel=config["Preprocess"]["tcmodel"]

#sentencepiece
sentencepiece=config["Preprocess"]["sentencepiece"]
spmodel=config["Preprocess"]["sp_model_SL"]
spvocab=config["Preprocess"]["sp_vocabulary_SL"]
sp_splitter=config["Preprocess"]["sp_splitter"]

#BPE subword-nmt
BPE=config["Preprocess"]["BPE"]
bpecodes=config["Preprocess"]["bpecodes"]
bpe_joiner=config["Preprocess"]["bpe_joiner"]

#bos and eos annotate
bos_annotate=config["Preprocess"]["bos_annotate"]
if bos_annotate=="None": bos_annotate=""
eos_annotate=config["Preprocess"]["eos_annotate"]
if eos_annotate=="None": eos_annotate=""

finaldetokenization=config["Preprocess"]["finaldetokenization"]

#Lucy server specific options
TRANSLATION_DIRECTION=config["Lucy"]["TRANSLATION_DIRECTION"]
USER=config["Lucy"]["USER"]
if MTUOCtokenizerSL=="None": MTUOCtokenizerSL=None
if MTUOCtokenizerTL=="None": MTUOCtokenizerTL=None
if tcmodel=="None": tcmodel=None
if tcmodel:
    from MTUOC_truecaser import Truecaser
    truecaser=Truecaser(tokenizer=MTUOCtokenizerSL,tc_model=tcmodel)
else:
    truecaser=None
change_files=config["change_list"].split(";")

changes=[]
if not change_files[0]=="None":
    for change_list in change_files:
        with open(change_list) as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for row in csvreader:
                changes.append(row)
        

    

if not MTUOCServer_MTengine=="ModernMT":

    if MTUOCtokenizerSL:
        if not MTUOCtokenizerSL.endswith(".py"): MTUOCtokenizerSL=MTUOCtokenizerSL+".py"
        spec = importlib.util.spec_from_file_location('', MTUOCtokenizerSL)
        tokenizerSLmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tokenizerSLmod)
        tokenizerSL=tokenizerSLmod.Tokenizer()
    else:
        tokenizerSL=None
    
    if MTUOCtokenizerSL:
        if not MTUOCtokenizerTL.endswith(".py"): MTUOCtokenizerTL=MTUOCtokenizerTL+".py"
        spec = importlib.util.spec_from_file_location('', MTUOCtokenizerTL)
        tokenizerTLmod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tokenizerTLmod)
        tokenizerTL=tokenizerTLmod.Tokenizer()
    else:
        tokenizerTL=None
        
    from MTUOC_tags import TagRestorer
    tagrestorer=TagRestorer()
    
   
    ###sentencepiece
    if sentencepiece:
        
        
        sp= spm.SentencePieceProcessor(model_file=spmodel, out_type=str, add_bos=bos_annotate, add_eos=eos_annotate)
        sp2= spm.SentencePieceProcessor(model_file=spmodel, out_type=str)

    elif BPE:
        bpeobject=apply_bpe.BPE(open(bpecodes,encoding="utf-8"),separator=bpe_joiner)
        

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
            printLOG(0,"Connection with Marian Server created","")
            error=False
        except:
            printLOG(0,"Error: waiting for Marian server to start. Retrying in 5 seconds.","")
            time.sleep(5)
            error=True
            
           
elif MTUOCServer_MTengine=="OpenNMT":
    import requests
    url = "http://"+MTEngineIP+":"+str(MTEnginePort)+"/translator/translate"
    headers = {'content-type': 'application/json'}

    
elif MTUOCServer_MTengine=="Moses":
    proxyMoses = xmlrpc.client.ServerProxy("http://"+MTEngineIP+":"+str(MTEnginePort)+"/RPC2")

if MTUOCServer_type=="MTUOC":
    from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
    class MTUOC_server(WebSocket):
        def handleMessage(self):
            self.translation=translate_segment(self.data)
            self.sendMessage(self.translation)

        def handleConnected(self):
            printLOG(0,'Connected to: ',self.address[0].split(":")[-1])

        def handleClose(self):
            printLOG(0,'Disconnected from: ',self.address[0].split(":")[-1])
    server = SimpleWebSocketServer('', MTUOCServer_port, MTUOC_server)
    ip=get_IP_info()
    print("MTUOC server IP:",ip," port:",MTUOCServer_port)
    server.serveforever()

elif MTUOCServer_type=="OpenNMT":
    from flask import Flask, jsonify, request
    MTUOCServer_ONMT_url_root=config["MTUOCServer"]["ONMT_url_root"]
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    STATUS_OK = "ok"
    STATUS_ERROR = "error"
    print("MTUOC server started as OpenNMT server")
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
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    STATUS_OK = "ok"
    STATUS_ERROR = "error"
    print("MTUOC server started as NMTWizard server")
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
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    STATUS_OK = "ok"
    STATUS_ERROR = "error"
    print("MTUOC server started as ModernMT server")
    def start(
              url_root="",
              host="",
              port=MTUOCServer_port,
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
        print("MTUOC server started as Moses server IP:",ip," port:",MTUOCServer_port)
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
        
elif MTUOCServer_type=="Lucy":
    from flask import Flask, jsonify, request
    from dicttoxml import dicttoxml
    MTUOCServer_ONMT_url_root=config["MTUOCServer"]["ONMT_url_root"]
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    STATUS_OK = "ok"
    STATUS_ERROR = "error"
    print("MTUOC server started as Lucy server")
    STATUS_ERROR = "error"
    out={}
    def start(url_root="./AutoTranslateRS/V1.3",
              host="0.0.0.0",
              port=5000,
              debug=True):
        def prefix_route(route_function, prefix='', mask='{0}{1}'):
            def newroute(route, *args, **kwargs):
                return route_function(mask.format(prefix, route), *args, **kwargs)
            return newroute

        app = Flask(__name__)
        app.route = prefix_route(app.route, url_root)
        @app.route('/mtrans/exec/', methods=['POST'])
        def translateLucy():
            inputs = request.get_json(force=True)
            inputs0=inputs['inputParams']
            
            out = {}
            try:
                out = [[]]
                ss=inputs0['param'][4]['@value'].replace("[*áéíóúñ*] ","").lstrip()
                ts=translate_segment(ss)

                WORDS=len(ts.split())
                CHARACTERS=len(ts)
                INPUT=ss
                response_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><task><inputParams><param name="TRANSLATION_DIRECTION" value="'+TRANSLATION_DIRECTION+'"/><param name="MARK_UNKNOWNS" value="0"/><param name="MARK_ALTERNATIVES" value="0"/><param name="MARK_COMPOUNDS" value="0"/><param name="INPUT" value="'+str(INPUT)+'"/><param name="USER" value="'+USER+'"/></inputParams><outputParams><param name="OUTPUT" value="'+str(ts)+'"/><param name="MARK_UNKNOWNS" value="0"/><param name="MARK_ALTERNATIVES" value="0"/><param name="SENTENCES" value="1"/><param name="WORDS" value="'+str(WORDS)+'"/><param name="CHARACTERS" value="'+str(CHARACTERS)+'"/><param name="FORMAT" value="ASCII"/><param name="CHARSET" value="UTF"/><param name="SOURCE_ENCODING" value="UTF-8"/><param name="TARGET_ENCODING" value="UTF-8"/><param name="ERROR_MESSAGE" value=""/></outputParams></task>'
                out=response_xml
            except:
                out['error'] = "Error"
                out['status'] = STATUS_ERROR

            return out
            
        
        app.run(debug=debug, host=host, port=port, use_reloader=False,
            threaded=True)
    url_root=MTUOCServer_ONMT_url_root
    ip="0.0.0.0"
    ip=get_IP_info()
    debug="store_true"
    start(url_root="/AutoTranslateRS/V1.3", host=ip, port=MTUOCServer_port,debug=debug)

if MTUOCServer_type=="OpusMT":
    from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
    
    class OpusMT_server(WebSocket):
        def handleMessage(self):
            self.input=eval(self.data)
            self.translation=translate_segment(self.input['text'])
            self.data2 = {'result':  self.translation}
            self.jsondata=json.dumps(self.data2)
            self.sendMessage(self.jsondata)

        def handleConnected(self):
            printLOG(0,'Connected to: ',self.address[0].split(":")[-1])

        def handleClose(self):
            printLOG(0,'Disconnected from: ',self.address[0].split(":")[-1])
    server = SimpleWebSocketServer('', MTUOCServer_port, OpusMT_server)
    ip=get_IP_info()
    print("OpusMT server IP:",ip," port:",MTUOCServer_port)
    server.serveforever()
