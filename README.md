# 🏢 Reverse Proxy avec Nginx - Projet Docker

## 📋 Description du Projet

Ce projet démontre l'utilisation d'un **reverse proxy Nginx** pour router le trafic entre deux applications web :
- **Flask App (API)** - Une application Python Flask servant une API REST
- **HTML App (Site statique)** - Un site HTML statique

### 🎯 La Métaphore de l'Immeuble

Imagine un **immeuble** avec un **réceptionniste** (Nginx) qui dirige les visiteurs :
- 🏢 **Bureau 101** → Application Flask (API Backend)
- 🏢 **Bureau 102** → Site HTML statique (Frontend)
- 👔 **Réceptionniste** → Nginx (Reverse Proxy)

Le réceptionniste écoute à la porte d'entrée (port 80) et redirige chaque visiteur vers le bon bureau selon ce qu'il demande.

---

## 📁 Structure du Projet

```
rendue_Docker/
├── docker-compose.yml              # Orchestration des 3 services
├── nginx/
│   └── default.conf               # Configuration du reverse proxy
├── flask-app/
│   ├── app.py                     # Application Flask
│   ├── requirements.txt           # Dépendances Python
│   └── Dockerfile                 # Image Docker Flask
└── html-app/
    └── index.html                 # Site HTML statique
```

---

## 🚀 Comment Lancer le Projet

### Prérequis
- Docker installé
- Docker Compose installé

### 1. Lancer tous les services

```bash
docker-compose up --build
```

Cette commande va :
1. Construire l'image Docker pour Flask
2. Télécharger les images Nginx
3. Démarrer les 3 conteneurs
4. Créer un réseau pour qu'ils communiquent

### 2. Vérifier que tout fonctionne

Ouvre ton navigateur et teste ces URLs :

| Route | Description | URL |
|-------|-------------|-----|
| **Accueil** | Page d'accueil du proxy | http://localhost/ |
| **API Flask** | Endpoint hello de l'API | http://localhost/api/hello |
| **API Flask Info** | Informations sur l'API | http://localhost/api/info |
| **Site HTML** | Site statique | http://localhost/site/ |

---

## 🔍 Comment ça Fonctionne ?

### Le Flux de Requête

```
Navigateur
    ↓
http://localhost/api/hello
    ↓
Nginx (port 80) 🚪
    ↓
"Je vois /api/, je redirige vers flask-app"
    ↓
Flask App (port 5000 interne)
    ↓
Réponse JSON
    ↓
Nginx
    ↓
Navigateur
```

### Configuration Nginx (le cerveau du réceptionniste)

```nginx
# Route /api/ → Flask App
location /api/ {
    proxy_pass http://flask-app:5000/;
}

# Route /site/ → HTML App
location /site/ {
    proxy_pass http://html-app:80/;
}
```

**Explication** :
- `proxy_pass` = "Redirige la requête vers..."
- `http://flask-app:5000/` = Nom du service Docker + port interne
- Les noms (`flask-app`, `html-app`) sont définis dans `docker-compose.yml`

---

## 🧪 Tester les Endpoints

### Avec un Navigateur
- Accueil : http://localhost/
- API : http://localhost/api/hello
- Site : http://localhost/site/

### Avec curl (en ligne de commande)

```bash
# Tester l'API Flask
curl http://localhost/api/hello

# Tester le site HTML
curl http://localhost/site/

# Tester l'endpoint info
curl http://localhost/api/info
```

---

## 🛠️ Commandes Utiles

### Démarrer en arrière-plan
```bash
docker-compose up -d
```

### Voir les logs
```bash
# Tous les services
docker-compose logs -f

# Seulement Flask
docker-compose logs -f flask-app

# Seulement Nginx
docker-compose logs -f nginx
```

### Arrêter les services
```bash
docker-compose down
```

### Reconstruire après modification
```bash
docker-compose up --build
```

### Voir les conteneurs actifs
```bash
docker-compose ps
```

---

## 📊 Architecture Réseau

```
┌─────────────────────────────────────────┐
│         Réseau: app-network             │
│  ┌─────────────────────────────────┐    │
│  │   Nginx (nginx-proxy)           │    │
│  │   Port exposé: 80               │    │
│  │   Rôle: Reverse Proxy           │    │
│  └──────────┬────────────┬─────────┘    │
│             │            │               │
│    ┌────────▼────┐  ┌───▼─────────┐     │
│    │ Flask-App   │  │  HTML-App   │     │
│    │ Port: 5000  │  │  Port: 80   │     │
│    │ /api/*      │  │  /site/*    │     │
│    └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────┘
```

---

## 🎓 Ce que tu Apprends

1. **Reverse Proxy** : Comment Nginx route les requêtes
2. **Docker Compose** : Orchestrer plusieurs conteneurs
3. **Réseau Docker** : Communication entre conteneurs
4. **Séparation des services** : API backend + frontend statique
5. **Configuration Nginx** : proxy_pass, locations, headers

---

## 🐛 Dépannage

### Le port 80 est déjà utilisé
**Erreur** : `Bind for 0.0.0.0:80 failed: port is already allocated`

**Solution** : Change le port dans `docker-compose.yml` :
```yaml
nginx:
  ports:
    - "8080:80"  # Utilise le port 8080 au lieu de 80
```
Puis accède à http://localhost:8080/

### Les conteneurs ne se trouvent pas
**Erreur** : `flask-app could not be resolved`

**Solution** : Vérifie que tous les services sont sur le même réseau dans `docker-compose.yml`

### Modifications non prises en compte
**Solution** : Rebuild les images :
```bash
docker-compose down
docker-compose up --build
```

---

## 📝 Exercices pour Aller Plus Loin

1. **Ajouter un nouveau service** :
   - Crée une 3ème application (par ex. Node.js)
   - Ajoute-la à `docker-compose.yml`
   - Configure Nginx pour router vers `/node/`

2. **Ajouter HTTPS** :
   - Configure des certificats SSL
   - Modifie Nginx pour écouter sur le port 443

3. **Load Balancing** :
   - Lance plusieurs instances de Flask
   - Configure Nginx pour répartir la charge

4. **Logging** :
   - Configure les logs Nginx personnalisés
   - Ajoute un service ELK pour centraliser les logs

---

## 🎉 Résultat Attendu

Une fois lancé, tu peux :
- ✅ Visiter http://localhost/ → Voir la page d'accueil
- ✅ Visiter http://localhost/api/hello → Recevoir du JSON de Flask
- ✅ Visiter http://localhost/site/ → Voir le site HTML coloré
- ✅ Comprendre comment un reverse proxy fonctionne

---

## 📚 Ressources

- [Documentation Nginx](https://nginx.org/en/docs/)
- [Documentation Docker Compose](https://docs.docker.com/compose/)
- [Documentation Flask](https://flask.palletsprojects.com/)

---

**Créé avec ❤️ pour apprendre Docker et Nginx**
