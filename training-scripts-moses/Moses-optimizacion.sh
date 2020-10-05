#ESPECIFICAMOS LAS LENGUAS
SL="en"
TL="es"

#DEFINIMOS VARIABLES DE ENTORNO
export PATH=/TA-Tools/mosesdecoder/bin:$PATH
export MTOOLS="/TA-Tools/mosesdecoder/tools"
export MCONTRIB="/TA-Tools/mosesdecoder/contrib"
export MSCRIPTS="/TA-Tools/mosesdecoder/scripts"
export MBIN="/TA-Tools/mosesdecoder/bin/"

echo "INICIAMOS OPTIMIZACIÓN"
echo "MERT-MOSES"

$MSCRIPTS/training/mert-moses.pl val.$SL val.$TL $MBIN/moses ./working/train/model/moses.ini --mertdir $MBIN &> mert.out 

cd ..
