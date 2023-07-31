from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from unidecode import unidecode
import uvicorn
from pandas import DataFrame
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import HTTPException

app = FastAPI()

df_peliculas = pd.read_csv('data_movies_fin.csv')
df_peliculas['id'] = df_peliculas['id'].astype(int)
df_creditos = pd.read_csv('creditos_fin.csv')
df_unido = pd.merge(df_peliculas, df_creditos, on='id')


# ---------------------------------------------------
@app.get("/cantidad_filmaciones_mes/{mes}", tags=['Consulta 1'])
async def cantidad_filmaciones_mes_endpoint(mes: str):
        # Convertir la columna "release_date" a tipo datetime si no está en ese formato
    df_unido['release_date'] = pd.to_datetime(df_unido['release_date'])
    # Filtrar los datos por el mes especificado en español
    data_filtrado = df_unido[df_unido['release_date'].dt.month_name(
        locale='es') == mes]
    # Obtener la cantidad de registros que coinciden
    cantidad = len(data_filtrado)
    mensaje = f"La cantidad de películas estrenadas en el mes es {cantidad}"
    return mensaje

    
  

# ----------------------------------------------------
@app.get("/cantidad_filmaciones_dia/{dia}", tags=['Consulta 2'])
async def cantidad_filmaciones_dia_endpoint(dia: str):
    data_filtrado = df_unido[df_unido['release_date'].dt.day_name(
        locale='es') == dia]
    # Obtener la cantidad de registros que coinciden
    cantidad = len(data_filtrado)
    mensaje = f"La cantidad de películas estrenadas en el día es {cantidad}"
    return {"mensaje":mensaje}

# ----------------------------------------------------
@app.get("/score_titulo/{titulo}", tags=['Consulta 3'])
async def score_titulo_endpoint(title: str):
    """
    Endpoint para obtener información de una filmación a partir de su título.
    
    Args:
        titulo (str): Título de la filmación en formato de texto.
    
    Returns:
        dict: Diccionario con el mensaje que contiene el título, año de estreno y score/popularidad de la filmación.
              En caso de no encontrar la filmación, se devuelve un mensaje de error.
    """
    # Convertir el título de la filmación a minúsculas para realizar la comparación
    titulo = titulo.lower()

    # Extraer los DataFrames del archivo ZIP
    datasets_df, _, _, _, _ = df_unido

    # Filtrar el DataFrame para obtener la fila correspondiente al título de la filmación
    filmacion = datasets_df[datasets_df['title'].str.lower() == titulo]

    if filmacion.empty:
        return {"mensaje": f"No se encontró la filmación con el título: {titulo}"}

    # Obtener el título, año de estreno y score de la filmación
    titulo_filmacion = filmacion['title'].iloc[0]
    año_estreno = filmacion['release_year'].iloc[0]
    score = round(filmacion['popularity'].iloc[0], 2)

    mensaje = f"La película '{titulo_filmacion}' fue estrenada en el año {año_estreno} con un score/popularidad de {score}"
    return {"mensaje": mensaje}

# ----------------------------------------------------
@app.get("/votos_titulo/{titulo}", tags=['Consulta 4'])
async def votos_valor_de_la_filmacion_endpoint(titulo: str):
    """
    Endpoint para obtener información sobre los votos y valoraciones de una filmación a partir de su título.
    
    Args:
        titulo (str): Título de la filmación en formato de texto.
    
    Returns:
        dict: Diccionario con el mensaje que contiene el título, año de estreno, cantidad de votos y promedio de votaciones de la filmación.
              En caso de no encontrar la filmación o no cumplir con la cantidad mínima de votos, se devuelve un mensaje de error.
    """
    # Convertir el título de la filmación a minúsculas para realizar la comparación
    titulo = titulo.lower()

    # Extraer los DataFrames del archivo ZIP
    datasets_df, _, _, _, _ = df_unido

    # Filtrar el DataFrame para obtener la fila correspondiente al título de la filmación
    filmacion = datasets_df[datasets_df['title'].str.lower() == titulo]

    if filmacion.empty:
        return {"mensaje": f"No se encontró la filmación con el título: {titulo}"}

    # Obtener el título, año de estreno, cantidad de votos y promedio de votaciones de la filmación
    titulo_filmacion = filmacion['title'].iloc[0]
    año_estreno = filmacion['release_year'].iloc[0]
    cantidad_votos = round(filmacion['vote_count'].iloc[0])
    promedio_votaciones = filmacion['vote_average'].iloc[0]

    if cantidad_votos < 2000:
        return {"mensaje": f"La filmación '{titulo_filmacion}' no cumple con la condición de tener al menos 2000 votos"}

    mensaje = f"La película '{titulo_filmacion}' fue estrenada en el año {año_estreno}. La misma cuenta con un total de {cantidad_votos} valoraciones, con un promedio de {promedio_votaciones}"

    return {"mensaje": mensaje}

