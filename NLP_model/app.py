from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import pickle
import re
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sup_file import PreProccesingTransformer
import uvicorn

app = FastAPI()


def load_model():
    with open('model1.bin', 'rb') as archivo:
        modelo = pickle.load(archivo)
    return modelo


@app.post("/predict")
def predict(data: dict):
    # Make a prediction
    prediccion = MODEL.predict(data)

    # Response with Json
    respuesta = {"prediccion": prediccion.tolist()}
    return JSONResponse(content=jsonable_encoder(respuesta))

if __name__ == "__main__":
    MODEL = load_model()
    uvicorn.run(app, host="localhost", port=8000)