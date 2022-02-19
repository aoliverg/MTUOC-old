import os
import codecs
import sys


def guided_alignment_fast_align(MTUOC="/MTUOC",ROOTNAME_ALI="train.sp",ROOTNAME_OUT="train.sp",SL="en",TL="es",BOTH_DIRECTIONS=False,VERBOSE=True):
    if VERBOSE: print("Alignment using fast_align:",ROOTNAME_ALI,SL,TL)
    sys.path.append(MTUOC)
    from MTUOC_check_guided_alignment import check_guided_alignment
    FILE1=ROOTNAME_ALI+"."+SL
    FILE2=ROOTNAME_ALI+"."+TL
    FILEOUT="corpus."+SL+"."+TL+"."+"fa"
    FORWARDALI=ROOTNAME_OUT+"."+SL+"."+TL+".align"
    REVERSEALI=ROOTNAME_OUT+"."+TL+"."+SL+".align"
    command="paste "+FILE1+" "+FILE2+" | sed 's/\t/ ||| /g' > "+FILEOUT
    if VERBOSE: print(command)
    os.system(command)
    
    command=MTUOC+"/fast_align -vdo -i corpus."+SL+"."+TL+".fa > forward."+SL+"."+TL+".align"
    if VERBOSE: print(command)
    os.system(command)
    command=MTUOC+"/fast_align -vdor -i corpus."+SL+"."+TL+".fa > reverse."+SL+"."+TL+".align"
    if VERBOSE: print(command)
    os.system(command)
    command=MTUOC+"/atools -c grow-diag-final -i forward."+SL+"."+TL+".align -j reverse."+SL+"."+TL+".align > "+FORWARDALI
    if VERBOSE: print(command)
    os.system(command)
    '''
    if BOTH_DIRECTIONS:
        FILE1=ROOTNAME_ALI+"."+SL
        FILE2=ROOTNAME_ALI+"."+TL
        FILEOUT="corpus."+TL+"."+SL+"."+"fa"
        command="paste "+FILE2+" "+FILE1+" | sed 's/\t/ ||| /g' > "+FILEOUT
        if VERBOSE: print(command)
        os.system(command)
        command=MTUOC+"/fast_align -vdo -i corpus."+TL+"."+SL+".fa > forward."+TL+"."+SL+".align"
        if VERBOSE: print(command)
        os.system(command)
        command=MTUOC+"/fast_align -vdor -i corpus."+TL+"."+SL+".fa > reverse."+TL+"."+SL+".align"
        if VERBOSE: print(command)
        os.system(command)
        command=MTUOC+"/atools -c grow-diag-final -i forward."+TL+"."+SL+".align -j reverse."+TL+"."+SL+".align > "+REVERSEALI
        if VERBOSE: print(command)
        os.system(command)
    
    '''
    if VERBOSE: print("Checking guided alignment")
    check_guided_alignment(FILE1,FILE2,ROOTNAME_OUT+"."+SL+"."+TL+".align","todelete.align")
    listfiles = os.listdir(".")
    try:
        os.remove(FILEOUT)
    except:
        pass
    try:
        os.remove("forward."+SL+"."+TL+".align")
    except:
        pass
    try:
        os.remove("reverse."+SL+"."+TL+".align")
    except:
        pass
    try:
        os.remove("forward."+TL+"."+SL+".align")
    except:
        pass
    try:
        os.remove("reverse."+TL+"."+SL+".align")
    except:
        pass
    

if __name__ == "__main__":
    MTUOC=sys.argv[1]
    ROOTNAME_ALI=sys.argv[2]
    ROOTNAME_OUT=sys.argv[3]
    SL=sys.argv[4]
    TL=sys.argv[5]
    if len(sys.argv)>6:
        BOTH_DIRECTIONS=sys.argv[6]
    else:
        BOTH_DIRECTIONS=True
    if len(sys.argv)>7:
        VERBOSE=sys.argv[7]
    else:
        VERBOSE=True
    guided_alignment_fast_align(MTUOC,ROOTNAME_ALI,ROOTNAME_OUT,SL,TL,BOTH_DIRECTIONS,VERBOSE)
