from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from data import df
from unidecode import unidecode
import uvicorn
from IPython.display import display
from pandas import DataFrame
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Instance api
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def welcome_page(request: Request):
    return templates.TemplateResponse("welcome.html", {"request": request, "title": "Welcome to 🎬 Movies Recommendation System 🍿"})

'''def welcome_page():
    title = "Welcome to Movies Recommendation Project"

    footer = """
    <footer>
        <p><h1>Created by Hugo Salazar</h1></p>
        <p><a href="https://www.linkedin.com/in/hasalazars/">LinkedIn</a></p>
        <p><a href="https://github.com/HugoSalazarS">GitHub</a></p>
    </footer>
    """

    body = """
    <h2>About the Project</h2>
    <p>The Movies Recommendation Project is designed to provide movie recommendations based on various criteria. It offers the following functions:</p>
    <ol>
        <li>This function calculates the number of films released in a specific month. The month input should be provided in Spanish language. <a href="/cantidad_filmaciones_mes/enero" target="_blank">Click here</a> to try this function.</li>
        <li>This function calculates the number of films released in a specific day of the week. The day of the week should be provided in Spanish language. <a href="/cantidad_filmaciones_dia/lunes" target="_blank">Click here</a> to try this function.</li>
        <li>This function returns the title, the year released, and the score of the movie. If there is more than one movie with the same title, it returns all of them. <a href="/score_titulo/cinderella" target="_blank">Click here</a> to try this function.</li>
        <li>This function returns the title, the total number of votes, and the average vote value. <a href="/votos_titulo/Toy Story" target="_blank">Click here</a> to try this function.</li>
        <li>This function retrieves information about an actor, including the number of films they have participated in and the total return value. <a href="/get_actor/Tom Hanks" target="_blank">Click here</a> to try this function.</li>
        <li>This function retrieves information about a director, including the number of films they have directed and the total return value. <a href="/get_director/Steven Spielberg" target="_blank">Click here</a> to try this function.</li>
        <li><b>This function retrieves 5 recomended Movies based on the title given by the user. <a href="/recomendacion/Twelve Monkeys" target="_blank">Click here</a> to try this function. </li>
    </ol>
    """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{title}</title>
        <style>
            table, th, td {{
                border: 1px solid black;
                border-collapse: collapse;
                padding: 8px;
                text-align: left;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        {body}
        {footer}
    </body>
    </html>
    """'''

meses = {
        "enero": "January",
        "febrero": "February",
        "marzo": "March",
        "abril": "April",
        "mayo": "May",
        "junio": "June",
        "julio": "July",
        "agosto": "August",
        "septiembre": "September",
        "octubre": "October",
        "noviembre": "November",
        "diciembre": "December"
    }

# 1 This function calculates the number of films released in a specific month. The month input should be provided in Spanish language.
@app.get("/cantidad_filmaciones_mes/{mes}")
def cantidad_filmaciones_mes(mes: str):
    # Convert month to Spanish
    mes = mes.lower().strip()

    # Verify if the month is in the dict
    if mes in meses:
        # Get the corresponding English month name
        mes_en_ingles = meses[mes]
        # Count the films with release dates containing the English month name
        cantidad = len(df[df["release_date"].str.contains(mes_en_ingles, case=False)])
    else:
        # Return a message indicating that no films were released in the month
        return {'mes': mes, 'cantidad': f"No se encontraron películas estrenadas en el mes de {mes}"}

    # respuesta = f"{cantidad} películas fueron estrenadas en el mes de {mes}"

    # Return the month and the count of film releases
    return {'mes': mes, 'cantidad': cantidad}



@app.get("/view_films/{mes}")
def view_films_mes(mes: str):
    mes = mes.lower().strip()

    if mes in meses:
        mes_en_ingles = meses[mes]
        films = df[df["release_date"].str.contains(mes_en_ingles, case=False)][["title", "release_year"]].sort_values(by="release_year")

        if films.empty:
            return f"No se encontraron películas estrenadas en el mes de {mes}"

        table_html = films.to_html(index=False)

        page_title = f"Películas estrenadas en el mes de {mes}"

        complete_html = f"""
        <html>
        <head>
            <title>{page_title}</title>
        </head>
        <body>
            <h1>{page_title}</h1>
            {table_html}
        </body>
        </html>
        """

        return HTMLResponse(content=complete_html, status_code=200)
    else:
        return f"No se reconoce el mes '{mes}'. Por favor, ingresa un mes válido en español."


