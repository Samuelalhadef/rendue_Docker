from flask import Flask, jsonify, request
import datetime
import os
import requests
import re
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_this_secret')

# Enable CORS for all routes
CORS(app)

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://mongodb:27017')
MONGO_DB = os.environ.get('MONGO_DB', 'hoteldb')

try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[MONGO_DB]
    users_col = db.users
except Exception:
    mongo_client = None
    db = None
    users_col = None


@app.route('/')
def home():
    return jsonify({
        'name': 'Docker Meteo API',
        'version': '1.0.0',
        'message': 'Bienvenue sur l\'API Docker Meteo 🌤️',
        'status': 'En ligne',
        'timestamp': datetime.datetime.now().isoformat(),
        'endpoints': [
            'POST /register - Créer un compte utilisateur',
            'POST /login - Se connecter',
            'GET /users - Liste des utilisateurs',
            'POST /chat - Chat météo intelligent'
        ],
        'features': [
            'Chat conversationnel avec IA',
            'Météo temps réel (Open-Meteo)',
            'Authentification utilisateurs',
            'Base de données MongoDB'
        ]
    })


# --------------------
# User management (MongoDB)
# --------------------


@app.route('/register', methods=['POST'])
def register():
    if users_col is None:
        return jsonify({'error': 'Database not available'}), 500
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    if users_col.find_one({'username': username}):
        return jsonify({'error': 'user already exists'}), 409
    pw_hash = generate_password_hash(password)
    user = {
        'username': username,
        'password': pw_hash,
        'created_at': datetime.datetime.utcnow().isoformat()
    }
    users_col.insert_one(user)
    return jsonify({'message': 'user registered', 'username': username}), 201


@app.route('/login', methods=['POST'])
def login():
    if users_col is None:
        return jsonify({'error': 'Database not available'}), 500
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'username and password required'}), 400
    user = users_col.find_one({'username': username})
    if not user or not check_password_hash(user.get('password', ''), password):
        return jsonify({'error': 'invalid credentials'}), 401
    return jsonify({'message': 'login success', 'username': username}), 200


@app.route('/users', methods=['GET'])
def list_users():
    if users_col is None:
        return jsonify({'error': 'Database not available'}), 500
    users = list(users_col.find({}, {'password': 0}))
    for u in users:
        u['_id'] = str(u.get('_id'))
    return jsonify({'users': users})


# --------------------
# Conversational Chat System with Weather
# --------------------

import random

# Chat personality and responses
GREETINGS = [
    "Bonjour ! 👋 Je suis votre assistant météo. Comment puis-je vous aider aujourd'hui ?",
    "Salut ! 😊 Ravi de vous voir ! Voulez-vous connaître la météo quelque part ?",
    "Hello ! ☀️ Prêt à découvrir la météo ? Quelle ville vous intéresse ?",
    "Coucou ! 🌤️ Je suis là pour vous parler météo ou simplement discuter !"
]

FAREWELLS = [
    "Au revoir ! 👋 À bientôt pour de nouvelles prévisions météo !",
    "À plus tard ! 😊 Prenez soin de vous et n'oubliez pas votre parapluie si besoin !",
    "Salut ! ☀️ Revenez quand vous voulez parler météo !",
    "Bye bye ! 🌈 Passez une excellente journée !"
]

HOW_ARE_YOU = [
    "Je vais très bien, merci ! ☀️ Prêt à vous donner toutes les infos météo dont vous avez besoin !",
    "Au top ! 🌤️ Il fait beau dans mon serveur Docker ! Et vous, comment allez-vous ?",
    "Je suis en pleine forme ! 💪 Mes algorithmes tournent à merveille. Parlons météo !",
    "Excellent ! 😊 Toujours prêt à discuter du temps qu'il fait. Et vous ?"
]

THANKS = [
    "De rien ! 😊 C'est toujours un plaisir de vous aider !",
    "Avec plaisir ! ☀️ N'hésitez pas si vous avez d'autres questions !",
    "Je suis là pour ça ! 🌤️ Revenez quand vous voulez !",
    "Tout le plaisir est pour moi ! 🎉"
]

