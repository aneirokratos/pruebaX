from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def welcome_page():
    return """
    <html>
        <head>
            <title>Bienvenido</title>
        </head>
        <body>
            <h1>Bienvenido a mi aplicación</h1>
            <form action="/respuesta" method="post">
                <label for="respuesta1">Respuesta 1:</label>
                <input type="text" id="respuesta1" name="respuesta1"><br><br>
                <label for="respuesta2">Respuesta 2:</label>
                <input type="text" id="respuesta2" name="respuesta2"><br><br>
                <input type="submit" value="Enviar">
            </form>
        </body>
    </html>
    """

@app.post("/respuesta", response_class=HTMLResponse)
def respuesta_page(respuesta1: str, respuesta2: str):
    return f"""
    <html>
        <head>
            <title>Respuestas</title>
        </head>
        <body>
            <h1>Tus respuestas:</h1>
            <p>Respuesta 1: {respuesta1}</p>
            <p>Respuesta 2: {respuesta2}</p>
        </body>
    </html>
    """