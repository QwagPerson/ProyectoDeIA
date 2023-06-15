import pickle
from sup_file import PreProccesingTransformer

with open(r"C:\Users\nahue\OneDrive\Escritorio\Universidad\9no_Semestre\CC6409_Proyecto de IA\ProyectoDeIA\NLP_model\model1.bin", 'rb') as archivo:
    modelo = pickle.load(archivo)

print(modelo.predict(['Hola, quiero cancelar mi hora']))