JOKES = [
    "Quelle est la différence entre un nuage et un pull ? Le nuage, on le porte pas ! ☁️😄",
    "Pourquoi les poissons n'aiment pas jouer au tennis ? Parce qu'ils ont peur du filet... et de la pluie ! 🐟🎾",
    "Quel est le comble pour un nuage ? C'est de tomber en panne ! ☁️😂",
    "Comment appelle-t-on un chat qui vit dans l'igloo ? Un gla-gla-chat ! ❄️🐱"
]

COMPLIMENTS = [
    "Oh merci ! 😊 Vous êtes très gentil ! Je fais de mon mieux pour vous servir !",
    "C'est adorable ! 🥰 Vous rendez mon code tout chaud !",
    "Vous allez me faire bugger de bonheur ! 💙 Merci beaucoup !",
    "Merci ! 😄 Vous aussi vous êtes super ! Continuons cette belle conversation !"
]

ABOUT_ME = [
    "Je suis un assistant météo intelligent créé avec Flask et Python ! 🐍 J'utilise l'API Open-Meteo pour vous donner des prévisions en temps réel partout dans le monde ! 🌍",
    "Je m'appelle Docker Meteo Bot ! Je tourne dans un conteneur Docker et je peux vous donner la météo de n'importe quelle ville. Je sais aussi discuter un peu ! 😊",
    "Je suis votre chatbot météo personnel ! Alimenté par Open-Meteo API, je peux vous dire le temps qu'il fait partout sur Terre ! Et j'adore discuter ! 💬"
]

CAPABILITIES = [
    "Je peux vous donner la météo de n'importe quelle ville du monde ! 🌍 Demandez-moi juste 'Météo à Paris', 'Tokyo', ou 'Quel temps à New York ?'",
    "Mes super-pouvoirs : 🌤️ Météo temps réel partout dans le monde, 💬 Discussion sympathique, et 😄 quelques blagues de temps en temps !",
    "Je suis capable de récupérer la température, l'humidité, la vitesse du vent et les conditions météo pour toutes les villes ! Essayez-moi ! ⚡"
]

def detect_intent(message):
    """Detect user intent from message"""
    message_lower = message.lower().strip()

    # Greetings (check first with exact matches)
    greeting_words = ['bonjour', 'salut', 'hello', 'hey', 'coucou', 'bonsoir', 'hi', 'yo']
    if message_lower in greeting_words or any(message_lower.startswith(word) for word in greeting_words):
        return 'greeting'

    # Farewells
    farewell_words = ['au revoir', 'bye', 'salut', 'à bientôt', 'ciao', 'adieu', 'à plus']
    if any(word in message_lower for word in farewell_words) and len(message.split()) <= 4:
        return 'farewell'

    # How are you
    if any(phrase in message_lower for phrase in ['comment vas', 'comment allez', 'ça va', 'ca va', 'comment tu vas']):
        return 'how_are_you'

    # Thanks
    if any(word in message_lower for word in ['merci', 'thank', 'thanks', 'remercie']):
        return 'thanks'

    # Jokes
    if any(phrase in message_lower for phrase in ['blague', 'joke', 'rigole', 'marrant', 'drôle', 'humour']):
        return 'joke'

    # Compliments
    if any(word in message_lower for word in ['génial', 'super', 'cool', 'top', 'excellent', 'parfait', 'bravo', 'incroyable']):
        return 'compliment'

    # About bot
    if any(phrase in message_lower for phrase in ['qui es-tu', 'qui es tu', 'c\'est quoi', 'c est quoi', 'présente-toi', 'presente toi', 'ton nom']):
        return 'about'

    # Capabilities
    if any(phrase in message_lower for phrase in ['que peux-tu', 'que peux tu', 'tu sais faire', 'capacités', 'capacites', 'what can you']):
        return 'capabilities'

    # Weather - check for city names or weather keywords
    weather_keywords = ['météo', 'meteo', 'temps', 'température', 'temperature', 'weather', 'forecast', 'prévision', 'prevision']
    if any(keyword in message_lower for keyword in weather_keywords):
        return 'weather'

    # If message looks like a city name (short, capitalized words)
    if len(message.split()) <= 3 and not message_lower.startswith(('pourquoi', 'comment', 'quand', 'où', 'que', 'qui')):
        return 'weather'

    # Default to general conversation
    return 'general'

