#    MTUOC_replacenumbers
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

re_num = re.compile(r'[\d,\./]+')      
    
def replace(segment):
    trobatsEXPRNUM=re.finditer(re_num,segment)
    for trobat in trobatsEXPRNUM:
        if not trobat.group(0) in [".",","]:
            segment=segment.replace(trobat.group(0),"@NUM@",1)
    return(segment)

  

def print_help():
    print("MTUOC Replace Numbers: replaces numeric expressions with @NUM@.")
    print("      python3 MTUOC_replacenumbers.py < corpus > corpus.split")
    sys.exit()

if __name__ == "__main__":
    if len(sys.argv)>1:
        if sys.argv[1]=="-h" or sys.argv[1]=="--help":
            print_help()
    for line in sys.stdin:
        line=line.strip()
        line2=replace(line)
        print(line2)
        
        
    
