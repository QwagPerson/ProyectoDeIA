from bot_poo import Bot

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import pickle
import re
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
#from sup_file import PreProccesingTransformer, Classifier
import uvicorn
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from torch import nn
import os
from sup_file import Classifier


## Load Model And tokenizer
def load_model(model_path, device):
    modelo = torch.load(model_path, map_location=device)
    return modelo

def load_tokenizer(tokenizer_path, device):
    tokenizer = torch.load(tokenizer_path, map_location=device)
    return tokenizer


if __name__ == "__main__":
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    print(script_dir)

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("Using device:", device)
    MODEL = load_model(f'{script_dir}\\model_beto.pt',device)
    TOKENIZER = load_tokenizer(f'{script_dir}\\tokenizer_beto.pt',device)

    botcito = Bot('123', 'Nahuel', MODEL, TOKENIZER, device)

    while botcito.action_stage != 'end':
        x = input('Val: ')
        botcito.action(x)