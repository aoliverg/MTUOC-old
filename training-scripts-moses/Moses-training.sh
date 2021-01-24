#ESPECIFICAMOS LOS CORPUS
trainPrefix="train.smt"
valPrefix="val.smt"

#ESPECIFICAMOS LAS LENGUAS
SL="en"
TL="es"

#ESPECIFICAMOS EL ORDEN DEL MODELO DE LENGUA
LMORDER=5

#A PARTIR DE AQUI NO ES NECESARIO CAMBIAR NADA

#DEFINIMOS VARIABLES DE ENTORNO
export PATH=/Moses/bin:$PATH
export MTOOLS="/Moses/tools"
export MCONTRIB="/Moses/contrib"
export MSCRIPTS="/Moses/scripts"
export MBIN="/Moses/bin/"

#EL DIRECTORIO ACTUAL
CURRENTDIR="$PWD"

echo "ENTRENAMIENTO DEL MODELO DE LENGUA"

mkdir lm
cd lm

$MBIN/lmplz -o $LMORDER <../$trainPrefix.$TL > lm.arpa.$TL

echo "BINARIZACIÓN DEL MODELO DE LENGUA"

$MBIN/build_binary lm.arpa.$TL lm.blm.$TL

cd ..

echo "ENTRENAMIENTO DEL MODELO DE TRADUCCIÓN"

mkdir working
cd working

$MSCRIPTS/training/train-model.perl -root-dir train -mgiza -corpus ../$trainPrefix  -f $SL -e $TL -alignment grow-diag-final-and -reordering msd-bidirectional-fe -lm 0:$LMORDER:$CURRENTDIR/lm/lm.blm.$TL:8 -external-bin-dir $MTOOLS > training.out 
