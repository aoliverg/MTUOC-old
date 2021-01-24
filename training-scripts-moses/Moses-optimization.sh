#ESPECIFICAMOS LOS CORPUS
trainPrefix="train.smt"
valPrefix="val.smt"

#ESPECIFICAMOS LAS LENGUAS
SL="en"
TL="es"

#DEFINIMOS VARIABLES DE ENTORNO
export PATH=/Moses/bin:$PATH
export MTOOLS="/Moses/tools"
export MCONTRIB="/Moses/contrib"
export MSCRIPTS="/Moses/scripts"
export MBIN="/Moses/bin/"

echo "INICIAMOS OPTIMIZACIÓN"
echo "MERT-MOSES"

$MSCRIPTS/training/mert-moses.pl $valPrefix.$SL $valPrefix.$TL $MBIN/moses ./working/train/model/moses.ini --mertdir $MBIN &> mert.out 


