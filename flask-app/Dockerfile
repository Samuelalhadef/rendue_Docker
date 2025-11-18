###########################################
# Dockerfile pour l'application Flask
# Ce fichier décrit comment construire l'image Docker
# contenant notre application Python/Flask.
###########################################

# Image de base légère avec Python 3.11
FROM python:3.11-slim

# Définit le répertoire de travail à l'intérieur du conteneur
# Toutes les commandes suivantes (COPY, RUN, etc.) s'exécutent depuis /app
WORKDIR /app

# Copier uniquement le fichier des dépendances d'abord (optimisation des couches)
# Cela permet de tirer parti du cache Docker lorsque seules les sources changent
COPY requirements.txt .

# Installer les dépendances Python listées dans requirements.txt
# --no-cache-dir réduit la taille de l'image en évitant de garder le cache pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application dans l'image
# (on pourrait copier un dossier entier si l'app grandit)
COPY app.py .

# Exposer le port que l'application Flask écoute à l'intérieur du conteneur
EXPOSE 5000

# Commande de démarrage du conteneur
# Ici l'app est démarrée avec l'interpréteur Python
CMD ["python", "app.py"]
