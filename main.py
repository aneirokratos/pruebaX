import pandas as pd
from fastapi import FastAPI

ruta_archivo = 'https://drive.google.com/uc?id=1-XkhEhJjFk4UsLy_EaT3yUa0BXjAnErv'

df = pd.read_csv(ruta_archivo, parse_dates=['release_date'])
df['release_date'] = pd.to_datetime(df['release_date'])

app = FastAPI(title='Proyecto Individual Henry Data science',
            description='Carlos Aneiro Pérez')

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

@app.get('/votos_titulo/{votos}')
def votos_titulo(titulo_de_la_filmacion:str):
    data = df
    pelicula = data[data['title'] == titulo_de_la_filmacion]
    if pelicula.empty:
        return "No se encontró información para la película: " + titulo_de_la_filmacion
    else:
        votos = pelicula['vote_count'].values[0]
        promedio = pelicula['vote_average'].values[0]
        if votos >= 2000:
            return f"La película '{titulo_de_la_filmacion}' fue estrenada en el año {pelicula['release_year'].values[0]}. La misma cuenta con un total de {votos} valoraciones, con un promedio de {promedio}"
        else:
            return f"La película '{titulo_de_la_filmacion}' no cumple con la condición de tener al menos 2000 valoraciones."

@app.get('/actor/{actor}')
def get_actor(nombre_actor):
    lista_peli_actor = df[df['name_cast'].astype(str).str.contains(
        nombre_actor, case=False, na=False)].drop_duplicates(subset='id')
    if len(lista_peli_actor) > 0:
        num_movies = len(lista_peli_actor)
        total_return = lista_peli_actor['return'].sum()
        average_return = round(total_return / num_movies, 2)
        return f"El actor {nombre_actor} ha participado en {num_movies} películas, logrando un retorno total de {total_return} con un promedio de {average_return} por película."
    else:
        return f"No se encontraron datos del actor {nombre_actor}."
    
@app.get('/director/{director}')
def get_director(nombre_director):

    lista_peli_director = df[df['name_crew'].astype(str).str.contains(
        nombre_director, case=False, na=False)].drop_duplicates(subset='title')
    if len(lista_peli_director) > 0:
        movies = lista_peli_director['title'].tolist()
        release_years = lista_peli_director['release_year'].tolist()
        returns = lista_peli_director['return'].tolist()
        budgets = lista_peli_director['budget'].tolist()
        revenues = lista_peli_director['revenue'].tolist()
        return list(zip(movies, release_years, returns, budgets, revenues))
    else:
        return f"No records found for the director {nombre_director}."


@app.get('/recomendaciones/{recomendaciones}')
def obtener_recomendaciones_peliculas(title):
    # Obtener el género de la película de entrada
    genero_pelicula = df[df['title'] == title]['genero_nombre'].values[0]
    # Filtrar las películas que coinciden con el género de la película de entrada
    peliculas_coincidentes = df[df['genero_nombre'] == genero_pelicula]
    # Excluir la película de entrada de las recomendaciones
    peliculas_recomendadas = peliculas_coincidentes[peliculas_coincidentes['title'] != title]
    # Obtener los primeros 5 títulos de películas recomendadas
    recomendaciones = peliculas_recomendadas['title'].head(5).tolist()
    return recomendaciones