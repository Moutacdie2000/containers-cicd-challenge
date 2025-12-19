import pytest
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Ces imports doivent venir après le conftest setup
from main import app, User, verify_token
from fastapi.testclient import TestClient

# client est importé depuis le conftest qui l'a déjà configuré
# On le récupère depuis les fixtures
@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)

class TestSignup:
    """Tests pour l'endpoint /signup"""
    
    def test_signup_success(self, client):
        """Test 1: Création d'un compte utilisateur avec succès"""
        response = client.post(
            "/signup",
            json={"email": "test@example.com", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "token" in data
        assert "id" in data
    
    def test_signup_duplicate_email(self, client):
        """Test 2: Impossible de créer deux comptes avec le même email"""
        # Créer le premier compte
        client.post(
            "/signup",
            json={"email": "duplicate@example.com", "password": "password123"}
        )
        # Essayer de créer un deuxième compte avec le même email
        response = client.post(
            "/signup",
            json={"email": "duplicate@example.com", "password": "password456"}
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

class TestLogin:
    """Tests pour l'endpoint /login"""
    
    def test_login_success(self, client):
        """Test 3: Connexion réussie avec les bonnes identifiants"""
        # D'abord créer un compte
        client.post(
            "/signup",
            json={"email": "login@example.com", "password": "mypassword"}
        )
        
        # Ensuite se connecter
        response = client.post(
            "/login",
            json={"email": "login@example.com", "password": "mypassword"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "login@example.com"
        assert "token" in data
    
    def test_login_invalid_password(self, client):
        """Test 4: Impossible de se connecter avec un mauvais mot de passe"""
        # Créer un compte
        client.post(
            "/signup",
            json={"email": "invalid@example.com", "password": "correctpassword"}
        )
        
        # Essayer de se connecter avec le mauvais mot de passe
        response = client.post(
            "/login",
            json={"email": "invalid@example.com", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]

class TestProtectedRoute:
    """Tests pour les routes protégées"""
    
    def test_protected_route_with_valid_token(self, client):
        """Test 5: Accès à une route protégée avec un token valide"""
        # Créer un compte et obtenir un token
        signup_response = client.post(
            "/signup",
            json={"email": "protected@example.com", "password": "password123"}
        )
        token = signup_response.json()["token"]
        
        # Accéder à la route protégée
        response = client.get(
            "/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert "Hello protected@example.com!" in response.json()["message"]
    
    def test_protected_route_without_token(self, client):
        """Test 6: Impossible d'accéder à une route protégée sans token"""
        response = client.get("/protected")
        assert response.status_code == 403

class TestHealthCheck:
    """Tests pour l'endpoint de health check"""
    
    def test_health_check(self, client):
        """Test 7: Le health check retourne le statut ok"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
