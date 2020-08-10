#    MTUOC_combine_corpus
#    Copyright (C) 2020  Antoni Oliver
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
import os
import codecs
import kenlm
from nltk.probability import FreqDist
import subprocess 


def combine_corpus(MTUOC, CALLPATH, SL, TL, SPE_corpus, GEN_corpus, GEN_selected, GEN_selected_segments):
    print("COMBINING CORPORA...")
    print(MTUOC, CALLPATH, SL, TL, SPE_corpus, GEN_corpus, GEN_selected, GEN_selected_segments)
    print(type(GEN_selected_segments))
    #SL SPE corpus language model calculation

    print("STEP 1. Language Model Calculation")
    kenlmmodel= "lm.arpa."+SL


    command=MTUOC+"/lmplz -o 5 --skip_symbols --discount_fallback < "+CALLPATH+"/"+SPE_corpus+"."+SL+" > "+CALLPATH+"/"+kenlmmodel
    #command=MTUOC+"/lmplz -o 5 --skip_symbols --discount_fallback <"+SPE_corpus+"."+SL+" >"+kenlmmodel
    print("*******************************")
    print(command)
    print("*******************************")
    os.system(command)
    #print(command.split(" "))
    #subprocess.run(command.split(" "))


    #Scores calculation
    print("STEP 2. Scores calculation")
    nentrada=GEN_corpus+"."+SL
    entrada=codecs.open(nentrada,"r",encoding="utf-8")
    sortida=codecs.open("scores.tmp","w",encoding="utf-8")
    model = kenlm.Model(kenlmmodel)
    for linia in entrada:
        linia=linia.rstrip()
        perplexity=model.perplexity(linia)
        invperplexity=1/perplexity
        sortida.write(str(invperplexity)+"\n")
        
    #Creation of selection file
    print("STEP 3. Creation of the selection file")
    entrada=codecs.open("scores.tmp","r",encoding="utf-8")
    sortida=codecs.open("selection.tmp","w",encoding="utf-8")
    fdist = FreqDist()
    cont=0
    for linia in entrada:
        linia=float(linia.rstrip())
        fdist[cont]=linia
        cont+=1


    for element in fdist.most_common(GEN_selected_segments):
        cadena=str(element[0])+"\t"+str(element[1])
        sortida.write(cadena+"\n")
        
    #Selection from LM
    print("STEP 4. Selection from LM")
    entrada=codecs.open("selection.tmp","r",encoding="utf-8")

    select={}

    for linia in entrada:
        linia=linia.rstrip()
        camps=linia.split("\t")
        select[camps[0]]=camps[1]
    nl1if=GEN_corpus+"."+SL
    nl2if=GEN_corpus+"."+TL
    l1if=codecs.open(nl1if,"r",encoding="utf-8")
    l2if=codecs.open(nl2if,"r",encoding="utf-8")

    nl1of=GEN_selected+"."+SL
    nl2of=GEN_selected+"."+TL
    l1of=codecs.open(nl1of,"w",encoding="utf-8")
    l2of=codecs.open(nl2of,"w",encoding="utf-8")
    cont=0
    while 1:
        linial1=l1if.readline()
        if not linial1:
            break
        linial2=l2if.readline()
        if str(cont) in select:
            detoken_m_linia1=linial1.replace("￭","")
            detoken_m_linia2=linial2.replace("￭","")
            l1of.write(detoken_m_linia1)
            l2of.write(detoken_m_linia2)
        cont+=1
        
    print("STEP 5. Deleting temporal files")
    os.remove("scores.tmp")
    os.remove("selection.tmp")

if __name__ == "__main__":

    MTUOC=sys.argv[1]
    CALLPATH=sys.argv[2]
    #source and target languages
    SL=sys.argv[3]
    TL=sys.argv[4]

    #corpus (should be preprocessed up to split numbers)

    SPE_corpus=sys.argv[5]
    GEN_corpus=sys.argv[6]
    GEN_selected=sys.argv[7]
    GEN_selected_segments=int(sys.argv[8])

    combine_corpus(MTUOC, CALLPATH, SL, TL, SPE_corpus, GEN_corpus, GEN_selected, GEN_selected_segments)


