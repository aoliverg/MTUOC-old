#!/bin/bash
cd $(dirname $0)

#NAME AND LANGUAGES OF THE CORPUS
ROOTNAME="corpus"
SL="en"
TL="es"

#Mosesdecoder directory
MOSESDECODER_DIR="/TA-Tools/mosesdecoder"
#MTUOC's scripts directory
MTUOC="/MTUOC"
#TOKENIZATION
TOKENIZE_SL=true
TOKENIZE_TL=true
#CLEANING
CLEAN=true
    CLEAN_MAX_TOK=80
LEARN_TRUECASER_SL=true
LEARN_TRUECASER_TL=true

TRUECASE_SL=true
TRUECASE_TL=true

#SPLITTING NUMBERS
SPLIT_NUMBERS_SL=true
SPLIT_NUMBERS_TL=true

#REPLACING NUMERS
REPLACE_NUMBERS_SL=true
REPLACE_NUMBERS_TL=true

#SUBWORDS
LEARN_BPE=false
JOIN_LANGUAGES=true
APPLY_BPE=false
    VOCABULARY_THRESHOLD=50
    BPE_DROPOUT=true
    BPE_DROPOUT_P=0.1

#SPLITTING CORPUS
SPLIT_CORPUS=true
    lval=100
    leval=100
    SPLIT_SPLITTED=false
    SPLIT_NUM=false
    SPLIT_BPE=false

#DELETING TEMPORAL FILES
DELETE_TOK=false
DELETE_TRUE=false
DELETE_SPLIT=false
DELETE_NUM=false



TOKENIZER_DIR="$MOSESDECODER_DIR/scripts/tokenizer"
TRAINING_DIR="$MOSESDECODER_DIR/scripts/training"
RECASER_DIR="$MOSESDECODER_DIR/scripts/recaser"
if [ $TOKENIZE_SL = true  ] 
then
echo "TOKENIZING SL"
cat "$ROOTNAME.$SL" | perl "$TOKENIZER_DIR/tokenizer.perl" "-l" "$SL" "-no-escape" > "$ROOTNAME.tok.$SL"
fi
if [ $TOKENIZE_TL = true  ] 
then
echo "TOKENIZING TL"
cat "$ROOTNAME.$TL" | perl "$TOKENIZER_DIR/tokenizer.perl" "-l" "$TL" "-no-escape" > "$ROOTNAME.tok.$TL"
fi
#CLEANING
if [ $CLEAN = true  ] 
then
echo "CLEANING"
perl "$TRAINING_DIR/clean-corpus-n.perl" "$ROOTNAME.tok" "$SL" "$TL" "$ROOTNAME.tok.clean" 1 "$CLEAN_MAX_TOK"
fi
#TRUECASING
if [ $LEARN_TRUECASER_SL = true  ] 
then
echo "LEARNING TRUECASER SL"
#trained with tokenized, before cleaning
perl "$RECASER_DIR/train-truecaser.perl" --model "tc.$SL" --corpus "$ROOTNAME.tok.$SL"
fi
if [ $LEARN_TRUECASER_TL = true  ] 
then
echo "LEARNING TRUECASER TL"
#trained with tokenized, before cleaning
perl "$RECASER_DIR/train-truecaser.perl" --model "tc.$TL" --corpus "$ROOTNAME.tok.$TL"
fi
if [ $TRUECASE_SL = true  ] 
then
echo "TRUECASING SL"
perl "$RECASER_DIR/truecase.perl" --model "tc.$SL" < "$ROOTNAME.tok.clean.$SL" > "$ROOTNAME.true.$SL"
fi
if [ $TRUECASE_TL = true ]
then
echo "TRUECASING TL"
perl "$RECASER_DIR/truecase.perl" --model "tc.$TL" < "$ROOTNAME.tok.clean.$TL" > "$ROOTNAME.true.$TL"
fi
if [ $SPLIT_NUMBERS_SL = true  ] 
then
echo "SPLITTING NUMBERS SL"
cat "$ROOTNAME.true.$SL" | python3 "$MTUOC/MTUOC_splitnumbers.py" > "$ROOTNAME.split.$SL"
fi
if [ $SPLIT_NUMBERS_TL = true  ] 
then
echo "SPLITTING NUMBERS TL"
cat "$ROOTNAME.true.$TL" | python3 "$MTUOC/MTUOC_splitnumbers.py" > "$ROOTNAME.split.$TL"
fi
if [ $REPLACE_NUMBERS_SL = true  ] 
then
echo "REPLACE NUMBERS SL"
cat "$ROOTNAME.true.$SL" | python3 "$MTUOC/MTUOC_replacenumbers.py" > "$ROOTNAME.num.$SL"
fi
if [ $REPLACE_NUMBERS_TL = true  ] 
then
echo "REPLACE NUMBERS TL"
cat "$ROOTNAME.true.$TL" | python3 "$MTUOC/MTUOC_replacenumbers.py" > "$ROOTNAME.num.$TL"
fi

