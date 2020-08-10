import sys
import unicodedata
import html


def normalize(segment):
    segment=segment.replace("’","'")
    segment=segment.replace('“','"')
    segment=segment.replace('”','"')
    segment=segment.replace("«",'"')
    segment=segment.replace("»",'"')
    segment=html.unescape(segment)
    segment = unicodedata.normalize('NFC', segment)
    return(segment)
    
    
if __name__ == "__main__":
    for line in sys.stdin:
        line=line.strip()
        line=normalize(line)
        print(line)
        
