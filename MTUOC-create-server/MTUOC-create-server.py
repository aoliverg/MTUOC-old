#    MTUOC-NMT-SP-preprocess
#    Copyright (C) 2022  Antoni Oliver
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

import sys
import os
from shutil import copyfile
import stat
import codecs
import yaml
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper
    
stream = open('config-create-server.yaml', 'r',encoding="utf-8")
config=yaml.load(stream, Loader=yaml.FullLoader)

MTUOC=config["MTUOC"]
Marian_dir=config["Marian_dir"]
Final_TA_engine_dir=config["Final_TA_engine_dir"]
MTUOC_server_dir=config["MTUOC_server_dir"]
Corpus_dir=config["Corpus_dir"]
Training_dir=config["Training_dir"]
SLcode3=config["SLcode3"]
TLcode3=config["TLcode3"]
SLcode2=config["SLcode2"]
TLcode2=config["TLcode2"]
CPU_GPU=config["CPU_GPU"]
mt_engine_port=config["mt_engine_port"]
server_port=config["server_port"]
server_type=config["server_type"]

if os.path.isdir(Final_TA_engine_dir):
    print("Final TA engine dir exists. Delete it or choose another one.")
    sys.exit()
else:
    os.makedirs(Final_TA_engine_dir)

files=["MTUOC-server.py","MTUOC-stop-server.py","MTUOC_tags.py","MTUOC_truecaser.py","WACalculatorEflomal.py","getWordAlignments.py"]


for file in files:
    src=os.path.join(MTUOC_server_dir,file)
    dst=os.path.join(Final_TA_engine_dir,file)
    copyfile(src, dst)
    
tokenizer="MTUOC_tokenizer_"+SLcode3+".py"
file1=os.path.join(MTUOC,tokenizer)
file2=os.path.join(Final_TA_engine_dir,tokenizer)
copyfile(file1, file2)
tokenizer="MTUOC_tokenizer_"+TLcode3+".py"
file1=os.path.join(MTUOC,tokenizer)
file2=os.path.join(Final_TA_engine_dir,tokenizer)
copyfile(file1, file2)

if CPU_GPU=="CPU":
    src=os.path.join(Marian_dir,"marian-server-CPU")
    dst=os.path.join(Final_TA_engine_dir,"marian-server")
    copyfile(src, dst)
elif CPU_GPU=="GPU":
    src=os.path.join(Marian_dir,"marian-GPU")
    dst=os.path.join(Final_TA_engine_dir,"marian-server")
    copyfile(src, dst)
os.chmod(os.path.join(Final_TA_engine_dir,"marian-server"), stat.S_IEXEC)

sortida=codecs.open(os.path.join(Final_TA_engine_dir,"config-server.yaml"),"w",encoding="utf-8")

cadena="MTEngine:"
sortida.write(cadena+"\n")
cadena="    MTengine: Marian"
sortida.write(cadena+"\n")
cadena="    startMTEngine: True"
sortida.write(cadena+"\n")
cadena="    startCommand: \"./marian-server -m model.npz -v vocab-"+SLcode2+".yml vocab-"+TLcode2+".yml -p "+str(mt_engine_port)+" --n-best --alignment hard  --normalize 1 --quiet &\""
sortida.write(cadena+"\n")
cadena="    IP: localhost"
sortida.write(cadena+"\n")
cadena="    port: "+str(mt_engine_port)
sortida.write(cadena+"\n")
cadena="    min_len_factor: 0.5"
sortida.write(cadena+"\n")

