#    MTUOC_prune_tc_model
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
import codecs
import pickle
import argparse
import importlib

def load_model(model):
    tc_model = pickle.load(open(model, "rb" ) )
    return(tc_model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MTUOC program for pruning a truecasing model.')
    parser.add_argument('-m','--model', action="store", dest="model", help='The truecasing model to prune.',required=True)
    parser.add_argument('-f',action="store", dest="minimum", help='The minimum frequency to keep an entry',required=False)
    
    
args = parser.parse_args()
model=args.model
tc_model=load_model(model)
minfreq=int(args.minimum)

tc2=tc_model.copy()

for clau in tc_model:
    fmin=0
    if tc_model[clau]["lc"]>fmin:fmin=tc_model[clau]["lc"]
    if tc_model[clau]["u1"]>fmin:fmin=tc_model[clau]["u1"]
    if tc_model[clau]["uc"]>fmin:fmin=tc_model[clau]["uc"]
    if fmin<minfreq:
        tc2.pop(clau)
        
pickle.dump(tc2, open(model, "wb"))