def get_general_response(message):
    """Generate response for general conversation"""
    message_lower = message.lower()

    # Questions about weather in general
    if 'pluie' in message_lower or 'pleut' in message_lower:
        return "La pluie, c'est important pour la nature ! 🌧️ Voulez-vous savoir s'il pleut quelque part en particulier ?"

    if 'neige' in message_lower:
        return "La neige, c'est magique ! ❄️ Voulez-vous savoir où il neige actuellement ?"

    if 'soleil' in message_lower:
        return "Le soleil, source de vie ! ☀️ Voulez-vous connaître l'ensoleillement d'une ville ?"

    # Questions
    if message_lower.startswith(('pourquoi', 'comment', 'quand', 'où', 'que')):
        return "C'est une excellente question ! 🤔 Je suis spécialisé dans la météo, donc pour y répondre précisément, demandez-moi la météo d'une ville ! Sinon, je peux juste discuter avec vous. 😊"

    # Default friendly response
    responses = [
        "Intéressant ! 🤔 Je suis surtout expert en météo. Voulez-vous connaître le temps qu'il fait quelque part ?",
        "Je vous écoute ! 👂 Mais je suis meilleur pour parler météo. Quelle ville vous intéresse ?",
        "C'est sympa d'en parler ! 😊 Au fait, besoin d'infos météo aujourd'hui ?",
        "Je comprends ! 💭 En tant qu'assistant météo, je peux vous aider avec les prévisions. Une ville en particulier ?",
        "Absolument ! ✨ N'hésitez pas à me demander la météo de n'importe quelle ville du monde !"
    ]
    return random.choice(responses)

def get_coordinates(city_name):
    """Get coordinates from city name using geocoding API"""
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=fr&format=json"
        res = requests.get(url, timeout=5)
        data = res.json()
        if 'results' in data and len(data['results']) > 0:
            result = data['results'][0]
            return {
                'name': result.get('name'),
                'country': result.get('country'),
                'lat': result.get('latitude'),
                'lon': result.get('longitude')
            }
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None


def get_weather(lat, lon):
    """Get weather data from Open-Meteo API"""
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&timezone=auto"
        res = requests.get(url, timeout=5)
        data = res.json()

        if 'current' in data:
            current = data['current']
            weather_codes = {
                0: "Ciel dégagé",
                1: "Principalement dégagé",
                2: "Partiellement nuageux",
                3: "Couvert",
                45: "Brouillard",
                48: "Brouillard givrant",
                51: "Bruine légère",
                53: "Bruine modérée",
                55: "Bruine dense",
                61: "Pluie légère",
                63: "Pluie modérée",
                65: "Pluie forte",
                71: "Neige légère",
                73: "Neige modérée",
                75: "Neige forte",
                95: "Orage",
                96: "Orage avec grêle"
            }

            weather_desc = weather_codes.get(current.get('weather_code', 0), "Non défini")

            return {
                'temperature': current.get('temperature_2m'),
                'humidity': current.get('relative_humidity_2m'),
                'feels_like': current.get('apparent_temperature'),
                'wind_speed': current.get('wind_speed_10m'),
                'description': weather_desc,
                'time': current.get('time')
            }
    except Exception as e:
        print(f"Weather API error: {e}")
    return None


