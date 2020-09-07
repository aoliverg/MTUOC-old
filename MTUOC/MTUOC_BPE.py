#    MTUOC_BPE
#    Copyright (C) 2020 Antoni Oliver
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

from subword_nmt import apply_bpe
import sys
import re

def load_codes(codes):
    bpeobject=apply_bpe.BPE(open(codes,encoding="utf-8"))
    return(bpeobject)

def apply_BPE(bpeobject,segment):
    segmentBPE=bpeobject.process_line(segment)
    return(segmentBPE)
    
def deapply_BPE(segment):
    segment=re.sub(r'(@@ )|(@@ ?$)', '', segment)
    return(segment)
    
def print_help():
    print("MTUOC BPE: applies or deapplies BPE subwords in a corpus.")
    print("Apply BPE: ")
    print("      python3 MTUOC_BPE.py apply codes_file < corpus > corpus.BPE")
    print("De-apply BPE: ")
    print("      python3 MTUOC_BPE.py deapply < corpus > corpus.BPE")
    sys.exit()

if __name__ == "__main__":
    if sys.argv[1]=="-h" or sys.argv[1]=="--help":
        print_help()
    action=sys.argv[1]
    if action=="apply":
        codesfile=sys.argv[2]
        bpeobject=load_codes(codesfile)
        

    for line in sys.stdin:
        if action=="apply":
            line2=apply_BPE(bpeobject,line)
            print(line2.rstrip())
        elif action=="deapply":
            line2=deapply_BPE(line)
            print(line2.rstrip())
