from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import pickle

app = FastAPI()

@app.post("/predict")
def predict(data: dict):
    # Load the best model
    with open('model1.pkl', 'rb') as archivo:
        modelo = pickle.load(archivo)

    # Make a prediction
    prediccion = modelo.predict(data)

    # Response with Json
    respuesta = {"prediccion": prediccion.tolist()}
    return JSONResponse(content=jsonable_encoder(respuesta))