# 2 Calculate the number of films releasead in a specific day of the week. The day of the weew should be provided in Spanish Language.

dias = {
        "lunes": "Monday",
        "martes": "Tuesday",
        "miércoles": "Wednesday",
        "jueves": "Thursday",
        "viernes": "Friday",
        "sábado": "Saturday",
        "domingo": "Sunday"
    }

@app.get("/cantidad_filmaciones_dia/{dia}")
def cantidad_filmaciones_dia(dia: str):
    # Convert the day string to lowercase and remove whitespace
    dia = dia.lower().strip()

    if dia in dias: # Check if the day exists in the dias dictionary
        dia_en_ingles = dias[dia] # Convert the day to English
        films = df[df["release_day"].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower().str.contains(dia_en_ingles, case=False)]

        if films.empty:
            return {'dia': dia, 'cantidad': f"No se encontraron películas estrenadas en los días {dia}"}

        # respuesta = f"{len(films)} películas fueron estrenadas en los días {dia}"

        # Return the day and the count of film releases
        return {'dia': dia, 'cantidad': len(films)} 
    else:
        # Return message for unrecognized day
        return {'dia': dia, 'cantidad': f"No se reconoce el día '{dia}'. Por favor, ingresa un día de la semana válido en español."}


@app.get("/view_films_day/{day}")
def view_films_day(day: str):
    day = day.lower().strip()  # Convert the day string to lowercase and remove whitespace

    if day in dias:  # Check if the day exists in the dias dictionary
        dia_en_ingles = dias[day]  # Convert the day to English
        films = df[df["release_day"].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8').str.lower().str.contains(dia_en_ingles, case=False)][["title", "release_year", "Director"]].sort_values(by="release_year")

        if films.empty:
            return f"No films were released on {day}"  # Return message for no films found
    
    table_html = films.to_html(index=False)  # Convert the films DataFrame to an HTML table

    # Set the page title
    page_title = f"Films Released on {day}"

    # Embed the table in a complete HTML page
    complete_html = f"""
    <html>
    <head>
        <title>{page_title}</title>
    </head>
    <body>
        <h1>{page_title}</h1>
        {table_html}
    </body>
    </html>
    """

    return HTMLResponse(content=complete_html, status_code=200)



# 3 Returns the title, the year released and the score of the movie. If there is more than one movie with the same title, returns all of them
@app.get("/score_titulo/{film_title}")
def score_titulo(film_title: str):
    # Filter films based on the specified film title
    films = df[df["title"].str.lower() == film_title.lower()]
    # Check if films are found
    if films.empty:
        return {'titulo': film_title, 'anio': None, 'popularidad': "No se encontró la filmación especificada."}
    # Sort films by release year in ascending order
    ordered_films = films.sort_values(by="release_year")
    # Initialize an empty list to store the response
    respuesta = []
    # Iterate over the ordered films
    for index, row in ordered_films.iterrows():
        # Extract the title, release year, and popularity score of each film
        title = row["title"]
        year_released = row["release_year"]
        score = row["popularity"]
        # Create a dictionary for the film and add it to the response list
        respuesta.append({'titulo': title, 'anio': year_released, 'popularidad': score})

    return respuesta
    

# 4 Returns the title, the total of votes and the vote average

@app.get("/votos_titulo/{titulo}")
def votos_titulo(titulo:str):
    # Filter films based on the specified film title
    filmaciones = df[df["title"].str.lower() == titulo.lower()]
    # Check if films are found
    if filmaciones.empty:
        return "No se encontró la filmación especificada."
    
    # Initialize an empty list to store the responses
    respuestas = []
    
    # Iterate over the filtered films
    for _, row in filmaciones.iterrows():
        cantidad_votos = row["vote_count"]
        
        if cantidad_votos < 2000:
            continue  # Skip this movie if you don't meet the minimum number of votes
        
        # Extract the vote count, title, release year, and average vote of each film
        titulo = row["title"]
        anio = row["release_year"]
        promedio_votos = row["vote_average"]

        # Create a dictionary for the film with its information
        respuesta = {'titulo': titulo, 'anio': anio, 'voto_total': cantidad_votos, 'voto_promedio': promedio_votos}
        respuestas.append(respuesta)

    # Check if no films meet the minimum vote count requirement
    if not respuestas:
        return "No se encontraron filmaciones que cumplan con la cantidad mínima de votos requerida (2000 votos)."
    
    return respuesta


# 5 Returns the total films and the average return
@app.get("/get_actor/{actor_name}")
def get_actor(actor_name):
    # Filter films based on the specified actor name
    actor_films = df[df["actor_name_funct"].str.contains(fr"\b{actor_name}\b", case=False, regex=True, na=False)]
    
    # Check if films are found for the actor
    if actor_films.empty:
        return "The specified actor was not found."
    
    # Calculate the number of films for the actor
    film_count = len(actor_films)
    
    # Calculate the total return of the actor's films
    total_return = round(actor_films["return"].sum(),2)
    
    # Calculate the average return per film
    average_return = round(total_return / film_count,2)
    
    # Return a dictionary containing the actor's name, the number of films, total return, and average return
    return {'actor': actor_name, 'film_count': film_count, 'total_return': total_return, 'average_return': average_return}



# 6 Returns the Director's information, how many films have been directed, and the total return value
@app.get("/get_director/{director_name}")
def get_director(director_name: str):
    # Filter movies based on the specified director name
    director_movies = df[df['Director'].str.contains(fr"\b{director_name}\b", case=False, regex=True, na=False)]

    # Check if movies are found for the director
    if director_movies.empty:
        return "The specified director was not found."

    # Calculate the number of movies for the director
    film_count = len(director_movies)

    # Calculate the total return of the director's movies
    total_return = round(director_movies['return'].sum(), 2)

    # Create a table of movies with selected columns and round the values to 2 decimal places
    movies_table = round(director_movies[['title', 'release_year', 'return', 'budget', 'revenue']], 2)

    
    return {'Director': director_name,
            'retorno_total_director': total_return,
            'total_peliculas': film_count,
            'peliculas': movies_table.to_dict(orient='records')}

# Remove rows with missing or null values in relevant columns
df1 = df.drop(columns=['budget', 'id', 'revenue', 'release_date', 'status', 'runtime', 'actor_name', 'genre', 'character', 'collection', 'status', 'tagline', 'vote_count', 'id_collection', 'genre', 'companies_id', 'companies_name', 'countrie_name', 'lang_name', 'release_year', 'return', 'character', 'lang_name'])

# Function to transform the columns for the vectrizer
def clean_column_values(df, column_name):
    df[column_name] = df[column_name].astype(str).str.replace('[', '', regex=False)
    df[column_name] = df[column_name].astype(str).str.replace(']', '', regex=False)
    df[column_name] = df[column_name].astype(str).str.replace("'", '', regex=False)
    df[column_name] = df[column_name].astype(str).str.replace(",", '', regex=False)
    return df

clean_column_values(df1,'actor_id')
clean_column_values(df1,'genre_id')


# Create a term frequency matrix using CountVectorizer for relevant columns
vectorizer = CountVectorizer()
term_matrix = vectorizer.fit_transform(df1['genre_id'] + ' ' + df1['actor_id'] + ' ' + df1['title'] + ' ' + df1['popularity'].astype(str) + ' ' + df1['vote_average'].astype(str))

# Function to get movies similar to a given movie
def obtener_peliculas_similares(titulo, n=5):
    titulo = titulo.lower()
    indice_pelicula = df1[df1['title'].str.lower() == titulo].index
    if len(indice_pelicula) == 0:
        return 'No se encontró la película, revisa si está bien escrita'

    indice_pelicula = indice_pelicula[0]
    vector_pelicula = term_matrix[indice_pelicula]
    similaridades = cosine_similarity(vector_pelicula, term_matrix)[0]
    indices_similares = similaridades.argsort()[::-1][1:n+1]  # Exclude the given movie

    # Sort the similar movies based on similarity score
    indices_similares_sorted = sorted(indices_similares, key=lambda x: similaridades[x], reverse=True)
    peliculas_similares = df1.iloc[indices_similares_sorted]['title'].tolist()
    return peliculas_similares

@app.get('/recomendacion/{titulo}')
def recomendacion(titulo: str):
    peliculas_recomendadas = obtener_peliculas_similares(titulo)
    return {'lista recomendada': peliculas_recomendadas}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)