cadena="MTUOCServer:"
sortida.write(cadena+"\n")
cadena="  port: "+str(server_port)
sortida.write(cadena+"\n")
cadena="  type: "+server_type
sortida.write(cadena+"\n")
cadena="  verbosity_level: 3"
sortida.write(cadena+"\n")
cadena="  log_file: None"
sortida.write(cadena+"\n")
cadena="  restore_tags: True"
sortida.write(cadena+"\n")
cadena="  restore_strategy: mtengine"
sortida.write(cadena+"\n")
cadena="  alimodel: None"
sortida.write(cadena+"\n")
cadena="  strictTagRestoration: True"
sortida.write(cadena+"\n")
cadena="  restore_case: True"
sortida.write(cadena+"\n")
cadena="  URLs: True"
sortida.write(cadena+"\n")
cadena="  EMAILs: True"
sortida.write(cadena+"\n")
cadena="  add_trailing_space: True"
sortida.write(cadena+"\n")
cadena="  unescape_html: True"
sortida.write(cadena+"\n")
cadena="  ONMT_url_root: \"/translator\""
sortida.write(cadena+"\n")
cadena="Preprocess:"
sortida.write(cadena+"\n")
cadena="  sl_lang: "+SLcode2
sortida.write(cadena+"\n")
cadena="  tl_lang: "+TLcode2
sortida.write(cadena+"\n")
cadena="  sl_tokenizer: MTUOC_tokenizer_"+SLcode3+".py"
sortida.write(cadena+"\n")
cadena="  tl_tokenizer: MTUOC_tokenizer_"+TLcode3+".py"
sortida.write(cadena+"\n")
cadena="  tcmodel: tc."+SLcode2
sortida.write(cadena+"\n")
cadena="  sentencepiece: True"
sortida.write(cadena+"\n")
cadena="  sp_model_SL: spmodel.model"
sortida.write(cadena+"\n")
cadena="  sp_vocabulary_SL: vocab_file."+SLcode2
sortida.write(cadena+"\n")
cadena="  sp_splitter: \"▁\""
sortida.write(cadena+"\n")
cadena="  BPE: False"
sortida.write(cadena+"\n")
cadena="  bpecodes: codes_file"
sortida.write(cadena+"\n")
cadena="  bpe_joiner: \"@@\""
sortida.write(cadena+"\n")
cadena="  bos_annotate: <s>"
sortida.write(cadena+"\n")
cadena="  eos_annotate: </s>"
sortida.write(cadena+"\n")
cadena="  finaldetokenization: True"
sortida.write(cadena+"\n")
cadena="change_list: None "
sortida.write(cadena+"\n")
cadena="Lucy:"
sortida.write(cadena+"\n")
cadena="    TRANSLATION_DIRECTION: ENGLISH-SPANISH"
sortida.write(cadena+"\n")
cadena="    USER: traductor"
sortida.write(cadena+"\n")

#Corpus dir
file="tc."+SLcode2
src=os.path.join(Corpus_dir,file)
dst=os.path.join(Final_TA_engine_dir,file)
copyfile(src, dst)

file="spmodel.model"
src=os.path.join(Corpus_dir,file)
dst=os.path.join(Final_TA_engine_dir,file)
copyfile(src, dst)

file="vocab_file."+SLcode2
src=os.path.join(Corpus_dir,file)
dst=os.path.join(Final_TA_engine_dir,file)
copyfile(src, dst)

#Training_dir

file="model.npz"
src=os.path.join(Training_dir,file)
dst=os.path.join(Final_TA_engine_dir,file)
copyfile(src, dst)
try:
    file="vocab-"+SLcode2+".yml"
    src=os.path.join(Training_dir,file)
    dst=os.path.join(Final_TA_engine_dir,file)
    copyfile(src, dst)
except:
    pass
try:
    file="vocab_"+SLcode2+".yml"
    file2="vocab-"+SLcode2+".yml"
    src=os.path.join(Training_dir,file)
    dst=os.path.join(Final_TA_engine_dir,file2)
    copyfile(src, dst)
except:
    pass
    
try:
    file="vocab-"+TLcode2+".yml"
    src=os.path.join(Training_dir,file)
    dst=os.path.join(Final_TA_engine_dir,file)
    copyfile(src, dst)
except:
    pass
try:
    file="vocab_"+TLcode2+".yml"
    file2="vocab-"+TLcode2+".yml"
    src=os.path.join(Training_dir,file)
    dst=os.path.join(Final_TA_engine_dir,file2)
    copyfile(src, dst)
except:
    pass