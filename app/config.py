# config.py
# Configurari pentru aplicatia de chat securizat
# Contine setarile pentru baza de date, sesiuni si criptare

import os
from datetime import timedelta

class Config:
    """
    Clasa de configurare pentru aplicatie.
    Foloseste variabile de mediu cu valori implicite pentru dezvoltare.
    """
    
    # Directorul radacina al aplicatiei
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Directorul pentru baza de date si fisiere uploadate
    # In Docker: /app/data, Local: ../data relativ la app/
    DATA_DIR = os.environ.get('DATA_DIR') or os.path.join(os.path.dirname(BASE_DIR), 'data')
    
    # Configurare baza de date SQLite
    # Folosim cale absoluta pentru a evita probleme cu working directory
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(DATA_DIR, "chat.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cheie secreta pentru sesiuni Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cheie-secreta-pentru-dezvoltare-schimba-in-productie'
    
    # Configurare JWT pentru autentificare
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-key-schimba-in-productie'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Directorul pentru fisiere uploadate
    UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limita 16MB pentru upload
    
    # Extensii permise pentru upload
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'log', 'csv', 'json', 'xml'}
    
    # Configurare criptare
    RSA_KEY_SIZE = 2048  # Dimensiune cheie RSA in biti
    AES_KEY_SIZE = 32    # Dimensiune cheie AES in bytes (256 biti)
    
    @staticmethod
    def init_app(app):
        """
        Initializeaza directoarele necesare pentru aplicatie.
        Creeaza directorul data si uploads daca nu exista.
        """
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
