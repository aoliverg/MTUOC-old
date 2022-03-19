import os

def sentencepiece_train(corpusPreSL,corpusPreTL,SLcode2="en",TLcode2="es",JOIN_LANGUAGES=True,SP_MODEL_PREFIX="spmodel",MODEL_TYPE="bpe",VOCAB_SIZE=32000,CHARACTER_COVERAGE=1,INPUT_SENTENCE_SIZE=1000000,SPLIT_DIGITS=True,CONTROL_SYMBOLS="",USER_DEFINED_SYMBOLS=""):
    options=[]
    if SPLIT_DIGITS:
        options.append("--split_digits=true")
    else:
        options.append("--split_digits=false")
    if not CONTROL_SYMBOLS=="":
        options.append("--control_symbols=\""+CONTROL_SYMBOLS+"\"")
    if not USER_DEFINED_SYMBOLS=="":
        options.append("--user_defined_symbols=\""+USER_DEFINED_SYMBOLS+"\"")
    
        
    options=" ".join(options)
    if JOIN_LANGUAGES:
        command = "cat "+corpusPreSL+" "+corpusPreTL+" | shuf > train"
        os.system(command)        
        command="spm_train --input=train --model_prefix="+SP_MODEL_PREFIX+" --model_type="+MODEL_TYPE+" --vocab_size="+str(VOCAB_SIZE)+" --character_coverage="+str(CHARACTER_COVERAGE)+" --split_digits --input_sentence_size="+str(INPUT_SENTENCE_SIZE)+" "+options
        print(command)
        os.system(command)
        command="spm_encode --model="+SP_MODEL_PREFIX+".model --generate_vocabulary < "+corpusPreSL+" > vocab_file."+SLcode2
        os.system(command)
        command="spm_encode --model="+SP_MODEL_PREFIX+".model --generate_vocabulary < "+corpusPreTL+" > vocab_file."+TLcode2
        os.system(command)
        
    else:
        command="spm_train --input="+corpusPreSL+" --model_prefix="+SP_MODEL_PREFIX+"-"+SLcode2+" --model_type="+MODEL_TYPE+" --vocab_size="+str(VOCAB_SIZE)+" --character_coverage="+str(CHARACTER_COVERAGE)+" --split_digits --input_sentence_size="+str(INPUT_SENTENCE_SIZE)+" "+options
        print(command)
        os.system(command)
        command="spm_train --input="+corpusPreTL+" --model_prefix="+SP_MODEL_PREFIX+"-"+TLcode2+" --model_type="+MODEL_TYPE+" --vocab_size="+str(VOCAB_SIZE)+" --character_coverage="+str(CHARACTER_COVERAGE)+" --split_digits --input_sentence_size="+str(INPUT_SENTENCE_SIZE)+" "+options
        print(command)
        os.system(command)
        command="spm_encode --model="+SP_MODEL_PREFIX+"-"+SLcode2+".model --generate_vocabulary < "+corpusPreSL+" > vocab_file."+SLcode2
        os.system(command)
        command="spm_encode --model="+SP_MODEL_PREFIX+"-"+TLcode2+".model --generate_vocabulary < "+corpusPreTL+" > vocab_file."+TLcode2
        os.system(command)
        
def sentencepiece_encode(corpusPre,OUTFILE,SP_MODEL,VOCABULARY,VOCABULARY_THRESHOLD=50, EOS=True, BOS=True):
    if EOS and BOS:
        extraoptions="--extra_options eos:bos"
    elif EOS:
        extraoptions="--extra_options eos"
    elif BOS:
        extraoptions="--extra_options bos"
    else:
        extraoptions=""
    command="spm_encode --model="+SP_MODEL+" "+extraoptions+" --vocabulary="+VOCABULARY+" --vocabulary_threshold="+str(VOCABULARY_THRESHOLD)+" < "+corpusPre+" > "+OUTFILE
    os.system(command)