if [ $LEARN_BPE = true  ] 
then
    echo "LEARNING BPE"
    if [ $JOIN_LANGUAGES = true  ] 
    then
    echo "JOINING LANGUAGES"
    subword-nmt learn-joint-bpe-and-vocab --input "$ROOTNAME.split.$SL" "$ROOTNAME.split.$TL" -s 85000 -o codes_file --write-vocabulary "vocab_BPE.$SL" "vocab_BPE.$TL"
    else
        if [ $PROCESS_SL = true ]
        then
        echo "SL"
        subword-nmt learn-joint-bpe-and-vocab --input "$ROOTNAME.split.$SL" -s 85000 -o "codes_file.$SL" --write-vocabulary "vocab_BPE.$SL"
        fi
        if [ $PROCESS_TL = true ]
        then
        echo "TL"
        subword-nmt learn-joint-bpe-and-vocab --input "$ROOTNAME.split.$TL" -s 85000 -o "codes_file.$TL" --write-vocabulary "vocab_BPE.$TL"
        fi
    fi
fi

if [ $APPLY_BPE = true  ] 
then
echo "APPLYING BPE"
    if [ $JOIN_LANGUAGES = true ]
    then
    BPESL="codes_file"
    BPETL="codes_file"
    fi
    if [ $JOIN_LANGUAGES = false ]
    then
    BPESL="codes_file.$SL"
    BPETL="codes_file.$TL"
    fi
    if [ $BPE_DROPOUT = false ]
    then
    echo "NO BPE DROPOUT"
    echo "SL using $BPESL"
    subword-nmt apply-bpe -c codes_file --vocabulary "vocab_BPE.$SL"  --vocabulary-threshold $VOCABULARY_THRESHOLD < "$ROOTNAME.split.$SL" > "$ROOTNAME.BPE.$SL"
    echo "TL using $BPETL"
    subword-nmt apply-bpe -c codes_file --vocabulary "vocab_BPE.$TL"  --vocabulary-threshold $VOCABULARY_THRESHOLD < "$ROOTNAME.split.$TL" > "$ROOTNAME.BPE.$TL"
    fi
    if [ $BPE_DROPOUT = true ]
    then
    echo "BPE DROPOUT P= $BPE_DROPOUT_P"
    echo "SL using $BPESL"
    subword-nmt apply-bpe -c codes_file --vocabulary "vocab_BPE.$SL"  --vocabulary-threshold $VOCABULARY_THRESHOLD --dropout "$BPE_DROPOUT_P" < "$ROOTNAME.split.$SL" > "$ROOTNAME.BPE.$SL"
    echo "TL using $BPETL"
    subword-nmt apply-bpe -c codes_file --vocabulary "vocab_BPE.$TL"  --vocabulary-threshold $VOCABULARY_THRESHOLD --dropout "$BPE_DROPOUT_P" < "$ROOTNAME.split.$TL" > "$ROOTNAME.BPE.$TL"
    fi
fi


