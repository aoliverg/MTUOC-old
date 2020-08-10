#    MTUOC_desplitnumbers.py
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

import pyonmttok
import re
import sys

re_num = re.compile(r'[\d,.\-/]+')
re_num_tl = re.compile(r'(([\d,.\-/]\s?)+)')


if __name__ == "__main__":
    tokenizer = pyonmttok.Tokenizer("aggressive", joiner_annotate=True, segment_numbers=True)
    for line in sys.stdin:
        output=tokenizer.detokenize(line.split(" "))
        print(output)
        
        

    

