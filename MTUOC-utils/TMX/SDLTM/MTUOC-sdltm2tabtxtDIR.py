import sys
import sqlite3
import xml.etree.ElementTree as etree
import codecs
import os
import argparse

import html
import re

def lreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % pattern, sub, string)

def rreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' ends 'string'.
    """
    return re.sub('%s$' % pattern, sub, string)
    
def FT2ST(segment):
    segmenttagsimple=segment
    segmenttagsimple=re.sub('(<[^>]+?/>)', "<t/>",segmenttagsimple)
    segmenttagsimple=re.sub('(</[^>]+?>)', "</t>",segmenttagsimple)
    segmenttagsimple=re.sub('(<[^/>]+?>)', "<t>",segmenttagsimple)
    return(segmenttagsimple)
    
def FT2NT(segment):
    segmentnotags=re.sub('(<[^>]+>)', " ",segment)
    segmentnotags=' '.join(segmentnotags.split()).strip()
    return(segmentnotags)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MTUOC program for converting all the SDLTM in a given directory into a tab text.')
    parser.add_argument('-d','--dir', action="store", dest="inputdir", help='The input directory where the SDLTM files are located.',required=True)
    parser.add_argument('-o','--out', action="store", dest="outputfile", help='The output text file.',required=True)    
    parser.add_argument('--noTags', action='store_true', default=False, dest='noTags',help='Removes the internal tags.')
    parser.add_argument('--simpleTags', action='store_true', default=False, dest='simpleTags',help='Replaces tags with <t>, </t> or <t/>.')
    parser.add_argument('--noEntities', action='store_true', default=False, dest='noEntities',help='Replaces html/xml entities by corresponding characters.')

args = parser.parse_args()
directory=args.inputdir
fsortida=args.outputfile
sortida=codecs.open(fsortida,"w",encoding="utf-8")


for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith(".sdltm"):
            try:
                sdltmfile=os.path.join(root, "", file)
                print(sdltmfile)
                conn=sqlite3.connect(sdltmfile)
                cur = conn.cursor() 
                cur.execute('select source_segment,target_segment from translation_units;')
                data=cur.fetchall()
                for d in data:
                    ssxml=d[0]
                    tsxml=d[1]
                    try:
                        rootSL = etree.fromstring(ssxml)
                        for text in rootSL.iter('Value'):
                            sltext="".join(text.itertext()).replace("\n"," ")
                        rootTL = etree.fromstring(tsxml)
                        for text in rootTL.iter('Value'):
                            tltext="".join(text.itertext()).replace("\n"," ")
                        if not sltext=="" and not tltext=="":
                            if args.noEntities:
                                sltext=html.unescape(sltext)
                                tltext=html.unescape(tltext)
                            if args.simpleTags:
                                sltext=FT2ST(sltext)
                                tltext=FT2ST(tltext)
                            if args.noTags:
                                sltext=FT2NT(sltext)
                                tltext=FT2NT(tltext)
                            cadena=sltext+"\t"+tltext
                            print(cadena)
                            sortida.write(cadena+"\n")
                    except:
                        print("ERROR")
            except:
                pass
               
sortida.close()