if [ $SPLIT_CORPUS = true  ] 
then
echo "SPLITTING CORPUS"
    if [ $SPLIT_SPLITTED = true ]
    then
    NUMOFLINES=$(cat "$ROOTNAME.split.$SL" | wc -l )
    NLTRAIN=$((NUMOFLINES - lval -leval))
    python3 "$MTUOC/MTUOC_split_corpus.py"  "$ROOTNAME.split.$SL"  "train.split.$SL" $NLTRAIN  "val.split.$SL" $lval  "eval.split.$SL" $leval
    python3 "$MTUOC/MTUOC_split_corpus.py"  "$ROOTNAME.split.$TL"  "train.split.$TL" $NLTRAIN  "val.split.$TL" $lval  "eval.split.$TL" $leval
    fi
    if [ $SPLIT_NUM = true ]
    then
    NUMOFLINES=$(cat "$ROOTNAME.num.$SL" | wc -l )
    NLTRAIN=$((NUMOFLINES - lval -leval))
    python3 "$MTUOC/MTUOC_split_corpus.py"  "$ROOTNAME.num.$SL"  "train.num.$SL" $NLTRAIN  "val.num.$SL" $lval  "eval.num.$SL" $leval
    python3 "$MTUOC/MTUOC_split_corpus.py"  "$ROOTNAME.num.$TL"  "train.num.$TL" $NLTRAIN  "val.num.$TL" $lval  "eval.num.$TL" $leval
    fi
    if [ $SPLIT_BPE = true ]
    then
    NUMOFLINES=$(cat "$ROOTNAME.BPE.$SL" | wc -l )
    NLTRAIN=$((NUMOFLINES - lval -leval))
    python3 "$MTUOC/MTUOC_split_corpus.py"  "$ROOTNAME.BPE.$SL"  "train.BPE.$SL" $NLTRAIN  "val.BPE.$SL" $lval  "eval.BPE.$SL" $leval
    python3 "$MTUOC/MTUOC_split_corpus.py"  "$ROOTNAME.BPE.$TL"  "train.BPE.$TL" $NLTRAIN  "val.BPE.$TL" $lval  "eval.BPE.$TL" $leval
    
    cat "train.BPE.$SL" | python3 "$MTUOC/MTUOC_BPE.py" deapply | perl "$MOSESDECODER_DIR/scripts/tokenizer/detokenizer.perl" "-l $SL" | perl  "$MOSESDECODER_DIR/scripts/recaser/detruecase.perl" > "train.$SL"
    cat "train.BPE.$TL" | python3 "$MTUOC/MTUOC_BPE.py" deapply | perl "$MOSESDECODER_DIR/scripts/tokenizer/detokenizer.perl" "-l $TL" | perl  "$MOSESDECODER_DIR/scripts/recaser/detruecase.perl" > "train.$TL"
    
    cat "val.BPE.$SL" | python3 "$MTUOC/MTUOC_BPE.py" deapply | perl "$MOSESDECODER_DIR/scripts/tokenizer/detokenizer.perl" "-l $SL" | perl  "$MOSESDECODER_DIR/scripts/recaser/detruecase.perl" > "val.$SL"
    cat "val.BPE.$TL" | python3 "$MTUOC/MTUOC_BPE.py" deapply | perl "$MOSESDECODER_DIR/scripts/tokenizer/detokenizer.perl" "-l $TL" | perl  "$MOSESDECODER_DIR/scripts/recaser/detruecase.perl" > "val.$TL"
    
    cat "eval.BPE.$SL" | python3 "$MTUOC/MTUOC_BPE.py" deapply | perl "$MOSESDECODER_DIR/scripts/tokenizer/detokenizer.perl" "-l $SL" | perl  "$MOSESDECODER_DIR/scripts/recaser/detruecase.perl" > "eval.$SL"
    cat "eval.BPE.$TL" | python3 "$MTUOC/MTUOC_BPE.py" deapply | perl "$MOSESDECODER_DIR/scripts/tokenizer/detokenizer.perl" "-l $TL" | perl  "$MOSESDECODER_DIR/scripts/recaser/detruecase.perl" > "eval.$TL"
    
    
    fi
fi

#REMOVING TEMPORAL FILES

echo "REMOVING TEMPORAL FILES" 

if [ $DELETE_TOK = true  ] 
then
rm *.tok.*
fi

if [ $DELETE_TRUE = true  ] 
then
rm *.true.*
fi

if [ $DELETE_SPLIT = true  ] 
then
rm *.split.*
fi

if [ $DELETE_NUM = true  ] 
then
rm *.num.*
fi
