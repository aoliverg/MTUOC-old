#MOSES BINARY AND TOOLS DIRECTORY
MosesDIR="/Moses"

#CORPORA
trainPrefix="train.smt"
valPrefix="val.smt"

#LANGUAGES
SL="en"
TL="es"

#LANGUAGE MODEL ORDER
LMORDER=5

#NO NEED TO EDIT FURTHER

#ENVIRONMENT VARIABLE
export PATH=/$MosesDIR/bin:$PATH
export MTOOLS="/$MosesDIR/tools"
export MCONTRIB="/$MosesDIR/contrib"
export MSCRIPTS="/$MosesDIR/scripts"
export MBIN="/$MosesDIR/bin/"
export MSAM="/$MosesDIR/SALM"


CURRENTDIR="$PWD"

echo "LANGUAGE MODEL TRAINING"

mkdir lm
cd lm

$MBIN/lmplz -o $LMORDER <../$trainPrefix.$TL > lm.arpa.$TL

echo "BINARIZATION OF THE LANGUAGE MODEL"

$MBIN/build_binary lm.arpa.$TL lm.blm.$TL

cd ..

echo "TRAINING TRANSLATION MODEL"

mkdir working
cd working

$MSCRIPTS/training/train-model.perl -root-dir train -mgiza -corpus ../$trainPrefix  -f $SL -e $TL -alignment grow-diag-final-and -reordering msd-bidirectional-fe -lm 0:$LMORDER:$CURRENTDIR/lm/lm.blm.$TL:8 -external-bin-dir $MTOOLS > training.out 

cd ..

#SALM

echo "SALM"


$MSAM/IndexSA.O64 $trainPrefix.$TL 

$MSAM/IndexSA.O64 $trainPrefix.$SL 

zcat ./working/train/model/phrase-table.gz | $MCONTRIB/sigtest-filter/filter-pt -e $trainPrefix.$TL  -f $trainPrefix.$SL -l a+e -n 30 > ./working/train/model/phrase-table.pruned

gzip ./working/train/model/phrase-table.pruned

sed -i -e 's/phrase-table.gz/phrase-table.pruned.gz/g' ./working/train/model/moses.ini


echo "STARTING OPTIMIZATION"
echo "MERT-MOSES"

$MSCRIPTS/training/mert-moses.pl $valPrefix.$SL $valPrefix.$TL $MBIN/moses ./working/train/model/moses.ini --mertdir $MBIN &> mert.out 


#CREATION OF THE DIRECTORY FOR THE BINARIZED MODEL
mkdir binarised-model

#SORTING TRANSLATION MODEL
#BINARIZATION OF THE TRANSLATION MODEL
zcat ./working/train/model/phrase-table.pruned.gz | LC_ALL=C sort > ./working/train/model/phrase-table-sorted
gzip ./working/train/model/phrase-table-sorted
$MBIN/processPhraseTableMin -in ./working/train/model/phrase-table-sorted.gz -nscores 4 -out ./binarised-model/phrase-table-bin

#SORTING REORDERING MODEL
#BINARIZATION OF THE REORDERING MODEL
zcat ./working/train/model/reordering-table.wbe-msd-bidirectional-fe.gz | LC_ALL=C sort > ./working/train/model/reordering-table-sorted
gzip ./working/train/model/reordering-table-sorted
$MBIN/processLexicalTableMin -in ./working/train/model/reordering-table-sorted.gz -out ./binarised-model/reordering-table-bin -threads 4

#COPYING BINARIZED LANGUAGE MODEL TO THE FINAL MODEL DIRECTORY
cp ./lm/lm.blm.$TL ./binarised-model

#COPYING OPTIMIZED MOSES.INI TO THE FINAL MODEL DIRECTORY
cp ./mert-work/moses.ini ./binarised-model/moses.ini

#MODIFYING MOSES.INI
sed -i -e 's/.*PhraseDictionaryMemory.*/PhraseDictionaryCompact name=TranslationModel0 num-features=4 path=phrase-table-bin.minphr input-factor=0 output-factor=0/g' ./binarised-model/moses.ini
sed -i -e 's/.*LexicalReordering name.*/LexicalReordering name=LexicalReordering0 num-features=6 type=wbe-msd-bidirectional-fe-allff input-factor=0 output-factor=0 path=reordering-table-bin/g' ./binarised-model/moses.ini
sed -i -e "s/.*KENLM.*/KENLM name=LM0 factor=0 path=lm.blm.$TL order=$LMORDER/g" ./binarised-model/moses.ini

