import os
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from passlib.context import CryptContext
import secrets
from typing import Optional

# Configuration de la base de données
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/fastapi_db"
)

# Pour SQLite en-mémoire, il faut check_same_thread=False
if "sqlite" in DATABASE_URL:
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuration de sécurité
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modèle de base de données
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    token = Column(String, nullable=True, unique=True, index=True)

# NOTE: Ne pas appeler Base.metadata.create_all() ici car il peut être
# appelé avant que le conftest.py ait la chance de reconfigurer l'engine
# Les tables seront créées lors du démarrage de l'app ou dans les tests

# Modèles Pydantic
class UserSignup(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    token: str

    class Config:
        from_attributes = True

# Dépendance pour la base de données
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Fonction pour créer les tables
def init_db():
    """Créer les tables de la base de données"""
    Base.metadata.create_all(bind=engine)

# Fonctions utilitaires
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def generate_token() -> str:
    return secrets.token_urlsafe(32)

def verify_token(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Authorization header missing",
        )
    
    # Extraire le token du header "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    token = parts[1]
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Application FastAPI
app = FastAPI(title="FastAPI Auth API", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permettre toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Permettre tous les méthodes (GET, POST, etc.)
    allow_headers=["*"],  # Permettre tous les headers
)

@app.on_event("startup")
def startup_event():
    """Initialiser les tables au démarrage"""
    init_db()

@app.post("/signup", response_model=UserResponse)
def signup(user: UserSignup, db: Session = Depends(get_db)):
    """
    Endpoint pour créer un nouveau compte utilisateur.
    """
    # Vérifier si l'email existe déjà
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Créer le nouvel utilisateur
    hashed_password = hash_password(user.password)
    token = generate_token()
    
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        token=token
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        email=new_user.email,
        token=new_user.token
    )

@app.post("/login", response_model=UserResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Endpoint pour se connecter et obtenir un token.
    """
    # Chercher l'utilisateur par email
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Générer un nouveau token
    new_token = generate_token()
    db_user.token = new_token
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        token=db_user.token
    )

@app.get("/protected")
def protected_route(user: User = Depends(verify_token)):
    """
    Endpoint protégé qui nécessite un token valide.
    """
    return {"message": f"Hello {user.email}!"}

@app.get("/health")
def health_check():
    """
    Endpoint de health check.
    """
    return {"status": "ok"}
