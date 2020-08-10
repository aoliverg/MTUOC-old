#    MTUOC_restorenumbers
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
import re


def restore(segmentTL,segmentSL):
    trobatsEXPRNUM=re.finditer(re_num,segmentSL)
    for trobat in trobatsEXPRNUM:
        if not trobat.group(0) in [".",","]:
            segmentTL=segmentTL.replace("@NUM@",trobat.group(0),1)
    return(segmentTL)

re_num = re.compile(r'[\d,\./]+')        

def print_help():
    print("MTUOC Restore Numbers: restores the numeric expressions. Both original segment with numbers and target segment with $NUM$ are required.")
    print('      python3 MTUOC_restorenumbers.py "Esto cuesta @NUM@ dólares ." "This costs 100 dollars ."')
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv)>1:
        if sys.argv[1]=="-h" or sys.argv[1]=="--help":
            print_help()
    if len(sys.argv)>2:
        s1=sys.argv[1]
        s2=sys.argv[2]
        restored=restore(s1,s2)
        print(restored)
        
        
    
