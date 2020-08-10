#    MTUOC_combine_tcmodels
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

arguments=sys.argv

if len(arguments)==1 or arguments[1]=="-h" or arguments[1]=="-h" or arguments[1]=="--help":
    print("MTUOC_combine_tcmodels: a programm to combine MTUOC truecasing models.")
    print("Usage: if you want to combine tc1.ll tc2.ll tc3.ll into tc.ll write:")
    print("python MTUOC_combine_tcmodels.py tc1.ll tc2.ll tc3.ll tc.ll")
    print("You can combine any number of models, the last one being the resulting model")
    sys.exit()

tcout=arguments[-1]
tcsin=arguments[1:-1]

tc_model_out = {}

for tcm in tcsin:
    tc_model = pickle.load(open(tcm, "rb" ) )
    for clau in tc_model:
        if not clau in tc_model_out:
            tc_model_out[clau]=tc_model[clau]
        else:
            for clau2 in tc_model[clau]:
                if not clau2 in tc_model_out[clau]:
                    tc_model_out[clau][clau2]=tc_model[clau][clau2]
                else:
                    tc_model_out[clau][clau2]=tc_model[clau][clau2]+tc_model_out[clau][clau2]




pickle.dump(tc_model_out, open(tcout, "wb"))
