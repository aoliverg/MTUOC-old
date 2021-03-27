import zipfile, urllib.request, shutil
import sys
import os
import argparse
import codecs


parser = argparse.ArgumentParser(description='MTUOC program for downloading Machine Translation Engines.')
parser.add_argument('-e','--engine', action="store", dest="engine", help='The name of the engine to download',required=False)
parser.add_argument('-l','--list', action='store_true', default=False, dest='listEngines',help='List the available engines.',required=False)

args = parser.parse_args()

if args.listEngines:
    url="http://lpg.uoc.edu/MTUOC/enginelist.txt"
    with urllib.request.urlopen(url) as response, open("enginelist.txt", 'wb') as out_file:
        shutil.copyfileobj(response, out_file)
        out_file.close()
        entrada=codecs.open("enginelist.txt","r",encoding="utf-8")
        lines=entrada.readlines()
        for line in lines:
            print(line.rstrip())
        os.remove("enginelist.txt")
        
elif args.engine:
    try:
        engine=args.engine
        url="http://lpg.uoc.edu/MTUOC/"+engine+".zip"
        file_name = engine+".zip"

        print("Downloading ",url)
        with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            with zipfile.ZipFile(file_name) as zf:
                zf.extractall()

        os.remove(file_name)
        try:
            path="./"+engine+"/marian*"
        except:
            pass
        try:
            path="./"+engine+"/moses"
        except:
            pass    
            
        print("Changing permissions to ",path)
        os.chmod(path, 111)
    except:
        print("Some error occurred: check the integrity of the engine "+engine,sys.exc_info()[0])
