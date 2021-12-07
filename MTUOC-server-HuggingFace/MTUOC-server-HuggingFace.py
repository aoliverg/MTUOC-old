#    MTUOC-server-HuggingFace
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

#adapted from: https://towardsdatascience.com/build-your-own-machine-translation-service-with-transformers-d0709df0791b

import os
from flask import Flask, request, jsonify
from translate import Translator
from config import *
import socket
import urllib
from urllib.request import urlretrieve
from config import *

#IMPORTS FOR YAML
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def get_IP_info(): 
    try: 
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name) 
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        return(IP)
    except: 
        IP = '127.0.0.1'
        return(IP)
    finally:
        s.close()    
        
def translate(segment):
    #function for Moses server
    translation=translator.translate(segment['text'])
    translationdict={}
    translationdict["text"]=translation
    return(translationdict)

def download_language_model(source,target):
    model = f"opus-mt-{source}-{target}"
    print(">>>Downloading data for %s to %s model..." % (source, target))
    os.makedirs(os.path.join("data",model))
    for f in FILENAMES:
        try:
            print(os.path.join(HUGGINGFACE_S3_BASE_URL,model,f))
            urlretrieve(os.path.join(HUGGINGFACE_S3_BASE_URL,model,f),
                                        os.path.join(MODEL_PATH,model,f))
            print("Download complete!")
        except urllib.error.HTTPError:
            print("Error retrieving model from url. Please confirm model exists.")
            os.rmdir(os.path.join("data",model))
            break

HUGGINGFACE_S3_BASE_URL="https://s3.amazonaws.com/models.huggingface.co/bert/Helsinki-NLP"
FILENAMES = ["config.json","pytorch_model.bin","source.spm","target.spm","tokenizer_config.json","vocab.json"]
MODEL_PATH = "data"


stream = open('config-server.yaml', 'r',encoding="utf-8")
config=yaml.load(stream,Loader=Loader)
SL=config['SL']
TL=config['TL']
GPU=config['GPU']
server_type=config['server_type']
port=config['port']
ONMT_url_root=config['ONMT_url_root']

route = f'{SL}-{TL}'
model = f'opus-mt-{route}'
path = os.path.join(MODEL_PATH,model)
if not os.path.isdir(path):
    download_language_model(SL,TL)

translator = Translator(MODEL_PATH,SL,TL,GPU=GPU)

app = Flask(__name__)
app.config["DEBUG"] = False # turn off in prod

@app.route('/', methods=["GET"])
def health_check():
    """Confirms service is running"""
    return "Machine translation service is up and running."



if server_type=="MTUOC":
    from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
    
    class MTUOC_server(WebSocket):
        def handleMessage(self):
            self.translation=translator.translate(self.data)
            self.sendMessage(self.translation)

        def handleConnected(self):
            #printLOG(0,'Connected to: ',self.address[0].split(":")[-1])
            pass
        def handleClose(self):
            #printLOG(0,'Disconnected from: ',self.address[0].split(":")[-1])
            pass
    server = SimpleWebSocketServer('', port, MTUOC_server)
    ip=get_IP_info()
    print("MTUOC server IP:",ip," port:",port)
    server.serveforever()

elif server_type=="OpenNMT":
    from flask import Flask, jsonify, request
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
                ts=translator.translate(ss)
                response = {"src": ss, "tgt": ts,
                                "n_best": 0, "pred_score": 0}
                    
                out[0].append(response)
            except:
                out['error'] = "Error"
                out['status'] = STATUS_ERROR

            return jsonify(out)
            
        
        app.run(debug=debug, host=host, port=port, use_reloader=False,
            threaded=True)
    url_root=ONMT_url_root
    ip="0.0.0.0"
    ip=get_IP_info()
    debug="store_true"
    start(url_root=MTUOCServer_url_root, host=ip, port=port,debug=debug)

elif server_type=="NMTWizard":
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
                targettext=translator.translate(sourcetext)
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
    start(url_root=url_root, host=ip, port=port,debug=debug)

elif server_type=="ModernMT":
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
                translation=translator.translate(segment)
                print("SEGMENT",segment)
                print("TRANSLATION",translation)
                out['data']['translation']=translation
            except:
                out['status'] = STATUS_ERROR
            return jsonify(out)
        ip=get_IP_info()
        app.run(debug=True, host=ip, port=port, use_reloader=False,
                threaded=True)
    start()

elif server_type=="Moses":
    from xmlrpc.server import SimpleXMLRPCServer
    server = SimpleXMLRPCServer(
    ("", port),
    logRequests=True,)
    server.register_function(translate)
    server.register_introspection_functions()
    # Start the server
    try:
        ip=get_IP_info()
        print("Moses server IP:",ip," port:",port)
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
