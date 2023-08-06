from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def welcome_page():
    return """
    <html>
        <head>
            <title>Proyecto individual</title>
        </head>
        <body>
            <h1>Aplicación de películas de Carlos Aneiro Pérez</h1>
 <form action="/respuesta" method="post">
                <label for="respuesta1">Respuesta 1:</label>
                <input type="text" id="respuesta1" name="respuesta1"><br><br>
                <input type="submit" value="Enviar">
            </form>
            
            <form action="/respuesta2" method="post">
                <label for="respuesta2">Respuesta 2:</label>
                <input type="text" id="respuesta2" name="respuesta2"><br><br>
                <input type="submit" value="Enviar">
            </form>
        </body>
    </html>
    """

@app.post("/respuesta", response_class=HTMLResponse)
def respuesta_page(respuesta1: str):
    return f"""
    <html>
        <head>
            <title>Respuestas</title>
        </head>
        <body>
            <h1>Tu respuesta 1:</h1>
            <p>Respuesta 1: {respuesta1}</p>
        </body>
    </html>
    """

@app.post("/respuesta2", response_class=HTMLResponse)
def respuesta2_page(respuesta2: str):
    return f"""
    <html>
        <head>
            <title>Respuestas</title>
        </head>
        <body>
            <h1>Tu respuesta 2:</h1>
            <p>Respuesta 2: {respuesta2}</p>
        </body>
    </html>
    """