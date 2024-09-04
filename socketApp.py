import asyncio
import random
import string
import socketio
from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests

# Création de l'application FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Création du serveur Socket.IO avec les options CORS
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # Ajoutez ici l'origine de votre frontend
    logger=True,
    engineio_logger=True,
    allow_eio3=True
)
socket_app = socketio.ASGIApp(sio)

# Monter le serveur Socket.IO sur l'application FastAPI
app.mount("/", socket_app)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Monitoring GAME SOCKET API By RELOU"}

# Fonction pour envoyer un ID aléatoire toutes les 10 secondes
async def send_random_id():
    while True:
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        await sio.emit('random_id', {'id': random_id})
        await asyncio.sleep(10)


# Événements Socket.IO
@sio.event
def my_event(sid, data):
    pass


@sio.event
async def connect(sid, environ, auth):
    print('connect ', sid)

@sio.event
async def disconnect(sid):
    print('disconnect ', sid)






# Démarrage de la tâche asynchrone au démarrage de l'application
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_random_id())

# Démarrage du serveur avec uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7000)