"""
Fichier de configuration pour les tests
"""
import sys
from pathlib import Path
import pytest
import os
import tempfile

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Créer un fichier temporaire pour la BD SQLite au lieu d'utiliser :memory:
# car :memory: crée une base différente par thread avec TestClient
_temp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_temp_db_path = _temp_db.name
_temp_db.close()

os.environ["DATABASE_URL"] = f"sqlite:///{_temp_db_path}"

# Importer après avoir défini les variables d'environnement
from main import app, get_db, User, init_db
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import engine as test_engine

# Créer les tables AU CHARGEMENT du conftest
init_db()

# Créer une nouvelle SessionLocal avec le bon engine
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Override get_db dependency pour utiliser la nouvelle SessionLocal
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Fournir le TestClient pour chaque test"""
    return TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_db():
    """Nettoyer les données après chaque test"""
    yield
    # Supprimer tous les utilisateurs après le test
    db = TestingSessionLocal()
    try:
        db.query(User).delete()
        db.commit()
    finally:
        db.close()

@pytest.fixture(scope="session", autouse=True)
def cleanup_temp_db():
    """Nettoyer le fichier temporaire à la fin de la session"""
    yield
    # Supprimer le fichier temporaire
    try:
        os.unlink(_temp_db_path)
    except:
        pass
