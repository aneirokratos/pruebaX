import pandas as pd
from fastapi import FastAPI
from starlette.responses import HTMLResponse

import pandas as pd

ruta_archivo = 'https://drive.google.com/uc?id=1-XkhEhJjFk4UsLy_EaT3yUa0BXjAnErv'

df = pd.read_csv(ruta_archivo, parse_dates=['release_date'])

app = FastAPI(title='Proyecto Individual Henry Data science',
            description='Carlos Aneiro Pérez')

@app.get("/")
def welcome_page():
    return ("Aplicación de películas de Carlos Aneiro Pérez")

@app.get("/fimaciones/mes{mes}")
def cantidad_filmaciones_mes(mes):
    data_filtrado = df[df['release_date'].dt.month_name(locale='es') == mes]
    cantidad = len(data_filtrado)
    return str(f"La cantidad de películas estrenadas en el mes es {cantidad}")


@app.get("/filmaciones/dia")
def cantidad_filmaciones_dia(dia:str):
    days = {
    'lunes': 'Monday',
    'martes': 'Tuesday',
    'miercoles': 'Wednesday',
    'jueves': 'Thursday',
    'viernes': 'Friday',
    'sabado': 'Saturday',
    'domingo': 'Sunday'}

    day = days[dia.lower()]

    lista_peliculas_day = df[df['release_date'].dt.day_name() == day].drop_duplicates(subset='id')
    respuesta = lista_peliculas_day.shape[0]

    return {'dia':dia, 'cantidad':respuesta}

@app.get('/score_titulo/{titulo}')
def score_titulo(titulo:str):
   lista_peliculas_title = df[df['title'] == titulo].drop_duplicates(subset='title')    
   titulo = str(lista_peliculas_title['title'].iloc[0])
   año = str(lista_peliculas_title['release_year'].iloc[0])
   score =str(lista_peliculas_title['popularity'].iloc[0])
   return {'titulo':titulo, 'año':año, 'popularidad':score}