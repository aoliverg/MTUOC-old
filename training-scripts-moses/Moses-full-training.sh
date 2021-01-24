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

cd ..

echo "INICIAMOS OPTIMIZACIÓN"
echo "MERT-MOSES"

$MSCRIPTS/training/mert-moses.pl $valPrefix.$SL $valPrefix.$TL $MBIN/moses ./working/train/model/moses.ini --mertdir $MBIN &> mert.out 



#CREAMOS EL DIRECTORIO DONDE ESTARÁ EL MODELO BINARIZADO
mkdir binarised-model

#ORDENAMOS MODELO DE TRADUCCIÓN
#BINARIZAMOS MODELO DE TRADUCCIÓN
zcat ./working/train/model/phrase-table.gz | LC_ALL=C sort > ./working/train/model/phrase-table-sorted
gzip ./working/train/model/phrase-table-sorted
$MBIN/processPhraseTableMin -in ./working/train/model/phrase-table-sorted.gz -nscores 4 -out ./binarised-model/phrase-table-bin

#ORDENAMOS MODELO DE REORDENAMIENTO
#BINARIZAMOS MODELO DE REORDENAMIENTO
zcat ./working/train/model/reordering-table.wbe-msd-bidirectional-fe.gz | LC_ALL=C sort > ./working/train/model/reordering-table-sorted
gzip ./working/train/model/reordering-table-sorted
$MBIN/processLexicalTableMin -in ./working/train/model/reordering-table-sorted.gz -out ./binarised-model/reordering-table-bin -threads 4

#COPIAMOS EL MODELO DE LENGUA BINARIZADO AL DIRECTORIO 
cp ./lm/lm.blm.$TL ./binarised-model

#COPIAMOS EL MOSES.INI OPTIMIZADO AL DIRECTORIO
cp ./mert-work/moses.ini ./binarised-model/moses.ini

#MODIFICAMOS EL MOSES.INI
sed -i -e 's/.*PhraseDictionaryMemory.*/PhraseDictionaryCompact name=TranslationModel0 num-features=4 path=phrase-table-bin.minphr input-factor=0 output-factor=0/g' ./binarised-model/moses.ini
sed -i -e 's/.*LexicalReordering name.*/LexicalReordering name=LexicalReordering0 num-features=6 type=wbe-msd-bidirectional-fe-allff input-factor=0 output-factor=0 path=reordering-table-bin/g' ./binarised-model/moses.ini
sed -i -e "s/.*KENLM.*/KENLM name=LM0 factor=0 path=lm.blm.$TL order=$LMORDER/g" ./binarised-model/moses.ini

