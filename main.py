import pandas as pd
from fastapi import FastAPI
from starlette.responses import HTMLResponse

import pandas as pd

ruta_archivo = 'https://drive.google.com/uc?id=1-XkhEhJjFk4UsLy_EaT3yUa0BXjAnErv'

df = pd.read_csv(ruta_archivo, parse_dates=['release_date'])

app = FastAPI()

@app.get("/")
def welcome_page():
    return ("Aplicación de películas de Carlos Aneiro Pérez")

@app.get("/fimaciones/mes{mes}")
def cantidad_filmaciones_mes(mes):
    data_filtrado = df[df['release_date'].dt.month_name(locale='es') == mes]
    cantidad = len(data_filtrado)
    return{f"La cantidad de películas estrenadas en el mes es {cantidad}"}


@app.post("/filmaciones/dia")
def cantidad_filmaciones_dia(dia):
    data_filtrado = df[df['release_date'].dt.day_name(
        locale='es') == dia]
    cantidad_dia = len(data_filtrado)
    return str(f"La cantidad de películas estrenadas en el dìa es {cantidad_dia}")