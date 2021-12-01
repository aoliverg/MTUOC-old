#    MTUOC-TMXdetectlanguages
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

import argparse
import lxml.etree as ET
import sys
import codecs



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MTUOC program for detecting the language codes of a TMX file.')
    parser.add_argument('-i','--in', action="store", dest="inputfile", help='The input TMX file.',required=True)
    args = parser.parse_args()
    fentrada=args.inputfile

    parser = ET.XMLParser(recover=True)
    tree = ET.parse(fentrada, parser=parser)
    root = tree.getroot()

    langs={}
    for tu in root.iter('tu'):
        sl_text=""
        tl_text=""
        for tuv in tu.iter('tuv'):
            lang=tuv.attrib['{http://www.w3.org/XML/1998/namespace}lang']
            langs[lang]=1
            
    for l in langs:
        print(l)
