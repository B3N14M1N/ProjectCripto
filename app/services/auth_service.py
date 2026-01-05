# services/auth_service.py
# Serviciu pentru autentificare si gestionare utilizatori
# Responsabil pentru: inregistrare, login, sesiuni, generare chei RSA per utilizator
#
# Principii SOLID:
# - Single Responsibility: doar autentificare si gestionare useri
# - Dependency Inversion: depinde de interfata CryptoService

from datetime import datetime
from models import db, User
from .crypto_service import CryptoService


class AuthService:
    """
    Serviciu pentru autentificare si gestionare utilizatori.
    
    Responsabilitati:
    - Inregistrare utilizatori noi (cu generare chei RSA)
    - Autentificare (login)
    - Gestionare sesiuni
    - Cautare utilizatori
    
    La inregistrare, se genereaza automat o pereche de chei RSA:
    - Cheia publica este stocata in baza de date (vizibila pentru toti)
    - Cheia privata este stocata criptat sau trimisa utilizatorului pentru stocare locala
    """
    
    def __init__(self, crypto_service=None):
        """
        Initializeaza serviciul de autentificare.
        
        Args:
            crypto_service: Instanta CryptoService (dependency injection)
        """
        self.crypto_service = crypto_service or CryptoService()
    
    def register(self, username, email, password):
        """
        Inregistreaza un utilizator nou.
        
        Pasi:
        1. Valideaza datele de intrare
        2. Verifica unicitatea username/email
        3. Genereaza perechea de chei RSA
        4. Creeaza utilizatorul in baza de date
        
        Args:
            username: Nume utilizator (unic)
            email: Adresa email (unica)
            password: Parola (va fi hash-uita)
            
        Returns:
            dict: {
                'success': bool,
                'user': User sau None,
                'private_key': Cheia privata RSA (pentru stocare locala),
                'error': mesaj eroare sau None
            }
        """
        # Validare input
        if not username or len(username) < 3:
            return {'success': False, 'error': 'Numele de utilizator trebuie sa aiba minim 3 caractere'}
        
        if not email or '@' not in email:
            return {'success': False, 'error': 'Adresa de email invalida'}
        
        if not password or len(password) < 6:
            return {'success': False, 'error': 'Parola trebuie sa aiba minim 6 caractere'}
        
        # Verificam daca username-ul exista deja
        if User.query.filter_by(username=username).first():
            return {'success': False, 'error': 'Numele de utilizator este deja folosit'}
        
        # Verificam daca email-ul exista deja
        if User.query.filter_by(email=email).first():
            return {'success': False, 'error': 'Adresa de email este deja inregistrata'}
        
        try:
            # Generam perechea de chei RSA pentru utilizator
            private_key_pem, public_key_pem = self.crypto_service.generate_rsa_key_pair()
            
            # Generam o culoare aleatorie pentru avatar
            import random
            colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4']
            avatar_color = random.choice(colors)
            
            # Cream utilizatorul
            user = User(
                username=username,
                email=email,
                public_key=public_key_pem,
                private_key_encrypted=private_key_pem,  # In productie, ar trebui criptat
                avatar_color=avatar_color
            )
            user.set_password(password)
            
            # Salvam in baza de date
            db.session.add(user)
            db.session.commit()
            
            return {
                'success': True,
                'user': user,
                'private_key': private_key_pem,  # Trimitem utilizatorului pentru stocare locala
                'message': 'Cont creat cu succes! Salvati cheia privata in siguranta.'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Eroare la crearea contului: {str(e)}'}
    
    def login(self, username_or_email, password):
        """
        Autentifica un utilizator.
        
        Args:
            username_or_email: Nume utilizator sau email
            password: Parola
            
        Returns:
            dict: {
                'success': bool,
                'user': User sau None,
                'error': mesaj eroare sau None
            }
        """
        # Cautam utilizatorul dupa username sau email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user:
            return {'success': False, 'error': 'Utilizator negasit'}
        
        if not user.check_password(password):
            return {'success': False, 'error': 'Parola incorecta'}
        
        # Actualizam last_seen
        user.update_last_seen()
        db.session.commit()
        
        return {
            'success': True,
            'user': user,
            'message': 'Autentificare reusita'
        }
    
    def get_user_by_id(self, user_id):
        """
        Obtine un utilizator dupa ID.
        
        Args:
            user_id: ID-ul utilizatorului
            
        Returns:
            User sau None
        """
        return User.query.get(user_id)
    
    def get_user_by_username(self, username):
        """
        Obtine un utilizator dupa username.
        
        Args:
            username: Numele utilizatorului
            
        Returns:
            User sau None
        """
        return User.query.filter_by(username=username).first()
    
    def search_users(self, query, current_user_id=None, limit=10):
        """
        Cauta utilizatori dupa username sau email.
        
        Args:
            query: Textul de cautat
            current_user_id: ID utilizator curent (pentru excludere)
            limit: Numar maxim de rezultate
            
        Returns:
            list: Lista de User
        """
        if not query or len(query) < 2:
            return []
        
        search = f'%{query}%'
        
        users_query = User.query.filter(
            (User.username.ilike(search)) | 
            (User.email.ilike(search))
        )
        
        # Excludem utilizatorul curent din rezultate
        if current_user_id:
            users_query = users_query.filter(User.id != current_user_id)
        
        return users_query.limit(limit).all()
    
    def update_user_profile(self, user_id, **kwargs):
        """
        Actualizeaza profilul utilizatorului.
        
        Args:
            user_id: ID utilizator
            **kwargs: Campuri de actualizat (avatar_color, etc.)
            
        Returns:
            dict: Rezultat operatie
        """
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'Utilizator negasit'}
        
        try:
            # Actualizam campurile permise
            allowed_fields = ['avatar_color']
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(user, field, value)
            
            db.session.commit()
            return {'success': True, 'user': user}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def change_password(self, user_id, old_password, new_password):
        """
        Schimba parola utilizatorului.
        
        Args:
            user_id: ID utilizator
            old_password: Parola curenta
            new_password: Parola noua
            
        Returns:
            dict: Rezultat operatie
        """
        user = User.query.get(user_id)
        if not user:
            return {'success': False, 'error': 'Utilizator negasit'}
        
        if not user.check_password(old_password):
            return {'success': False, 'error': 'Parola curenta incorecta'}
        
        if len(new_password) < 6:
            return {'success': False, 'error': 'Parola noua trebuie sa aiba minim 6 caractere'}
        
        try:
            user.set_password(new_password)
            db.session.commit()
            return {'success': True, 'message': 'Parola schimbata cu succes'}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    def get_user_public_key(self, user_id):
        """
        Obtine cheia publica RSA a unui utilizator.
        Folosita pentru a cripta mesaje catre acest utilizator.
        
        Args:
            user_id: ID utilizator
            
        Returns:
            str: Cheia publica PEM sau None
        """
        user = User.query.get(user_id)
        return user.public_key if user else None
    
    def get_public_keys_for_users(self, user_ids):
        """
        Obtine cheile publice pentru mai multi utilizatori.
        Folosita la trimiterea mesajelor in conversatii.
        
        Args:
            user_ids: Lista de ID-uri utilizatori
            
        Returns:
            dict: {user_id: public_key_pem}
        """
        users = User.query.filter(User.id.in_(user_ids)).all()
        return {user.id: user.public_key for user in users if user.public_key}
