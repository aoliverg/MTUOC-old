#    MTUOC_desplitnumbers.py
#    Copyright (C) 2021  Antoni Oliver
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

import re
import sys


def desplitnumbers(line, joiner="@@"):
    re_desplit=re.compile("("+joiner+" )|("+joiner+" ?$)")
    #sed -r 's/(@@ )|(@@ ?$)//g'
    line=re.sub(re_desplit,"",line)
    return(line)

if __name__ == "__main__":
    for line in sys.stdin:
        output=desplitnumbers(line)
        print(output)
        
        

    

