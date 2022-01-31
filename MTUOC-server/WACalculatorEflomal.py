#!/usr/bin/env python3

from eflomal import read_text, write_text, align

import sys, argparse, random, os, io
from tempfile import NamedTemporaryFile

import pickle
import codecs


class WACalculatorEflomal():
    def __init__(self):
        self.model_prefix=""
        
    def load_model(self,model_prefix):
        if not model_prefix=="":
            priors_list_name=model_prefix+"-priors_list.pkl"
        else:
            priors_list_name="priors_list.pkl"
            
        if not model_prefix=="":
            ferf_priors_name=model_prefix+"-ferf_priors.pkl"
        else:
            ferf_priors_name="ferf_priors.pkl"
            
        if not model_prefix=="":
            ferr_priors_name=model_prefix+"-ferr_priors.pkl"
        else:
            ferr_priors_name="ferr_priors.pkl"
            
        if not model_prefix=="":
            hmmf_priors_name=model_prefix+"-hmmf_priors.pkl"
        else:
            hmmf_priors_name="hmmf_priors.pkl"
            
        if not model_prefix=="":
            hmmr_priors_name=model_prefix+"-hmmr_priors.pkl"
        else:
            hmmr_priors_name="hmmr_priors.pkl"
                
        with open(priors_list_name, 'rb') as f:
            self.priors_list = pickle.load(f)
        with open(ferf_priors_name, 'rb') as f:
            self.ferf_priors = pickle.load(f)
        with open(ferr_priors_name, 'rb') as f:
            self.ferr_priors = pickle.load(f)
        with open(hmmf_priors_name, 'rb') as f:
            self.hmmf_priors = pickle.load(f)
        with open(hmmr_priors_name, 'rb') as f:
            self.hmmr_priors = pickle.load(f)


    def getWordAlignments(self,SLsegment,TLsegment):
        
        stemp=codecs.open("tempSL.txt","w",encoding="utf-8")
        stemp.write(SLsegment)
        stemp.close()
        
        ttemp=codecs.open("tempTL.txt","w",encoding="utf-8")
        ttemp.write(TLsegment)
        ttemp.close()
        
        with open("tempSL.txt", 'r', encoding='utf-8') as f:
            src_sents, src_index = read_text(
                    f, True, 0, 0)
            n_src_sents = len(src_sents)
            src_voc_size = len(src_index)
            srcf = NamedTemporaryFile('wb')
            write_text(srcf, tuple(src_sents), src_voc_size)
            src_sents = None

            
        with open("tempTL.txt", 'r', encoding='utf-8') as f:
            trg_sents, trg_index = read_text(
                    f, True, 0, 0)
            trg_voc_size = len(trg_index)
            n_trg_sents = len(trg_sents)
            trgf = NamedTemporaryFile('wb')
            write_text(trgf, tuple(trg_sents), trg_voc_size)
            trg_sents = None

        if n_src_sents != n_trg_sents:
            print('ERROR: number of sentences differ in input files (%d vs %d)' % (
                    n_src_sents, n_trg_sents),
                  file=sys.stderr, flush=True)
            sys.exit(1)

        def get_src_index(src_word):
            src_word = src_word.lower()
            
            e = src_index.get(src_word)
            if e is not None:
                e = e + 1
            return e

        def get_trg_index(trg_word):
            trg_word = trg_word.lower()
            
            f = trg_index.get(trg_word)
            if f is not None:
                f = f + 1
            return f


        
        priors_indexed = {}
        for src_word, trg_word, alpha in self.priors_list:
            if src_word == '<NULL>':
                e = 0
            else:
                e = get_src_index(src_word)

            if trg_word == '<NULL>':
                f = 0
            else:
                f = get_trg_index(trg_word)

            if (e is not None) and (f is not None):
                priors_indexed[(e,f)] = priors_indexed.get((e,f), 0.0) \
                        + alpha

        ferf_indexed = {}
        for src_word, fert, alpha in self.ferf_priors:
            e = get_src_index(src_word)
            if e is not None:
                ferf_indexed[(e, fert)] = \
                        ferf_indexed.get((e, fert), 0.0) + alpha

        ferr_indexed = {}
        for trg_word, fert, alpha in self.ferr_priors:
            f = get_trg_index(trg_word)
            if f is not None:
                ferr_indexed[(f, fert)] = \
                        ferr_indexed.get((f, fert), 0.0) + alpha

        
        priorsf = NamedTemporaryFile('w', encoding='utf-8')
        print('%d %d %d %d %d %d %d' % (
            len(src_index)+1, len(trg_index)+1, len(priors_indexed),
            len(self.hmmf_priors), len(self.hmmr_priors),
            len(ferf_indexed), len(ferr_indexed)),
            file=priorsf)

        for (e, f), alpha in sorted(priors_indexed.items()):
            print('%d %d %g' % (e, f, alpha), file=priorsf)

        for jump, alpha in sorted(self.hmmf_priors.items()):
            print('%d %g' % (jump, alpha), file=priorsf)

        for jump, alpha in sorted(self.hmmr_priors.items()):
            print('%d %g' % (jump, alpha), file=priorsf)

        for (e, fert), alpha in sorted(ferf_indexed.items()):
            print('%d %d %g' % (e, fert, alpha), file=priorsf)

        for (f, fert), alpha in sorted(ferr_indexed.items()):
            print('%d %d %g' % (f, fert, alpha), file=priorsf)

        priorsf.flush()

        trg_index = None
        src_index = None


        iters = (None, None, None)
        if any(x is None for x in iters[:3]):
            iters = None

        

        align(srcf.name, trgf.name,
              links_filename_fwd="tempALI.fwd",
              links_filename_rev="tempALI.rev",
              statistics_filename=None,
              scores_filename_fwd="tempSCO.fwd",
              scores_filename_rev="tempSCO.rev",
              priors_filename=priorsf.name,
              model=3,
              score_model=0,
              n_iterations=iters,
              n_samplers=3,
              quiet=True,
              rel_iterations=1.0,
              null_prior=0.2,
              use_gdb=False)

        srcf.close()
        trgf.close()
        
        alitemp=codecs.open("tempALI.fwd","r",encoding="utf-8")
        alineament=alitemp.readline().rstrip()
        return(alineament)
        
    
