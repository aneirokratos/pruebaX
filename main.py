import pandas as pd
from fastapi import FastAPI
from starlette.responses import HTMLResponse
import locale

ruta_archivo = 'https://drive.google.com/uc?id=1-XkhEhJjFk4UsLy_EaT3yUa0BXjAnErv'

df = pd.read_csv(ruta_archivo, parse_dates=['release_date'])
df['release_date'] = pd.to_datetime(df['release_date'])

app = FastAPI(title='Proyecto Individual Henry Data science',
            description='Carlos Aneiro Pérez')

# Establecer configuración regional al inicio de la aplicación
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

@app.get("/")
def welcome_page():
    return ("Aplicación de películas de Carlos Aneiro Pérez")

@app.get("/fimaciones/mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
  
    mes = mes.lower()
    
    meses = {
    'enero': 1,
    'febrero': 2,
    'marzo': 3,
    'abril': 4,
    'mayo': 5,
    'junio': 6,
    'julio': 7,
    'agosto': 8,
    'septiembre': 9,
    'octubre': 10,
    'noviembre': 11,
    'diciembre': 12}

    mes_numero = meses[mes]

    try:
        month_filtered = df[df['release_date'].dt.month == mes_numero]
    except (ValueError, KeyError, TypeError):
        return None

    month_unique = month_filtered.drop_duplicates(subset='id')
    respuesta = month_unique.shape[0]

    return {'La cantidad de películas estrenadas en el mes es':mes, 'es de':respuesta}

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

    return {'La cantidad de películas estrenadas en el día':dia, 'es de':respuesta}

@app.get('/score_titulo/{titulo}')
def score_titulo(titulo:str):
   lista_peliculas_title = df[df['title'] == titulo].drop_duplicates(subset='title')    
   titulo = str(lista_peliculas_title['title'].iloc[0])
   año = str(lista_peliculas_title['release_year'].iloc[0])
   score =str(lista_peliculas_title['popularity'].iloc[0])
   return {'titulo':titulo, 'año':año, 'popularidad':score}