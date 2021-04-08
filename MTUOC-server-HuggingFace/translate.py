#adapted from https://towardsdatascience.com/build-your-own-machine-translation-service-with-transformers-d0709df0791b
from transformers import MarianTokenizer, MarianMTModel
import os
from typing import List

class Translator():
    def __init__(self, models_dir,SL,TL):
        self.models = {}
        self.models_dir = models_dir
        self.SL=SL
        self.TL=TL
        route = f'{self.SL}-{self.TL}'
        success_code, message = self.load_model(route)
        if not success_code:
            return message

    def load_model(self, route):
        model = f'opus-mt-{route}'
        path = os.path.join(self.models_dir,model)
        try:
            self.model = MarianMTModel.from_pretrained(path)
            self.tok = MarianTokenizer.from_pretrained(path)
        except:
            return 0,f"Make sure you have downloaded model for {route} translation"
        return 1,f"Successfully loaded model for {route} transation"

    def translate(self, text):
        translated = self.model.generate(**self.tok.prepare_seq2seq_batch(text, return_tensors="pt"))
        self.tgt_text = [self.tok.decode(t, skip_special_tokens=True) for t in translated]
        return self.tgt_text[0]
    
