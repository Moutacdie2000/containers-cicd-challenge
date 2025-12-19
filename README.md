# 🎯 FastAPI Authentication & PostgreSQL Backend with CI/CD

Une application backend FastAPI moderne avec authentification sécurisée, base de données PostgreSQL, tests unitaires complets et pipeline CI/CD automatisé avec GitHub Actions.

**Scalyz 30 Days Job-Ready Challenge — Chapter 3: Containers & CI/CD Pipelines**

---

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Tests](#-tests)
- [Docker & Docker Compose](#-docker--docker-compose)
- [Pipeline CI/CD](#-pipeline-cicd)
- [API Endpoints](#-api-endpoints)
- [Sécurité](#-sécurité)
- [Structure du projet](#-structure-du-projet)

## ✨ Fonctionnalités

✅ **Authentification sécurisée** : Enregistrement et connexion avec hachage bcrypt  
✅ **Base de données PostgreSQL** : Stockage persistant des utilisateurs  
✅ **Routes protégées** : Accès via token Bearer  
✅ **Tests unitaires** : 7+ tests couvrant les cas d'usage principaux  
✅ **Conteneurisation Docker** : Build et exécution isolée  
✅ **Docker Compose** : Orchestration locale FastAPI + PostgreSQL  
✅ **Pipeline CI/CD** : GitHub Actions automatisée (tests → build → push)  
✅ **Health checks** : Monitoring de la santé de l'application  
✅ **Variables d'environnement** : Configuration sans secrets en dur  

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│           GitHub Actions (CI/CD Pipeline)           │
│  - Tests unitaires                                   │
│  - Build Docker image                                │
│  - Push vers registre (si main)                      │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│              Docker Compose (Local)                  │
│                                                     │
│  ┌──────────────────┐      ┌──────────────────┐   │
│  │   FastAPI App    │ ←──→ │   PostgreSQL 15  │   │
│  │  (Python 3.10)   │      │   (Port: 5432)   │   │
│  │  (Port: 8000)    │      │                  │   │
│  └──────────────────┘      └──────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 📦 Prérequis

### Développement local
- **Python** 3.10+
- **pip** (gestionnaire de paquets Python)
- **PostgreSQL** 15+ (ou utiliser Docker Compose)

### Conteneurisation
- **Docker** 20.10+
- **Docker Compose** 2.0+

### CI/CD
- **GitHub Actions** (intégré dans ce repository)

## 🚀 Installation

### 1. Cloner le repository

```bash
git clone https://github.com/Moutacdie2000/containers-cicd-challenge.git
cd containers-cicd-challenge
```

### 2. Installation locale (sans Docker)

#### Créer un environnement virtuel

```bash
python3.10 -m venv venv
source venv/bin/activate  # sur Linux/macOS
# ou
venv\Scripts\activate  # sur Windows
```

#### Installer les dépendances

```bash
cd app
pip install -r requirements.txt
```

#### Configurer la base de données

```bash
# Option 1 : PostgreSQL local
export DATABASE_URL="postgresql://user:password@localhost:5432/fastapi_db"

# Option 2 : Base de données SQLite (tests)
# Laisser DATABASE_URL vide, la valeur par défaut sera utilisée
```

#### Démarrer l'application

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

L'application sera accessible sur `http://localhost:8000`

## 🐳 Docker & Docker Compose

### Démarrer l'application avec Docker Compose

```bash
cd docker

# Créer un fichier .env (optionnel - les valeurs par défaut sont définies)
echo "DB_USER=postgres" > .env
echo "DB_PASSWORD=postgres" >> .env
echo "DB_NAME=fastapi_db" >> .env

# Démarrer les services
docker-compose up -d

# Vérifier l'état des services
docker-compose ps

# Voir les logs
docker-compose logs -f api
docker-compose logs -f postgres
```

#### Arrêter les services

```bash
cd docker
docker-compose down

# Supprimer aussi les volumes (données)
docker-compose down -v
```

### Variables d'environnement pour Docker

Créez un fichier `.env` dans le répertoire `docker/` :

```env
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=fastapi_db
```

**⚠️ IMPORTANT** : Ne jamais commiter le fichier `.env` ! Ajouter à `.gitignore` :

```
docker/.env
app/.env
.env
```

## 💻 Utilisation

### Health Check

```bash
curl http://localhost:8000/health
# Réponse: {"status":"ok"}
```

### Inscription (Sign Up)

```bash
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure_password123"}'

# Réponse:
# {
#   "id": 1,
#   "email": "user@example.com",
#   "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
# }
```

### Connexion (Login)

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure_password123"}'

# Réponse:
# {
#   "id": 1,
#   "email": "user@example.com",
#   "token": "new_token_here"
# }
```

### Accès à une route protégée

```bash
curl -H "Authorization: Bearer <votre_token>" \
  http://localhost:8000/protected

# Réponse:
# {"message": "Hello user@example.com!"}
```

## 🧪 Tests

### Exécuter les tests unitaires

```bash
cd app

# Installer les dépendances de test
pip install -r requirements.txt

# Exécuter les tests
pytest tests/ -v

# Exécuter avec couverture
pytest tests/ -v --cov=main
```

### Couverture des tests

Les tests couvrent :

- ✅ **Test 1** : Inscription réussie
- ✅ **Test 2** : Rejet d'email dupliqué
- ✅ **Test 3** : Connexion réussie
- ✅ **Test 4** : Rejet de mot de passe incorrect
- ✅ **Test 5** : Accès à route protégée avec token valide
- ✅ **Test 6** : Rejet de route protégée sans token
- ✅ **Test 7** : Health check

## 🔄 Pipeline CI/CD

### Flux de travail GitHub Actions

Le pipeline s'exécute sur :
- **Push** vers `main` ou `develop`
- **Pull requests** vers `main` ou `develop`

### Étapes du pipeline

1. **Job "test"** : Lance les tests unitaires
   - Python 3.10
   - PostgreSQL service container
   - Installation des dépendances
   - Exécution de pytest

2. **Job "build"** : Build et push l'image Docker
   - Crée l'image Docker
   - Pousse vers `ghcr.io` (si branche `main`)
   - Utilise le cache Docker pour accélérer

3. **Job "docker-compose-test"** : Teste avec docker-compose
   - Démarre tous les services
   - Vérifie le health check
   - Nettoie les ressources

### Configuration GitHub Secrets

Aucun secret requis ! Le pipeline utilise :
- `secrets.GITHUB_TOKEN` (fourni automatiquement par GitHub)
- Variables d'environnement non sensibles

### Afficher le statut du pipeline

Consultez l'onglet **Actions** de votre repository GitHub pour voir :
- État des jobs
- Logs détaillés
- Historique des exécutions

## 📡 API Endpoints

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| `GET` | `/health` | Vérifier la santé de l'app | ❌ |
| `POST` | `/signup` | Créer un nouveau compte | ❌ |
| `POST` | `/login` | Se connecter et obtenir un token | ❌ |
| `GET` | `/protected` | Route protégée (exemple) | ✅ |

## 🔐 Sécurité

### Bonnes pratiques implémentées

✅ **Hachage des mots de passe** : Utilise bcrypt avec salting  
✅ **Tokens sécurisés** : Tokens URL-safe aléatoires (32+ caractères)  
✅ **Variables d'environnement** : Aucun secret en dur dans le code  
✅ **Authentification Bearer** : Tokens dans les headers HTTP  
✅ **Validation des données** : Pydantic pour validation stricte  
✅ **Health checks PostgreSQL** : Vérification de la connectivité

### À faire en production

⚠️ Utiliser JWT (JSON Web Tokens) au lieu de tokens simples  
⚠️ Ajouter HTTPS/TLS  
⚠️ Implémenter rate limiting  
⚠️ Ajouter logging et monitoring  
⚠️ Configurer CORS si nécessaire  
⚠️ Utiliser Azure Key Vault ou HashiCorp Vault pour les secrets

## 📁 Structure du projet

```
containers-cicd-challenge/
├── app/                                    # Code de l'application
│   ├── main.py                            # Application FastAPI
│   ├── requirements.txt                   # Dépendances Python
│   └── tests/
│       └── test_app.py                    # Tests unitaires
│
├── docker/                                 # Configuration Docker
│   ├── Dockerfile                         # Image Docker
│   └── docker-compose.yml                 # Orchestration locale
│
├── .github/
│   └── workflows/
│       └── ci.yml                         # Pipeline GitHub Actions
│
├── docs/
│   └── decision-log.md                    # Décisions techniques
│
├── README.md                               # Ce fichier
├── LICENSE                                 # Licence du projet
├── CODE_OF_CONDUCT.md                     # Code de conduite
├── CONTRIBUTING.md                        # Guide de contribution
├── SECURITY.md                            # Politique de sécurité
└── SUPPORT.md                             # Support
```

## 🔧 Développement

### Ajouter une nouvelle dépendance

```bash
cd app
pip install package_name
pip freeze > requirements.txt
```

### Ajouter de nouveaux tests

```bash
# Éditer app/tests/test_app.py et ajouter des tests
# Puis exécuter:
pytest tests/ -v
```

### Modifier la base de données

1. Éditer le modèle `User` dans `app/main.py`
2. Recréer les tables :
   ```python
   Base.metadata.drop_all(bind=engine)
   Base.metadata.create_all(bind=engine)
   ```

## 🐛 Troubleshooting

### Erreur : `Connection refused` PostgreSQL

**Cause** : PostgreSQL n'est pas en cours d'exécution

**Solution** :
```bash
# Avec Docker Compose
cd docker
docker-compose up -d postgres

# Ou vérifier la connexion
psql -h localhost -U postgres -d fastapi_db
```

### Erreur : Port `8000` déjà utilisé

**Solution** :
```bash
# Trouver le processus utilisant le port
lsof -i :8000

# Ou utiliser un autre port
uvicorn main:app --port 8001
```

### Erreur : Dépendances manquantes

**Solution** :
```bash
cd app
pip install -r requirements.txt
```

### Tests échouent en local mais passent en CI

**Cause** : Variables d'environnement différentes

**Solution** :
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/fastapi_db"
pytest tests/ -v
```

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 📝 Licence

Ce projet est sous licence MIT - voir [LICENSE](LICENSE)

## 👥 Contribution

Les contributions sont bienvenues ! Veuillez consulter [CONTRIBUTING.md](CONTRIBUTING.md)

## 🆘 Support

Pour toute question, veuillez consulter [SUPPORT.md](SUPPORT.md)

---

**Créé avec ❤️ pour les ingénieurs backend et DevOps**

- Implement a FastAPI app (`/signup` and `/login` routes).
- Write at least **two unit tests** for the app.
- Containerize the app with a `Dockerfile`.
- Use `docker-compose.yml` to run the app with PostgreSQL.
- Store DB connection info via environment variables.
- Add a GitHub Actions workflow (`ci.yml`) that:
  - Installs dependencies.
  - Runs unit tests.
  - Builds the Docker image.
  - Runs containers (FastAPI + Postgres).
- Ensure **secrets are not hardcoded** in the code or workflow.
- Document all steps in `README.md`.

---

## 📦 Structure

You will work inside the provided repo structure:

```

containers-cicd-challenge/
├── app/
│   ├── main.py
│   ├── requirements.txt
│   └── tests/
│       └── test\_app.py
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── decision-log.md
└── README.md

```

---

## ⚙️ Constraints

- Use Python 3.10+ and FastAPI.
- PostgreSQL via Docker Compose.
- No secrets committed to code (use environment variables).
- Pipeline must run **headless** (no manual prompts).
- A fresh clone + `docker-compose up` must work without extra steps.

---

## 🔍 Evaluation Process

1. Submit a Pull Request to this repository.
2. **GitHub Actions** will:
   - Run lint checks and unit tests.
   - Build the Docker image.
   - Start containers via Compose.
3. **Community Review**:
   - At least 2 peers review your PR.
   - Feedback focuses on code quality, containerization best practices, CI/CD correctness, and security.
4. **Approval & Tagging**:
   - Approved PRs are tagged and merged into the main branch.

---

## 📌 Tips for Success

- Review existing PRs before starting — you’ll learn faster.
- Keep commits small and descriptive.
- Document your design choices in `docs/decision-log.md`.
- Ask questions in the Scalyz community.
- Remember: this is about **building the habit** of shipping professional-grade work.

---

## 🚀 Your Next Step

- Fork the repo:
  ```bash
  git clone https://github.com/scalyz-community/containers-cicd-challenge.git
  ```

* Work on your solution locally.
* Submit your PR when ready.

Let’s see what you can build.
Prove it — to the community, to future employers, and to yourself.

---

**— Scalyz Community**
_Engineer. Collaborate. Deliver._

---

## ✅ Pre-Submission Checklist

Before you open a Pull Request, confirm that you have completed all items below.
**Tip:** Copy this checklist into your PR description and tick each item.

### 🔹 Functional Requirements

- [ ] FastAPI app with `/signup` and `/login` routes implemented.
- [ ] At least 2 unit tests written and passing.
- [ ] Dockerfile builds the app image successfully.
- [ ] docker-compose runs app + Postgres together.
- [ ] GitHub Actions workflow runs tests and builds the image.
- [ ] Secrets stored via environment variables (not hardcoded).

### 🔹 Code Quality & Structure

- [ ] Repo structure matches provided scaffolding.
- [ ] Code is modular and documented.
- [ ] Tests are clear and reproducible.
- [ ] No unused files or dependencies.

### 🔹 Documentation

- [ ] `README.md` includes setup and execution instructions.
- [ ] `docs/decision-log.md` explains tool choices and design decisions.
- [ ] Environment variables and ports are documented.

### 🔹 Git & Collaboration

- [ ] Commits are small and descriptive.
- [ ] Branch name is descriptive (e.g., `feature/fastapi-auth`).
- [ ] I have reviewed at least one existing PR in the repository.
- [ ] I am ready to respond to reviewer feedback in the PR discussion.

---

**Reminder:** This is a public community assignment.
Approved solutions will be tagged and remain visible as part of your **public engineering portfolio**.
