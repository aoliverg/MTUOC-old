import os
import shutil
import codecs
import re

def splitnumbers(segment,joiner="@@"):
    joiner=joiner+" "
    xifres = re.findall(re_num,segment)
    for xifra in xifres:
        xifrastr=str(xifra)
        xifrasplit=xifra.split()
        xifra2=joiner.join(xifra)
        segment=segment.replace(xifra,xifra2)
    return(segment)

re_num = re.compile(r'[\d,.\-/]+')
re_num_tl = re.compile(r'(([\d,.\-/]\s?)+)')

def subwordnmt_train(INPUT,SLcode2="en",TLcode2="es",NUM_OPERATIONS=85000,CODES_file="codes_file"):
    if len(INPUT.split(" "))==1:
        command="subword-nmt learn-joint-bpe-and-vocab --input "+INPUT+" -s "+str(NUM_OPERATIONS)+" -o codes_file --write-vocabulary vocab_BPE."+SLcode2
    elif len(INPUT.split(" "))==2:
        command="subword-nmt learn-joint-bpe-and-vocab --input "+INPUT+" -s "+str(NUM_OPERATIONS)+" -o codes_file --write-vocabulary vocab_BPE."+SLcode2+" vocab_BPE."+TLcode2
    print(command)
    os.system(command)
    
def subwordnmt_encode(INFILE,OUTFILE,CODES_FILE="codes_file",VOCAB_FILE="vocab_BPE.en",VOCABULARY_THRESHOLD=50,JOINER="@",BPE_DROPOUT=True,BPE_DROPOUT_P="0.1", SPLIT_DIGITS=True,BOS="<s>",EOS="</s>"):
    if BPE_DROPOUT:
        dropoutstring="--dropout "+str(BPE_DROPOUT_P)
    else:
        dropoutstring=""
    command="subword-nmt apply-bpe -c "+CODES_FILE+" --vocabulary "+VOCAB_FILE+" --vocabulary-threshold "+str(VOCABULARY_THRESHOLD)+" --separator "+JOINER+" "+dropoutstring+" < "+INFILE+" > "+OUTFILE
    print(command)
    os.system(command)
    if SPLIT_DIGITS:
        shutil.copyfile(OUTFILE, "temp.temp")
        entrada=codecs.open("temp.temp","r",encoding="utf-8")
        sortida=codecs.open(OUTFILE,"w",encoding="utf-8")
        for linia in entrada:
            linia=linia.rstrip()
            linia=splitnumbers(linia,JOINER)
            sortida.write(linia+"\n")
        entrada.close()
        sortida.close()
    if not EOS=="" and not BOS=="":
        shutil.copy(OUTFILE,"outBPE.tmp")
        entrada=codecs.open("outBPE.tmp","r",encoding="utf-8")
        sortida=codecs.open(OUTFILE,"w",encoding="utf-8")
        for linia in entrada:
            linia=linia.rstrip()
            if not BOS=="":
                linia=BOS+" "+linia
            if not EOS=="":
                linia=linia+" "+EOS
            sortida.write(linia+"\n")
        os.remove("outBPE.tmp")
        
    