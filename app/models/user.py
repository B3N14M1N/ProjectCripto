# models/user.py
# Model pentru utilizatori - gestioneaza conturile si cheile de criptare
# Fiecare utilizator are o pereche de chei RSA (publica/privata)

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    """
    Model pentru utilizatori.
    
    Responsabilitati:
    - Stocare date cont (username, email, parola hash)
    - Stocare chei RSA pentru criptare end-to-end
    - Cheia privata este criptata cu parola utilizatorului
    
    Atribute:
        id: Identificator unic
        username: Nume utilizator unic pentru login si cautare
        email: Adresa email unica
        password_hash: Hash bcrypt al parolei
        public_key: Cheia publica RSA in format PEM (vizibila pentru toti)
        private_key_encrypted: Cheia privata RSA criptata cu parola utilizatorului
        avatar_color: Culoare pentru avatar generat
        created_at: Data crearii contului
        last_seen: Ultima activitate a utilizatorului
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Chei RSA pentru criptare asimetrica
    # Cheia publica este accesibila pentru oricine (pentru a cripta mesaje catre acest utilizator)
    public_key = db.Column(db.Text, nullable=True)
    # Cheia privata este criptata cu parola utilizatorului pentru securitate suplimentara
    private_key_encrypted = db.Column(db.Text, nullable=True)
    
    # Personalizare profil - culoare pentru avatar generat automat
    avatar_color = db.Column(db.String(7), default='#3B82F6')
    
    # Timestamp-uri pentru activitate
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relatii
    # Mesajele trimise de acest utilizator
    sent_messages = db.relationship('Message', backref='sender', lazy='dynamic',
                                    foreign_keys='Message.sender_id')
    # Participarile la conversatii
    participations = db.relationship('ConversationParticipant', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """
        Seteaza parola utilizatorului folosind hash bcrypt.
        Nu stocam parola in clar pentru securitate.
        
        Args:
            password: Parola in text clar
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verifica daca parola introdusa corespunde cu hash-ul stocat.
        
        Args:
            password: Parola de verificat
            
        Returns:
            bool: True daca parola este corecta
        """
        return check_password_hash(self.password_hash, password)
    
    def update_last_seen(self):
        """
        Actualizeaza timestamp-ul ultimei activitati.
        Apelat la fiecare actiune a utilizatorului.
        """
        self.last_seen = datetime.utcnow()
    
    def to_dict(self, include_private=False):
        """
        Converteste utilizatorul la dictionar pentru raspuns JSON.
        
        Args:
            include_private: Daca True, include cheia privata criptata
            
        Returns:
            dict: Reprezentarea JSON a utilizatorului
        """
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'avatar_color': self.avatar_color,
            'public_key': self.public_key,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }
        
        # Cheia privata este returnata doar pentru utilizatorul propriu
        if include_private:
            data['private_key_encrypted'] = self.private_key_encrypted
            
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'