# ----------------------------------------------------
@app.get("/get_actor/{nombre}", tags=['Consulta 5'])
def nombre_actor(nombre: str):
    """
    Endpoint para obtener información sobre un actor a partir de su nombre.
    
    Args:
        nombre (str): Nombre del actor en formato de texto.
    
    Returns:
        dict: Diccionario con el nombre del actor, la cantidad de películas en las que ha participado, el promedio de retorno monetario de las películas
              y una lista de diccionarios con los títulos y retornos monetarios de las películas en las que ha participado.
    """
    datasets_df, _, cast_df, _, _ = df_unido

    # Filtrar las filas en las que el actor aparece en la columna "cast"
    actor_movies = cast_df[cast_df['cast'].str.contains(nombre, case=False)]
    
    # Verificar si se encontraron películas del actor
    if actor_movies.empty:
        return {"mensaje": f"No se encontró al actor {nombre} en la base de datos."}
        
    # Obtener los ID de las películas en las que el actor ha participado
    movie_ids = actor_movies['id'].tolist()
    
    # Filtrar el dataset "datasets_df" para obtener los nombres y retornos monetarios de las películas correspondientes
    movies = datasets_df[datasets_df['id'].isin(movie_ids)]
    
    # Obtener la cantidad de películas en las que el actor ha participado
    movie_count = len(movies)
    
    # Obtener el promedio de retorno monetario de las películas
    average_revenue = round(movies['revenue'].mean(), 2)

    
    # Crear una lista de diccionarios con los nombres y retornos monetarios de las películas
    movie_info = []
    for _, row in movies.iterrows():
        movie_info.append({
            "titulo": row['title'],
            "retorno_monetario": row['revenue']
        })
    
    return {
        "nombre_actor": nombre,
        "cantidad_peliculas": movie_count,
        "promedio_retorno_monetario": average_revenue,
        "peliculas": movie_info
    }

# ----------------------------------------------------
@app.get("/get_director/{nombre}", tags=['Consulta 6'])
def nombre_director(nombre: str):
    """
    Endpoint para obtener información sobre un director a partir de su nombre.
    
    Args:
        nombre (str): Nombre del director en formato de texto.
    
    Returns:
        dict: Diccionario con el nombre del director, las ganancias totales de las películas que ha dirigido y una lista de diccionarios
              con los ID, títulos, años, presupuestos, ingresos y relaciones de las películas dirigidas por el director.
    """
    datasets_df, crew_df, _, _, _ = df_unido

    # Filtrar las filas en las que el director aparece en la columna "crew_name" y "crew_job" contiene "Director"
    director_movies = crew_df[(crew_df['crew_name'].str.contains(nombre, case=False)) & (crew_df['crew_job'].str.contains("Director"))]
    
    # Verificar si se encontraron películas del director
    if director_movies.empty:
        return {"mensaje": f"No se encontró al director {nombre} en la base de datos."}
    
    # Obtener los ID de las películas en las que el director ha trabajado
    movie_ids = director_movies['id'].tolist()
    
    # Filtrar el dataset "datasets_df" para obtener los nombres, años, presupuestos, ingresos y relación de las películas correspondientes
    movies = datasets_df[datasets_df['id'].isin(movie_ids)]
    
    # Calcular las ganancias sumando todas las relaciones de las películas
    ganancias = round(movies['return'].sum(), 2)
    
    # Crear una lista de diccionarios con los ID, nombres, años, presupuestos, ingresos y relación de las películas
    movie_info = []
    for _, row in movies.iterrows():
        movie_info.append({
            "id": row['id'],
            "titulo": row['title'],
            "anio": row['release_year'],
            "presupuesto": row['budget'],
            "ingresos": row['revenue'],
            "relacion": row['return']
        })
    
    return {
        "nombre_director": nombre,
        "ganancias": ganancias,
        "peliculas": movie_info
    }

# Endpoint para la recomendación de películas
# ----------------------------------------------------
@app.get("/recomendacion/{movie_title}", tags=['Machine Learning'])
def recomendar_pelicula(movie_title: str):
    """
    Devuelve una lista de las 5 películas recomendadas basadas en una película dada.

    Args:
        movie_title (str): El título de la película.

    Returns:
        dict: Un diccionario con las películas recomendadas como una lista.
    """

    recommended_movies = recomendar_pelicula(movie_title)
    return {"recommended_movies": recommended_movies.tolist()}


 


# ----------------------------------------------------
# Ejecutar la aplicación
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



