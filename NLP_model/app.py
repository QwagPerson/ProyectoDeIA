from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import pickle
import re
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sup_file import PreProccesingTransformer, Classifier
import uvicorn
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from torch import nn

app = FastAPI()

sf = nn.Softmax(dim=1)

def load_model(device):
    modelo = torch.load("model_beto.pt", map_location=device)
    return modelo

def load_tokenizer(device):
    tokenizer = torch.load("tokenizer_beto.pt", map_location=device)
    return tokenizer

def make_pred(data, model, tokenizer, device):
  tokenizer_result = tokenizer(data)
  input_ids = torch.tensor(tokenizer_result["input_ids"]).to(device)
  attention_mask = torch.tensor(tokenizer_result["attention_mask"]).to(device)
  outputs = sf(model(input_ids, attention_mask).logits)
  return torch.argmax(outputs, dim=1)

@app.post("/predict")
def predict(data: list):
    # Make a prediction
    prediccion = make_pred(data, MODEL, TOKENIZER, device)
    # Response with Json
    respuesta = {"prediccion": prediccion.tolist()}
    print(data, prediccion.tolist())
    return JSONResponse(content=jsonable_encoder(respuesta))

if __name__ == "__main__":
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    print("Using device:", device)
    MODEL = load_model(device)
    TOKENIZER = load_tokenizer(device)
    uvicorn.run(app, host="localhost", port=8000)