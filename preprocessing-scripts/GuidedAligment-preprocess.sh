#!/bin/bash
cd $(dirname $0)

#DIRECTORY WHERE MTUOC SCRIPTS ARE LOCATED
MTUOC="/MTUOC3"

#NAME AND LANGUAGES OF THE CORPUS
#NOTE: The corpus should be uniq and shuffled
ROOTNAME="train.sp"
ROOTNAME_OUT="train"

SL="en"
TL="es"


ALIGNER=eflomal
#one of eflomal, fast_align
BOTH_DIRECTIONS=false #only for fast_align, eflomal aligns always the two directions at the same time
DELETE_EXISTING=true
DELETE_TEMP=true

if [ $DELETE_EXISTING = true ]
then
FILE="$ROOTNAME_OUT.$SL.$TL.align" 
if test -f "$FILE"; then
    rm "$ROOTNAME_OUT.$SL.$TL.align"
fi
FILE="$ROOTNAME_OUT.$TL.$SL.align" 
if test -f "$FILE"; then
    rm "$ROOTNAME_OUT.$TL.$SL.align" 
fi
fi


paste "$ROOTNAME.$SL" "$ROOTNAME.$TL" | sed 's/\t/ ||| /g' > "corpus.$SL.$TL.fa"

if [ $ALIGNER = fast_align ]
then


"$MTUOC/fast_align" -vdo -i "corpus.$SL.$TL.fa" > "forward.$SL.$TL.align"
"$MTUOC/fast_align" -vdor -i "corpus.$SL.$TL.fa" > "reverse.$SL.$TL.align"
"$MTUOC/atools" -c grow-diag-final -i "forward.$SL.$TL.align" -j "reverse.$SL.$TL.align" > "$ROOTNAME_OUT.$SL.$TL.align"

if [ $BOTH_DIRECTIONS = true ]
then
paste "$ROOTNAME.$TL" "$ROOTNAME.$SL" | sed 's/\t/ ||| /g' > "corpus.$TL.$SL.fa"
"$MTUOC/fast_align" -vdo -i "corpus.$TL.$SL.fa" > "forward.$TL.$SL.align"
"$MTUOC/fast_align" -vdor -i "corpus.$TL.$SL.fa" > "reverse.$TL.$SL.align"
"$MTUOC/atools" -c grow-diag-final -i "forward.$TL.$SL.align" -j "reverse.$TL.$SL.align" > "$ROOTNAME_OUT.$TL.$SL.align"
fi

fi

if [ $ALIGNER = eflomal ]
then
python3 "$MTUOC/eflomal-align.py" -i "corpus.$SL.$TL.fa" --model 3 -f "$ROOTNAME_OUT.$SL.$TL.align" -r "$ROOTNAME_OUT.$TL.$SL.align"
fi

if [ $DELETE_TEMP = true ]
then
rm "corpus.$SL.$TL.fa" || echo ""
if [ $ALIGNER = fast_align ]
then
rm "forward.$SL.$TL.align" 
rm "reverse.$SL.$TL.align" 
fi
fi
