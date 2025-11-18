from flask import Flask, jsonify
import datetime

app = Flask(__name__)

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
            '/services - Services de l\'hôtel'
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
            '/services - Liste des services'
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
