#    MTUOC-server-SP v 4  
#    Description: an MTUOC server using Sentence Piece as preprocessing step
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

import lxml

import html

###YAML IMPORTS
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    

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


#PREPROCESSING AND POSTPROCESSING

def to_MT_SP(segment,tokenizer,truecaser,spmodel, vocab, bos="<s>", eos='</s>'):
    hastags=tagrestorer.has_tags(segment)
    segment=segment.strip()
    if not truecaser==None:        
        segmenttrue=truecaser.truecase(segment)
        printLOG(3,"Segment TC",segmenttrue)
    else:
        segmenttrue=segment
    
    if not hastags:
        output=sp.encode(segmenttrue)
    else:
        output=[]
        if not bos==None: output.append("<s>")
        segmenttrue=tokenizerSL.tokenize(segmenttrue)
        for t in tagrestorer.splitTags(segmenttrue):
            if not tagrestorer.is_tag(t):
                sptok=" ".join(sp2.encode(t))
                output.append(sptok)
            else:
                output.append(t)
        if not eos==None: output.append("</s>")
    output=" ".join(output)
    return(output)

def from_MT_SP(sourcesegment,segment, tokenizer, joiner="▁",bos="<s>", eos="</s>"):
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
    ssfch=""
    for char in sourcesegment:
        if char.isalpha():
            ssfch=char 
            break
    if ssfch==ssfch.upper():
        segmenttrue=truecaser.detruecase(segment,tokenizer)
    else:
        segmenttrue=segment
    segmentdetok=tokenizer.detokenize_j(segmenttrue)
    tags=re.findall(r'<[^>]+>',segmentdetok)
    for tag in tags:
        if tag.find("▁")>-1:
            tagmod=tag.replace("▁"," ")
            segmentdetok=segmentdetok.replace(tag,tagmod,1)
    segmentdetok=segmentdetok.strip()
    return(segmentdetok)

def translate(segment):
    #function for Moses server
    translation=translate_segment(segment['text'])
    translationdict={}
    translationdict["text"]=translation
    return(translationdict)

def translate_segment(segment):
    try:
        printLOG(1,"Source segment:",segment)    
        if unescape_html:
            segment=html.unescape(segment)
            printLOG(3,"Unescaped segment:",segment)
        #leading and trailing spaces
        leading_spaces=len(segment)-len(segment.lstrip())
        trailing_spaces=len(segment)-len(segment.rstrip())-1
        segment=segment.lstrip().rstrip()
        ###Pretractament dels tags
        (segmentTAGS,equilG)=tagrestorer.group_tags(segment)
        (segmentTAGS,equil)=tagrestorer.replace_tags(segmentTAGS)
        
        tagInici=""
        tagFinal=""
        (segmentTAGS,tagInici,tagFinal)=tagrestorer.remove_start_end_tag(segmentTAGS)
        if not tagInici=="": printLOG(3,"Starting tag:",tagInici)
        if not tagFinal=="": printLOG(3,"Ending tag:",tagFinal)
        segmentNOTAGS=tagrestorer.remove_tags(segment)
        if MTUOCServer_EMAILs:
            segmentNOTAGS=replace_EMAILs(segmentNOTAGS)
        if MTUOCServer_URLs:
            segmentNOTAGS=replace_URLs(segmentNOTAGS)
        segmentPRENOTAGS=to_MT_SP(segmentNOTAGS,tokenizerSL,truecaser,spmodel,spvocab)
        printLOG(2,"Segment Pre. No Tags:",segmentPRENOTAGS)
        segmentPRETAGS=to_MT_SP(segmentTAGS,tokenizerSL,truecaser,spmodel,spvocab)
        if not segmentPRETAGS==segmentPRENOTAGS: printLOG(3,"Segment Pre. Tags:",segmentPRETAGS)
        hastags=tagrestorer.has_tags(segment)
        if MTUOCServer_MTengine=="Marian":
            (selectedtranslationPre, selectedalignment)=translate_segment_Marian(segmentPRENOTAGS)
        elif MTUOCServer_MTengine=="OpenNMT":
            print("TRANSLATING WITH OPENNMT")
            (selectedtranslationPre, selectedalignment)=translate_segment_OpenNMT(segmentPRENOTAGS)
            print("TRANSLATION",selectedtranslationPre)
        ###TO DO IMPLEMENT OTHER MT SYSTEMS: OpenNMT and ModernMT        
        
        #restoring tags
        if MTUOCServer_restore_tags and hastags:
            selectedtranslationTags=tagrestorer.restore_tags(segmentPRENOTAGS, segmentPRETAGS, selectedalignment, selectedtranslationPre, spechar="▁")
            printLOG(2,"Translation Restored Tags:",selectedtranslationTags)
        else:
            selectedtranslationTags=selectedtranslationPre
        
        #Leading and trailing tags
        selectedtranslationTags=from_MT_SP(segment,selectedtranslationTags,tokenizerSL)
        if tagInici:
            selectedtranslationTags=tagInici+selectedtranslationTags
        if tagFinal:
            selectedtranslationTags=selectedtranslationTags+tagFinal
        #Restoring real tags
        for t in equil:
            selectedtranslationTags=selectedtranslationTags.replace(t,equil[t])
        for t in equilG:
            selectedtranslationTags=selectedtranslationTags.replace(t,equilG[t])
        printLOG(2,"Translation Restored Real Tags:",selectedtranslationTags)
        #restoring/removing spaces before and after tags
        if MTUOCServer_restore_tags and hastags:
            selectedtranslationTags=tagrestorer.repairSpacesTags(segment,selectedtranslationTags)
        #restoring leading and trailing spaces
        lSP=leading_spaces*" "
        tSP=trailing_spaces*" "
        selectedtranslation=lSP+selectedtranslationTags+tSP
        #restoring case
        if MTUOCServer_restore_case:
            if segment==segment.upper():
                selectedtranslation=selectedtranslation.upper()
            elif not selectedalignment=="":
                selectedtranslation=tagrestorer.restoreCase(segment, segmentPRENOTAGS, selectedalignment, selectedtranslationPre, selectedtranslation,tokenizerSL,tokenizerTL)
            printLOG(2,"Translation Restored Case:",selectedtranslation)
            
                
        if MTUOCServer_EMAILs:
            selectedtranslation=restore_EMAILs(segment,selectedtranslation)
        if MTUOCServer_URLs:
            selectedtranslation=restore_URLs(segment,selectedtranslation)
        
                
    except:
        print("ERROR:",sys.exc_info())
    if add_trailing_space:
        selectedtranslation=selectedtranslation+" "
    printLOG(1,"Translation:",selectedtranslation) 
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
    printLOG(2,"Selected translation from Marian:",selectedtranslationPre)
    printLOG(2,"Selected alignment from Marian:",selectedalignment)
    return(selectedtranslationPre, selectedalignment)


