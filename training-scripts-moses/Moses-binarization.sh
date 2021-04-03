export MBIN="/Moses/bin/"

#ESPECIFICAMOS LOS CORPUS
trainPrefix="train.smt"
valPrefix="val.smt"


#LENGUAS DEL PARTIDA Y DE LLEGADA
SL="en"
TL="es"

#ORDEN DEL MODELO DE LENGUA
LMORDER=5

#CREAMOS EL DIRECTORIO DONDE ESTARÁ EL MODELO BINARIZADO
mkdir binarised-model

#ORDENAMOS MODELO DE TRADUCCIÓN
#BINARIZAMOS MODELO DE TRADUCCIÓN
zcat ./working/train/model/phrase-table.pruned.gz | LC_ALL=C sort > ./working/train/model/phrase-table-sorted
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

