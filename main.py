import asyncio
import json
import random
import string
import socketio
from fastapi import FastAPI
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import requests

from classType import FormData, JSON_Oject

# Création de l'application FastAPI
app = FastAPI()

# definition du middleware et des access
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Création du serveur Socket.IO avec les options CORS
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=["http://127.0.0.1:5500"],  # Ajoutez ici l'origine de votre frontend
    logger=True,
    engineio_logger=True,
    allow_eio3=True
)
socket_app = socketio.ASGIApp(sio)

# endpoint de depart juste utiliser pour tester le serveur socket io
@app.get("/")
def read_root():
    return {"message": "Welcome to the Monitoring GAME SOCKET API By RELOU"}

# Monter le serveur Socket.IO sur l'application FastAPI
app.mount("/", socket_app)

# Fonction pour envoyer un ID aléatoire toutes les 10 secondes
async def send_random_id():
    while True:
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        await sio.emit('random_id', {'id': random_id})
        await asyncio.sleep(3)

# GERE LE JEU     
# Fonction pour envoyer des données dans le fronts toutes les 10 secondes
async def send_data():
    while True:
        await sio.emit('get_data',{"state": "send"})
        await asyncio.sleep(10)

# Événements Socket.IO
@sio.event
def my_event(sid, data):
    pass

# qui permet de savoir si un utilisateur est connecté
@sio.event
async def connect(sid, environ, auth):
    print('connect ', sid)

# qui permet de savoir si un utilisateur est deconnecté
@sio.event
async def disconnect(sid):
    print('disconnect ', sid)

# cet ecouteur permet de savoir si la partie lanceur par le createur peut etre lancer 
@sio.on('game_verification')
async def verification_event(sid, data):
    dataState :  FormData  = data
    res = requests.post(url="http://127.0.0.1:5100/game-verification", json=dataState)
    await sio.emit('game_verification_data', data=res.json())

# GERE LE JEU
# cete ecouteur permet d'envoyer les données de jeu aux utilateurs
@sio.on('get_data_game')
async def getData(sid, data):
    dataset = JSON_Oject()
    dataset.gameId = data['gameId']
    dataset.first_user_token = data['first_user_token']
    dataset.second_user_token = data['second_user_token']
    dataset.tours = data['tours']
    
    # Convertir l'objet JSON_Oject en dictionnaire avant de l'envoyer
    dataset_dict = json.loads(dataset.toJSON())
    res = requests.post(url="http://127.0.0.1:5100/get-gamedata", json=dataset_dict)
    response = res.json()
    await sio.emit('get_data_game_data', data=response)
    
# GERE LE JEU
# cete ecouteur permet de sauvegarder la modification d'un  aux utilateurs
@sio.on('set_data_game')
async def getData(sid, data):
    dataset = JSON_Oject()
    dataset.gameId = data['gameId']
    dataset.first_user_token = data['first_user_token']
    dataset.second_user_token = data['second_user_token']
    dataset.tours = data['tours']
    
    # Convertir l'objet JSON_Oject en dictionnaire avant de l'envoyer
    dataset_dict = json.loads(dataset.toJSON())
    if dataset.second_user_token == "AI":
        res = requests.post(url="http://127.0.0.1:5100/update-ia-game", json=dataset_dict)
    else:
        res = requests.post(url="http://127.0.0.1:5100/update-gamedata", json=dataset_dict)
    response = res.json()
    print(response)

# Démarrage de la tâche asynchrone au démarrage de l'application
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_data()) # GERE LE JEU

# Démarrage du serveur avec uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=7000, reload=True)