def translate_segment_OpenNMT(segmentPre):
    print("ONMT",segmentPre)
    params = [{ "src" : segmentPre}]

    response = requests.post(url, json=params, headers=headers)
    print("RESPONSE",response)
    target = response.json()
    print("TARGET",target)
    selectedtranslationPre=target[0][0]["tgt"]
    if "align" in target[0][0]:
        selectedalignment=target[0][0]["align"][0]
    else:
        selectedalignments=""
    
    
    return(selectedtranslationPre, selectedalignments)
    
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
verbosity_level=int(config["MTUOCServer"]["verbosity_level"])
log_file=config["MTUOCServer"]["log_file"]
if log_file:
    sortidalog=codecs.open(log_file,"a",encoding="utf-8")
MTUOCServer_restore_tags=config["MTUOCServer"]["restore_tags"]
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
spmodel=config["Preprocess"]["sp_model_SL"]
spvocab=config["Preprocess"]["sp_vocabulary_SL"]
spvocabulary_threshold=config["Preprocess"]["sp_vocabulary_threshold"]
tcmodel=config["Preprocess"]["tcmodel"]
bos_annotate=config["Preprocess"]["bos_annotate"]
eos_annotate=config["Preprocess"]["eos_annotate"]
sp_joiner=config["Preprocess"]["sp_joiner"]

if tcmodel:
    from MTUOC_truecaser import Truecaser
    truecaser=Truecaser(tokenizer=MTUOCtokenizerSL,tc_model=tcmodel)
else:
    truecaser=None

if not MTUOCServer_MTengine=="ModernMT":
    if not MTUOCtokenizerSL.endswith(".py"): MTUOCtokenizerSL=MTUOCtokenizerSL+".py"

    spec = importlib.util.spec_from_file_location('', MTUOCtokenizerSL)
    tokenizerSLmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tokenizerSLmod)
    tokenizerSL=tokenizerSLmod.Tokenizer()
    
    if not MTUOCtokenizerTL.endswith(".py"): MTUOCtokenizerTL=MTUOCtokenizerTL+".py"

    spec = importlib.util.spec_from_file_location('', MTUOCtokenizerTL)
    tokenizerTLmod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tokenizerTLmod)
    tokenizerTL=tokenizerTLmod.Tokenizer()
    
    from MTUOC_tags import TagRestorer
    tagrestorer=TagRestorer()
    
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
    
    
#STARTING MTUOC SERVER

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
        print("Moses server IP:",ip," port:",MTUOCServer_port)
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
