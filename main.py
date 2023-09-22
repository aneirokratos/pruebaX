import pandas as pd
from fastapi import FastAPI

ruta_archivo_1 = 'https://drive.google.com/file/d/1nIuN3jQ0YccfCVE-H79nmdiRPTeTRgrm/view?usp=sharing'
ruta_archivo_2 = 'https://drive.google.com/file/d/1PXAN45iaP1DQQ1DVbICFujtxFW-p18ZO/view?usp=sharing'
ruta_archivo_3 = 'https://drive.google.com/file/d/1c3Sd2z6H5ydCrxDu8PFVjcBAMLc_ty4b/view?usp=sharing'
ruta_archivo_4 = 'https://drive.google.com/file/d/1IDMT7UcriqUOspiOJIOw8SGtiBe05yai/view?usp=drive_link'

# Leer el archivo CSV y guardarlo en un dataframe
rank_genre = pd.read_csv(ruta_archivo_1)
genre_data = pd.read_csv(ruta_archivo_2)
df_steam = pd.read_csv(ruta_archivo_3)
cant_items = pd.read_csv(ruta_archivo_4)

# Puedes utilizar el dataframe como necesites en tu aplicación FastAPI

app = FastAPI(title='Proyecto Individual Henry Data science',
            description='Carlos Aneiro Pérez')

df_steam['release_date'] = pd.to_datetime(
    df_steam['release_date'], errors='coerce')

@app.get("/")
def welcome_page():
    return ("Aplicación de películas de Carlos Aneiro Pérez")

@app.get("/Developer")
def developer(df, developer):
    # Filter data for the specified developer
    df_dev = df_steam[df_steam['developer'] == developer]
    # Get a list of unique years
    years = df_steam['release_date'].dt.year.unique()
    # Iterate over the years
    percentages = []
    for year in years:
        # Filter data for the year
        df_year = df_dev[df_dev['release_date'].dt.year == year]
        # Convert 'price' column to string
        df_year['price'] = df_year['price'].astype(str)
        # Count the number of free contents
        num_free = df_year[df_year['price'].str.lower(
        ).str.contains('free')].shape[0]
        # Calculate the percentage
        if num_free == 0:
            percentage = 0
        else:
            percentage = (num_free / df_year.shape[0]) * 100
        # Add the percentage to the list
        percentages.append(f'{year}: {percentage:.2f}%')
    return percentages

@app.get("/userdata")
def userdata(user_id):
    # Filtrar el dataframe por el user_id especificado
    user_data = cant_items[cant_items["user_id"] == user_id]

    # Obtener la cantidad de items y la suma de precios
    item_count = len(user_data)
    total_price = user_data["price"].sum()

    return {
        "Cantidad de items": item_count,
        "Suma de precios": total_price
    }


@app.get('genre')
def genre(genero):
    # filtro el dataframe "rank_genre" para quesu columna "genres" sea igual a el dato que se ingresa
    # a partir de esto se selecciona la columna "ranking" del conjunto resultante y se bloquea para obtener el valor
    orden = rank_genre[rank_genre["genre"] == genero]["ranking"].iloc[0]
    return {
        "El género": genero,
        "se encuentra en el puesto": orden
    }


@app.get('/userforgenre')
def userforgenre(genero):
    # se filtra el dataframe con la columna "genres" y se la iguala con el dato ingresado
    genre_data = genre_data[genre_data["genre"] == genero]
    # agrupo el genero por usuario y horas jugadas
    user_hours = genre_data.groupby(["user_id", "user_url"])[
        "playtime_forever"].sum().reset_index()
    # ordena los valores de mayor a menor
    user_hours = user_hours.sort_values(by="playtime_forever", ascending=False)
    # extrae los primeros 5
    top_5_users = user_hours.head(5)
    return top_5_users

