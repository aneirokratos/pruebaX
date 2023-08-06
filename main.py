import pandas as pd
import requests
from fastapi import FastAPI
from starlette.responses import HTMLResponse

ruta_archivo = 'https://drive.google.com/uc?id=1-XkhEhJjFk4UsLy_EaT3yUa0BXjAnErv'
response = requests.get(ruta_archivo)
with open('data.csv', 'wb') as file:
    file.write(response.content)

df = pd.read_csv('data.csv', parse_dates=['release_date'])

app = FastAPI()

@app.get("/")
def welcome_page():
    return "Aplicación de películas de Carlos Aneiro Pérez"

@app.post("/Cantidad_filmaciones_mes")
def cantidad_filmaciones_mes(mes):
    data_filtrado = df[df['release_date'].dt.month_name(locale='es') == mes]
    cantidad = len(data_filtrado)
    
    return str(f"La cantidad de películas estrenadas en el mes es {cantidad}")


