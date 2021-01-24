import os
import codecs
import sys


def guided_alignment_eflomal(MTUOC="/MTUOC",ROOTNAME_ALI="train.sp",ROOTNAME_OUT="train.sp",SL="en",TL="es",SPLIT_LIMIT=1000000,VERBOSE=True):
    if VERBOSE: print("Alignment using eflomal:",ROOTNAME_ALI,SL,TL)
    sys.path.append(MTUOC)
    from MTUOC_check_guided_alignment import check_guided_alignment
    FILE1=ROOTNAME_ALI+"."+SL
    FILE2=ROOTNAME_ALI+"."+TL
    FILEOUT="corpus."+SL+"."+TL+"."+"fa"
    command="paste "+FILE1+" "+FILE2+" | sed 's/\t/ ||| /g' > "+FILEOUT
    if VERBOSE: print(command)
    os.system(command)
    command="split -l "+str(SPLIT_LIMIT)+" "+FILEOUT+" tempsplitted-"
    if VERBOSE: print(command)
    os.system(command)
    
    listfiles = os.listdir(".")
    print(listfiles)
    
    for file in listfiles:
        if file.startswith("tempsplitted-"):
            tempaliforward="tempaliforward-"+file.split("-")[1]
            tempalireverse="tempalireverse-"+file.split("-")[1]
            command=MTUOC+"/eflomal-align.py -i "+file+" --model 3 -f "+tempaliforward+" -r "+tempalireverse
            if VERBOSE: print(command)
            os.system(command)
    
    command="cat tempaliforward-* > "+ROOTNAME_OUT+"."+SL+"."+TL+".align"
    if VERBOSE: print(command)
    os.system(command)
    command="cat tempalireverse-* > "+ROOTNAME_OUT+"."+TL+"."+SL+".align"
    if VERBOSE: print(command)
    os.system(command)
    if VERBOSE: print("Checking guided alignment")
    check_guided_alignment(FILE1,FILE2,ROOTNAME_OUT+"."+SL+"."+TL+".align",ROOTNAME_OUT+"."+TL+"."+SL+".align")
    listfiles = os.listdir(".")
    os.remove(FILEOUT)
    #os.remove(ROOTNAME_OUT+".novalid."+TL+"."+SL+".align")
    for file in listfiles:
        if file.startswith("tempsplitted-") or file.startswith("tempaliforward") or file.startswith("tempalireverse"):
            os.remove(file)
    

if __name__ == "__main__":
    MTUOC=sys.argv[1]
    ROOTNAME_ALI=sys.argv[2]
    ROOTNAME_OUT=sys.argv[3]
    SL=sys.argv[4]
    TL=sys.argv[5]
    SPLIT_LIMIT=sys.argv[6]
    if len(sys.argv)>7:
        VERBOSE=sys.argv[7]
    else:
        VERBOSE=True
    guided_alignment_eflomal(MTUOC,ROOTNAME_ALI,ROOTNAME_OUT,SL,TL,SPLIT_LIMIT,VERBOSE)
