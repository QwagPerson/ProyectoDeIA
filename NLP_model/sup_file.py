import pickle
import re
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from torch import nn
from transformers import AutoModelForSequenceClassification

class PreProccesingTransformer(BaseEstimator, TransformerMixin):
    def preprocess(self,sentence):
      # Deleting all except: exclamation/question signs and accents
      new_word = re.sub(r"[^a-zA-ZáéíóúÁÉÍÓÚñÑ¡!¿?\s]", '', sentence)
      # Deleting double blank spaces
      new_sentence = new_word.replace('  ',' ').replace('\n','').strip()
      return new_sentence

    def transform(self, X, y=None):
        values = []
        for tweet in X:
            values.append(self.preprocess(tweet))

        return(np.array(values))

    def fit(self, X, y=None):
        return self

class Classifier(nn.Module):
    def __init__(self, model_name, num_classes):
        super(Classifier, self).__init__()
        self.bert = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_classes)

    def forward(self, input_ids, attention_mask):
            outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
            return outputs