'''
def getWordAlignments(SLsegment,TLsegment,model_prefix=""):
    stemp=codecs.open("tempSL.txt","w",encoding="utf-8")
    stemp.write(SLsegment)
    stemp.close()
    
    ttemp=codecs.open("tempTL.txt","w",encoding="utf-8")
    ttemp.write(TLsegment)
    ttemp.close()
    
    
    if not model_prefix=="":
        priors_list_name=model_prefix+"-priors_list.pkl"
    else:
        priors_list_name="priors_list.pkl"
        
    if not model_prefix=="":
        ferf_priors_name=model_prefix+"-ferf_priors.pkl"
    else:
        ferf_priors_name="ferf_priors.pkl"
        
    if not model_prefix=="":
        ferr_priors_name=model_prefix+"-ferr_priors.pkl"
    else:
        ferr_priors_name="ferr_priors.pkl"
        
    if not model_prefix=="":
        hmmf_priors_name=model_prefix+"-hmmf_priors.pkl"
    else:
        hmmf_priors_name="hmmf_priors.pkl"
        
    if not model_prefix=="":
        hmmr_priors_name=model_prefix+"-hmmr_priors.pkl"
    else:
        hmmr_priors_name="hmmr_priors.pkl"
            
    with open(priors_list_name, 'rb') as f:
        priors_list = pickle.load(f)
    with open(ferf_priors_name, 'rb') as f:
        ferf_priors = pickle.load(f)
    with open(ferr_priors_name, 'rb') as f:
        ferr_priors = pickle.load(f)
    with open(hmmf_priors_name, 'rb') as f:
        hmmf_priors = pickle.load(f)
    with open(hmmr_priors_name, 'rb') as f:
        hmmr_priors = pickle.load(f)
        
    with open("tempSL.txt", 'r', encoding='utf-8') as f:
        src_sents, src_index = read_text(
                f, True, 0, 0)
        n_src_sents = len(src_sents)
        src_voc_size = len(src_index)
        srcf = NamedTemporaryFile('wb')
        write_text(srcf, tuple(src_sents), src_voc_size)
        src_sents = None

        
    with open("tempTL.txt", 'r', encoding='utf-8') as f:
        trg_sents, trg_index = read_text(
                f, True, 0, 0)
        trg_voc_size = len(trg_index)
        n_trg_sents = len(trg_sents)
        trgf = NamedTemporaryFile('wb')
        write_text(trgf, tuple(trg_sents), trg_voc_size)
        trg_sents = None

    if n_src_sents != n_trg_sents:
        print('ERROR: number of sentences differ in input files (%d vs %d)' % (
                n_src_sents, n_trg_sents),
              file=sys.stderr, flush=True)
        sys.exit(1)

    def get_src_index(src_word):
        src_word = src_word.lower()
        
        e = src_index.get(src_word)
        if e is not None:
            e = e + 1
        return e

    def get_trg_index(trg_word):
        trg_word = trg_word.lower()
        
        f = trg_index.get(trg_word)
        if f is not None:
            f = f + 1
        return f


    
    priors_indexed = {}
    for src_word, trg_word, alpha in priors_list:
        if src_word == '<NULL>':
            e = 0
        else:
            e = get_src_index(src_word)

        if trg_word == '<NULL>':
            f = 0
        else:
            f = get_trg_index(trg_word)

        if (e is not None) and (f is not None):
            priors_indexed[(e,f)] = priors_indexed.get((e,f), 0.0) \
                    + alpha

    ferf_indexed = {}
    for src_word, fert, alpha in ferf_priors:
        e = get_src_index(src_word)
        if e is not None:
            ferf_indexed[(e, fert)] = \
                    ferf_indexed.get((e, fert), 0.0) + alpha

    ferr_indexed = {}
    for trg_word, fert, alpha in ferr_priors:
        f = get_trg_index(trg_word)
        if f is not None:
            ferr_indexed[(f, fert)] = \
                    ferr_indexed.get((f, fert), 0.0) + alpha

    
    priorsf = NamedTemporaryFile('w', encoding='utf-8')
    print('%d %d %d %d %d %d %d' % (
        len(src_index)+1, len(trg_index)+1, len(priors_indexed),
        len(hmmf_priors), len(hmmr_priors),
        len(ferf_indexed), len(ferr_indexed)),
        file=priorsf)

    for (e, f), alpha in sorted(priors_indexed.items()):
        print('%d %d %g' % (e, f, alpha), file=priorsf)

    for jump, alpha in sorted(hmmf_priors.items()):
        print('%d %g' % (jump, alpha), file=priorsf)

    for jump, alpha in sorted(hmmr_priors.items()):
        print('%d %g' % (jump, alpha), file=priorsf)

    for (e, fert), alpha in sorted(ferf_indexed.items()):
        print('%d %d %g' % (e, fert, alpha), file=priorsf)

    for (f, fert), alpha in sorted(ferr_indexed.items()):
        print('%d %d %g' % (f, fert, alpha), file=priorsf)

    priorsf.flush()

    trg_index = None
    src_index = None


    iters = (None, None, None)
    if any(x is None for x in iters[:3]):
        iters = None

    

    align(srcf.name, trgf.name,
          links_filename_fwd="tempALI.fwd",
          links_filename_rev="tempALI.rev",
          statistics_filename=None,
          scores_filename_fwd="tempSCO.fwd",
          scores_filename_rev="tempSCO.rev",
          priors_filename=priorsf.name,
          model=3,
          score_model=0,
          n_iterations=iters,
          n_samplers=3,
          quiet=True,
          rel_iterations=1.0,
          null_prior=0.2,
          use_gdb=False)

    srcf.close()
    trgf.close()
    
    alitemp=codecs.open("tempALI.fwd","r",encoding="utf-8")
    alineament=alitemp.readline().rstrip()
    return(alineament)
'''    


