# routes/auth_routes.py
# Rute API pentru autentificare
# Endpoints: register, login, logout, profil utilizator, cautare utilizatori

from flask import Blueprint, request, jsonify, session
from functools import wraps
from services import AuthService, CryptoService

# Cream blueprint-ul pentru autentificare
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Instantiem serviciile
auth_service = AuthService()
crypto_service = CryptoService()


def login_required(f):
    """
    Decorator pentru verificarea autentificarii.
    Verifica daca utilizatorul este autentificat prin sesiune.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Autentificare necesara'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """
    Obtine utilizatorul curent din sesiune.
    
    Returns:
        User sau None
    """
    user_id = session.get('user_id')
    if user_id:
        return auth_service.get_user_by_id(user_id)
    return None


# ==================== ENDPOINTS AUTENTIFICARE ====================

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Inregistreaza un utilizator nou.
    
    Request Body:
    {
        "username": "string",
        "email": "string",
        "password": "string"
    }
    
    Response:
    {
        "success": true,
        "user": {...},
        "private_key": "-----BEGIN PRIVATE KEY-----..."
    }
    
    IMPORTANT: Cheia privata trebuie salvata de utilizator!
    Este trimisa o singura data la inregistrare.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Date lipsa'}), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # Apelam serviciul de autentificare
    result = auth_service.register(username, email, password)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    # Setam sesiunea
    session['user_id'] = result['user'].id
    session.permanent = True
    
    return jsonify({
        'success': True,
        'message': result.get('message', 'Cont creat cu succes'),
        'user': result['user'].to_dict(include_private=True),
        'private_key': result['private_key'],
        'crypto_info': {
            'description': 'Cheia privata RSA este necesara pentru decriptarea mesajelor. '
                          'Salvati aceasta cheie intr-un loc sigur - nu o putem recupera!',
            'key_type': 'RSA-2048',
            'usage': 'Decriptare chei AES pentru mesaje primite'
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Autentifica un utilizator.
    
    Request Body:
    {
        "username": "string (sau email)",
        "password": "string"
    }
    
    Response:
    {
        "success": true,
        "user": {...}
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Date lipsa'}), 400
    
    username_or_email = data.get('username', '').strip()
    password = data.get('password', '')
    
    result = auth_service.login(username_or_email, password)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 401
    
    # Setam sesiunea
    session['user_id'] = result['user'].id
    session.permanent = True
    
    return jsonify({
        'success': True,
        'message': 'Autentificare reusita',
        'user': result['user'].to_dict(include_private=True)
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Deconecteaza utilizatorul curent.
    Sterge sesiunea.
    """
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Deconectare reusita'
    })


@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user_info():
    """
    Obtine informatiile utilizatorului curent.
    Necesita autentificare.
    
    Response:
    {
        "user": {...}
    }
    """
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Utilizator negasit'}), 404
    
    return jsonify({
        'user': user.to_dict(include_private=True)
    })


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """
    Verifica daca utilizatorul este autentificat.
    Folosit de frontend pentru a verifica starea sesiunii.
    """
    user = get_current_user()
    if user:
        return jsonify({
            'authenticated': True,
            'user': user.to_dict(include_private=True)
        })
    return jsonify({'authenticated': False})


# ==================== ENDPOINTS UTILIZATORI ====================

@auth_bp.route('/users/search', methods=['GET'])
@login_required
def search_users():
    """
    Cauta utilizatori dupa username sau email.
    Folosit pentru a incepe conversatii noi.
    
    Query Parameters:
        q: Textul de cautat (minim 2 caractere)
        limit: Numar maxim rezultate (default 10)
    
    Response:
    {
        "users": [...]
    }
    """
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 10)), 20)
    
    current_user = get_current_user()
    users = auth_service.search_users(query, current_user.id, limit)
    
    return jsonify({
        'users': [user.to_dict() for user in users]
    })


@auth_bp.route('/users/<int:user_id>', methods=['GET'])
@login_required
def get_user(user_id):
    """
    Obtine profilul unui utilizator.
    
    Response:
    {
        "user": {...}
    }
    """
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'Utilizator negasit'}), 404
    
    return jsonify({
        'user': user.to_dict()
    })


@auth_bp.route('/users/<int:user_id>/public-key', methods=['GET'])
@login_required
def get_user_public_key(user_id):
    """
    Obtine cheia publica RSA a unui utilizator.
    Folosita pentru a cripta mesaje catre acel utilizator.
    
    Response:
    {
        "public_key": "-----BEGIN PUBLIC KEY-----...",
        "info": {...}
    }
    """
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': 'Utilizator negasit'}), 404
    
    if not user.public_key:
        return jsonify({'error': 'Utilizatorul nu are cheie publica configurata'}), 404
    
    return jsonify({
        'public_key': user.public_key,
        'username': user.username,
        'info': {
            'key_type': 'RSA-2048',
            'format': 'PEM',
            'usage': 'Criptare chei AES pentru mesaje trimise catre acest utilizator'
        }
    })


# ==================== ENDPOINTS PROFIL ====================

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """
    Actualizeaza profilul utilizatorului curent.
    
    Request Body:
    {
        "avatar_color": "#3B82F6"
    }
    """
    data = request.get_json()
    current_user = get_current_user()
    
    result = auth_service.update_user_profile(
        current_user.id,
        avatar_color=data.get('avatar_color')
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({
        'success': True,
        'user': result['user'].to_dict()
    })


@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """
    Schimba parola utilizatorului curent.
    
    Request Body:
    {
        "old_password": "string",
        "new_password": "string"
    }
    """
    data = request.get_json()
    current_user = get_current_user()
    
    result = auth_service.change_password(
        current_user.id,
        data.get('old_password', ''),
        data.get('new_password', '')
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({
        'success': True,
        'message': result.get('message', 'Parola schimbata cu succes')
    })


# ==================== ENDPOINTS INFORMATII CRIPTARE ====================

@auth_bp.route('/crypto-info', methods=['GET'])
def get_crypto_info():
    """
    Obtine informatii despre algoritmii de criptare folositi.
    Endpoint educational pentru afisarea in UI.
    """
    return jsonify(crypto_service.get_encryption_info())
