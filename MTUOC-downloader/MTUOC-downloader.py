import zipfile, urllib.request, shutil
import sys
import os
import os.path
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

        with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            with zipfile.ZipFile(file_name) as zf:
                zf.extractall()

        os.remove(file_name)
        path="./"+engine+"/marian-server"
        if os.path.isfile(path):
            print("Changing permissions to marian-server.")
            try:
                
                os.chmod(path, 111)
            except:
                print("Error changing permissions to marian-server. Change permissions manually:")
                print("chmod +x marian-server")
            else:
                print("Successfully changed permissions of marian-server")
        path="./"+engine+"/moses"
        if os.path.isfile(path):
            try:
                path="./"+engine+"/moses"
                os.chmod(path, 111)
            except:
                print("Error changing permissions to moses. Change permissions manually:")
                print("chmod +x moses")   
            else:
                print("Successfully changed permissions of moses")
        
    except:
        print("Some error occurred: check the integrity of the engine: "+engine)
        print("Please, report this error: ", sys.exc_info())
