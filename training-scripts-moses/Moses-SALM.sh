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
export MSAM="/Moses/SALM"


echo "INICIAMOS SALM"


$MSAM/IndexSA.O64 $trainPrefix.$TL 

$MSAM/IndexSA.O64 $trainPrefix.$SL 

zcat ./working/train/model/phrase-table.gz | $MCONTRIB/sigtest-filter/filter-pt -e $trainPrefix.$TL  -f $trainPrefix.$SL -l a+e -n 30 > ./working/train/model/phrase-table.pruned

gzip ./working/train/model/phrase-table.pruned

sed -i -e 's/phrase-table.gz/phrase-table.pruned.gz/g' ./working/train/model/moses.ini
