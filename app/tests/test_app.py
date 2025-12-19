import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, Base, get_db, User, verify_token

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_verify_token(authorization: str = None):
    """Override pour les tests - parse le token manuellement"""
    db = TestingSessionLocal()
    try:
        if not authorization:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Authorization header missing",
            )
        
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
            )
        
        token = parts[1]
        user = db.query(User).filter(User.token == token).first()
        if not user:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[verify_token] = override_verify_token

client = TestClient(app)

class TestSignup:
    """Tests pour l'endpoint /signup"""
    
    def test_signup_success(self):
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
    
    def test_signup_duplicate_email(self):
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
    
    def test_login_success(self):
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
    
    def test_login_invalid_password(self):
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
    
    def test_protected_route_with_valid_token(self):
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
    
    def test_protected_route_without_token(self):
        """Test 6: Impossible d'accéder à une route protégée sans token"""
        response = client.get("/protected")
        assert response.status_code == 403

class TestHealthCheck:
    """Tests pour l'endpoint de health check"""
    
    def test_health_check(self):
        """Test 7: Le health check retourne le statut ok"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
