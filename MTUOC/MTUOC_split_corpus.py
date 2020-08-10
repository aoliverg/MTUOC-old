#    MTUOC_split_corpus
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

import codecs
import sys

def split_corpus(aentrada,parametres):
    entrada=codecs.open(aentrada,"r",encoding="utf-8")
    nsortida=parametres.pop(0)
    limit=int(parametres.pop(0))
    print(nsortida,limit)
    sortida=codecs.open(nsortida,"w",encoding="utf-8")
    cont=0
    while 1:
        cont+=1
        linia=entrada.readline()
        linia=linia.rstrip()
        sortida.write(linia+"\n")
        if cont>=limit:
            if len(parametres)==0:
                break
            nsortida=parametres.pop(0)
            limit=int(parametres.pop(0))
            print(nsortida,limit)
            sortida.close()
            sortida=codecs.open(nsortida,"w",encoding="utf-8")
            cont=0
        
    sortida.close()

def print_help():
    print("MTUOC Split Corpus: split a corpus in n parts. Typical use: divide a corpus in train, val and eval.")
    print("Parameters: corpus part_1 size_1 part_2 size_2 .... part_n size_n")
    print("      python3 MTUOC_split_corpus corpus train 550134 val 1000 eval 1000")
    sys.exit()

if __name__ == "__main__":

    if sys.argv[1]=="-h" or sys.argv[1]=="--help":
        print_help()

    aentrada=sys.argv[1]
    parametres=sys.argv[2:]
    print(parametres)
    split_corpus(aentrada,parametres)
