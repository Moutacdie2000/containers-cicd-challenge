# Utiliser une image Python officielle
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les exigences
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
