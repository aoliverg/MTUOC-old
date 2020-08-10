#    MTUOC_detruecaser
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
import codecs
import pickle



def detruecase(line):
    tokens=line.split(" ")
    new=[]
    yet=False
    for token in tokens:
        if not yet and token.isalpha():
            yet=True
            new.append(token[0].upper()+token[1:])
        else:
            new.append(token)
    line=" ".join(new)
    return(line)
    
def print_help():
    print("MTUOC Truecaser: detruecases a text. It simply writes the first letter of the sentence in Upper Case")
    print("      python3 MTUOC_detruecaser.py < corpus.true > corpus.detrue")
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv)>1:
        if sys.argv[1]=="-h" or sys.argv[1]=="--help":
            print_help()
    for line in sys.stdin:
        line=line.strip()
        reline=detruecase(line)
        print(reline)
    