def extract_city_from_message(message):
    """Extract city name from user message"""
    # Remove common words and patterns
    message_lower = message.lower()

    # Patterns to detect city queries
    patterns = [
        r'météo (?:à|a|de|pour|sur) ([a-zàâçéèêëîïôûùüÿñæœ\s-]+)',
        r'temps (?:à|a|de|pour|sur) ([a-zàâçéèêëîïôûùüÿñæœ\s-]+)',
        r'(?:à|a) ([a-zàâçéèêëîïôûùüÿñæœ\s-]+)',
        r'(?:ville|city)[\s:]+([a-zàâçéèêëîïôûùüÿñæœ\s-]+)',
        r'^([a-zàâçéèêëîïôûùüÿñæœ\s-]+)$',  # Just the city name
    ]

    for pattern in patterns:
        match = re.search(pattern, message_lower)
        if match:
            city = match.group(1).strip()
            # Remove common stop words at the end
            city = re.sub(r'\s+(\?|s\'il|svp|merci|please).*$', '', city)
            return city.title()

    return None


@app.route('/chat', methods=['POST'])
def chat():
    """Conversational chat endpoint with weather capabilities"""
    data = request.get_json() or {}
    message = data.get('message', '').strip()
    username = data.get('username')

    if not message:
        return jsonify({'error': 'Message required'}), 400

    if not username:
        return jsonify({'error': 'Authentication required'}), 401

    # Detect user intent
    intent = detect_intent(message)

    # Handle different intents
    if intent == 'greeting':
        return jsonify({
            'response': random.choice(GREETINGS),
            'type': 'conversation'
        })

    elif intent == 'farewell':
        return jsonify({
            'response': random.choice(FAREWELLS),
            'type': 'conversation'
        })

    elif intent == 'how_are_you':
        return jsonify({
            'response': random.choice(HOW_ARE_YOU),
            'type': 'conversation'
        })

    elif intent == 'thanks':
        return jsonify({
            'response': random.choice(THANKS),
            'type': 'conversation'
        })

    elif intent == 'joke':
        return jsonify({
            'response': random.choice(JOKES),
            'type': 'conversation'
        })

    elif intent == 'compliment':
        return jsonify({
            'response': random.choice(COMPLIMENTS),
            'type': 'conversation'
        })

    elif intent == 'about':
        return jsonify({
            'response': random.choice(ABOUT_ME),
            'type': 'conversation'
        })

    elif intent == 'capabilities':
        return jsonify({
            'response': random.choice(CAPABILITIES),
            'type': 'conversation'
        })

    elif intent == 'weather':
        # Extract city from message
        city_name = extract_city_from_message(message)

        if not city_name:
            return jsonify({
                'response': "Je n'ai pas compris quelle ville vous intéresse. 🤔\n\nPourriez-vous préciser ? Par exemple:\n- Météo à Paris\n- Quel temps à Tokyo ?\n- New York",
                'type': 'help'
            })

        # Get coordinates
        coords = get_coordinates(city_name)
        if not coords:
            return jsonify({
                'response': f"Désolé, je n'ai pas trouvé la ville '{city_name}'. 😕\n\nVérifiez l'orthographe ou essayez une autre ville !",
                'type': 'error'
            })

        # Get weather
        weather = get_weather(coords['lat'], coords['lon'])
        if not weather:
            return jsonify({
                'response': f"Oups ! Impossible de récupérer la météo pour {coords['name']}. 😔\n\nRéessayez dans quelques instants !",
                'type': 'error'
            })

        # Format response
        response = f"📍 **{coords['name']}, {coords['country']}**\n\n"
        response += f"🌡️ Température: {weather['temperature']}°C\n"
        response += f"🤔 Ressenti: {weather['feels_like']}°C\n"
        response += f"💧 Humidité: {weather['humidity']}%\n"
        response += f"💨 Vent: {weather['wind_speed']} km/h\n"
        response += f"☁️ Conditions: {weather['description']}\n\n"
        response += f"_Données de Open-Meteo • Mise à jour: {weather['time']}_"

        return jsonify({
            'response': response,
            'type': 'weather',
            'data': {
                'city': coords['name'],
                'country': coords['country'],
                'weather': weather
            }
        })

    else:  # general conversation
        return jsonify({
            'response': get_general_response(message),
            'type': 'conversation'
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
