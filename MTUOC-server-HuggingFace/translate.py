#adapted from https://towardsdatascience.com/build-your-own-machine-translation-service-with-transformers-d0709df0791b
from transformers import MarianTokenizer, MarianMTModel
import os
from typing import List
import torch
import sys

class Translator():
    def __init__(self, models_dir,SL,TL, GPU=False):
        self.models = {}
        self.models_dir = models_dir
        self.SL=SL
        self.TL=TL
        self.GPU=GPU
        route = f'{self.SL}-{self.TL}'
        success_code, message = self.load_model(route)
        

    def load_model(self, route):
        if torch.cuda.is_available() and self.GPU:            
          dev = "cuda:0"
        else:  
          dev = "cpu" 
        self.device = torch.device(dev)
        model = f'opus-mt-{route}'
        path = os.path.join(self.models_dir,model)
        try:
            self.model = MarianMTModel.from_pretrained(path).to(self.device)
            
        except:
            print("ERROR MODEL",sys.exc_info())
        try:
            self.tok = MarianTokenizer.from_pretrained(path)
        except:
            print("ERROR TOK",sys.exc_info())

        return 1,f"Successfully loaded model for {route} translation"

    def translate(self, text):
        translated = self.model.generate(**self.tok.prepare_seq2seq_batch(text, return_tensors="pt").to(self.device))
        self.tgt_text = [self.tok.decode(t, skip_special_tokens=True) for t in translated]
        return self.tgt_text[0]
    
