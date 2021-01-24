#    MTUOC-TMXdetectlanguages
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

import argparse
import lxml.etree as ET
import sys
import codecs
import os



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MTUOC program for converting a TMX into a tab text.')
    parser.add_argument('-d','--dir', action="store", dest="inputdir", help='The input directory where the TMX files are located.',required=True)
    args = parser.parse_args()
    direntrada=args.inputdir
    langs={}
    parser = ET.XMLParser(recover=True)
    for root, dirs, files in os.walk(direntrada):
        for file in files:
            try:
                print(file)
                if file.endswith(".tmx"):
                    fentrada=os.path.join(root, file)
                    print(fentrada)
                    
                    tree = ET.parse(fentrada, parser=parser)
                    rootT = tree.getroot()

                    for tu in rootT.iter('tu'):
                        sl_text=""
                        tl_text=""
                        for tuv in tu.iter('tuv'):
                            lang=tuv.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                            langs[lang]=1

            except:
                print("ERROR in ",file,sys.exc_info())
                        
    for l in langs:
        print(l)
