from flask import Flask, jsonify, request
import datetime
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_this_secret')

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
        'hotel': 'Hôtel API - Le Grand Immeuble',
        'message': 'Bienvenue à la réception de l\'Hôtel API 🏨',
        'etage': '2 - Suites Exécutives',
        'status': 'Ouvert 24/7',
        'concierge': 'À votre service',
        'timestamp': datetime.datetime.now().isoformat(),
        'services_disponibles': [
            '/hello - Accueil de la réception',
            '/info - Informations sur l\'hôtel',
            '/rooms - Voir les chambres disponibles',
            '/services - Services de l\'hôtel',
            '/register - Enregistrer un utilisateur (POST)',
            '/login - Authentifier un utilisateur (POST)'
        ]
    })


@app.route('/hello')
def hello():
    return jsonify({
        'hotel': 'Hôtel API',
        'message': 'Bonjour et bienvenue! 🎩',
        'accueil': 'Votre concierge virtuel vous souhaite un excellent séjour',
        'etage': '2 - Suites Exécutives',
        'description': 'L\'hôtel le plus luxueux du Grand Immeuble',
        'specialite': 'Hébergement de données JSON premium',
        'timestamp': datetime.datetime.now().isoformat(),
        'note': 'Vous avez été dirigé ici par notre réceptionniste Nginx depuis la route /api/'
    })


@app.route('/info')
def info():
    return jsonify({
        'nom': 'Hôtel API - Le Grand Immeuble',
        'type': 'API REST Backend',
        'framework': 'Flask (Python)',
        'version': '2.0.0',
        'etoiles': '⭐⭐⭐⭐⭐',
        'description': 'Hôtel de données premium situé à l\'étage 2 du Grand Immeuble',
        'emplacement': {
            'etage': 2,
            'section': 'Suites Exécutives',
            'acces': 'Via reverse proxy Nginx route /api/'
        },
        'services': [
            'Hébergement JSON 24/7',
            'Service de données rapide',
            'Concierge API automatique',
            'Sécurité par conteneur Docker'
        ],
        'endpoints_disponibles': [
            '/ - Réception principale',
            '/hello - Accueil personnalisé',
            '/info - Informations complètes',
            '/rooms - Chambres disponibles',
            '/services - Liste des services',
            '/register - Enregistrer un utilisateur (POST)',
            '/login - Authentifier un utilisateur (POST)'
        ],
        'technologie': {
            'conteneur': 'Docker',
            'reverse_proxy': 'Nginx',
            'reseau': 'app-network bridge'
        }
    })


@app.route('/rooms')
def rooms():
    return jsonify({
        'hotel': 'Hôtel API',
        'chambres_disponibles': [
            {
                'numero': 201,
                'type': 'Suite JSON',
                'prix': '50 requêtes/jour',
                'equipements': ['Réponse rapide', 'Format structuré', 'Clés personnalisées']
            },
            {
                'numero': 202,
                'type': 'Suite REST',
                'prix': '100 requêtes/jour',
                'equipements': ['GET/POST support', 'Headers personnalisés', 'CORS activé']
            },
            {
                'numero': 203,
                'type': 'Penthouse API',
                'prix': 'Illimité',
                'equipements': ['Tous les verbes HTTP', 'WebSocket', 'GraphQL ready']
            }
        ],
        'message': 'Toutes nos chambres offrent une vue sur le réseau Docker',
        'timestamp': datetime.datetime.now().isoformat()
    })


@app.route('/services')
def services():
    return jsonify({
        'hotel': 'Hôtel API',
        'services_premium': {
            'petit_dejeuner': 'Données fraîches servies chaque matin',
            'room_service': 'Livraison de JSON à la demande',
            'concierge': 'Assistance API 24/7',
            'spa': 'Optimisation et cache des réponses',
            'parking': 'Stockage de données sécurisé',
            'wifi': 'Connexion haute vitesse via réseau Docker'
        },
        'note': 'Tous les services sont inclus dans votre conteneur Docker',
        'timestamp': datetime.datetime.now().isoformat()
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


@app.route('/users/<username>', methods=['DELETE'])
def delete_user(username):
    if users_col is None:
        return jsonify({'error': 'Database not available'}), 500
    res = users_col.delete_one({'username': username})
    if res.deleted_count:
        return jsonify({'message': 'deleted'}), 200
    return jsonify({'error': 'not found'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
