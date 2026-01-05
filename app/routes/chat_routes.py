# routes/chat_routes.py
# Rute API pentru conversatii si mesaje
# Toate mesajele sunt criptate cu AES+RSA

from flask import Blueprint, request, jsonify, session
from functools import wraps
from services import ChatService, AuthService

# Cream blueprint-ul pentru chat
chat_bp = Blueprint('chat', __name__, url_prefix='/api')

# Instantiem serviciile
chat_service = ChatService()
auth_service = AuthService()


def login_required(f):
    """Decorator pentru verificarea autentificarii."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Autentificare necesara'}), 401
        return f(*args, **kwargs)
    return decorated_function


def get_current_user_id():
    """Obtine ID-ul utilizatorului curent din sesiune."""
    return session.get('user_id')


# ==================== ENDPOINTS CONVERSATII ====================

@chat_bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    """
    Obtine lista conversatiilor utilizatorului curent.
    Ordonate descrescator dupa ultima activitate.
    
    Response:
    {
        "conversations": [
            {
                "id": 1,
                "name": "username_celalalt",
                "unread_count": 2,
                "last_message": {...},
                ...
            }
        ]
    }
    """
    user_id = get_current_user_id()
    conversations = chat_service.get_user_conversations(user_id)
    
    return jsonify({
        'conversations': [conv.to_dict(user_id) for conv in conversations]
    })


@chat_bp.route('/conversations', methods=['POST'])
@login_required
def create_conversation():
    """
    Creeaza o conversatie noua sau returneaza una existenta.
    
    Pentru conversatii 1-la-1, daca exista deja una intre cei doi
    utilizatori, o returneaza pe cea existenta.
    
    Request Body:
    {
        "participant_ids": [2, 3],  // Lista ID-uri (fara utilizatorul curent)
        "name": "Grup Proiect"      // Optional, doar pentru grupuri
    }
    
    Response:
    {
        "success": true,
        "conversation": {...},
        "is_existing": false
    }
    """
    data = request.get_json()
    user_id = get_current_user_id()
    
    participant_ids = data.get('participant_ids', [])
    name = data.get('name')
    
    if not participant_ids:
        return jsonify({'error': 'Trebuie sa specifici cel putin un participant'}), 400
    
    # Adaugam utilizatorul curent la participanti
    all_participants = [user_id] + participant_ids
    
    result = chat_service.create_conversation(user_id, all_participants, name)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({
        'success': True,
        'conversation': result['conversation'].to_dict(user_id),
        'is_existing': result.get('is_existing', False),
        'message': result.get('message')
    }), 201 if not result.get('is_existing') else 200


@chat_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
@login_required
def get_conversation(conversation_id):
    """
    Obtine detaliile unei conversatii.
    
    Response:
    {
        "conversation": {...},
        "crypto_info": {...}  // Informatii despre criptare
    }
    """
    user_id = get_current_user_id()
    conversation = chat_service.get_conversation(conversation_id, user_id)
    
    if not conversation:
        return jsonify({'error': 'Conversatie negasita sau acces interzis'}), 404
    
    crypto_info = chat_service.get_conversation_crypto_info(conversation_id)
    
    return jsonify({
        'conversation': conversation.to_dict(user_id),
        'crypto_info': crypto_info
    })


# ==================== ENDPOINTS MESAJE ====================

@chat_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@login_required
def get_messages(conversation_id):
    """
    Obtine mesajele dintr-o conversatie.
    Mesajele sunt returnate criptate - decriptarea se face pe client.
    
    Query Parameters:
        limit: Numar maxim mesaje (default 50)
        before: ID mesaj pentru paginare (mesaje mai vechi)
    
    Response:
    {
        "messages": [
            {
                "id": 1,
                "encrypted_content": "base64...",
                "encrypted_aes_key": "base64...",
                "iv": "base64...",
                "sender_id": 1,
                ...
            }
        ],
        "has_more": true
    }
    """
    user_id = get_current_user_id()
    
    limit = min(int(request.args.get('limit', 50)), 100)
    before_id = request.args.get('before', type=int)
    
    messages = chat_service.get_messages(conversation_id, user_id, limit, before_id)
    
    return jsonify({
        'messages': [msg.to_dict(user_id) for msg in messages],
        'has_more': len(messages) == limit
    })


@chat_bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
@login_required
def send_message(conversation_id):
    """
    Trimite un mesaj intr-o conversatie.
    Mesajul este criptat pe server folosind schema AES+RSA.
    
    Request Body:
    {
        "content": "Mesajul in clar",
        "message_type": "text"  // text, image, file
    }
    
    Response:
    {
        "success": true,
        "message": {...},
        "crypto_details": {
            "algorithm_content": "AES-256-CBC",
            "algorithm_key_exchange": "RSA-2048",
            ...
        }
    }
    """
    user_id = get_current_user_id()
    data = request.get_json()
    
    content = data.get('content', '').strip()
    message_type = data.get('message_type', 'text')
    
    if not content:
        return jsonify({'error': 'Mesajul nu poate fi gol'}), 400
    
    result = chat_service.send_message(
        conversation_id, 
        user_id, 
        content,
        message_type
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({
        'success': True,
        'message': result['message'].to_dict_with_crypto_info(user_id),
        'crypto_details': result.get('crypto_details')
    }), 201


@chat_bp.route('/conversations/<int:conversation_id>/read', methods=['PUT'])
@login_required
def mark_as_read(conversation_id):
    """
    Marcheaza toate mesajele din conversatie ca citite.
    Reseteaza contorul de mesaje necitite.
    """
    user_id = get_current_user_id()
    
    result = chat_service.mark_conversation_as_read(conversation_id, user_id)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({
        'success': True,
        'message': 'Mesaje marcate ca citite'
    })


# ==================== ENDPOINTS DECRIPTARE ====================

@chat_bp.route('/messages/<int:message_id>/decrypt', methods=['POST'])
@login_required
def decrypt_message(message_id):
    """
    Decripteaza un mesaj specific.
    
    NOTA IMPORTANTA: In mod normal, decriptarea ar trebui facuta pe client
    pentru securitate maxima. Acest endpoint este pentru demonstratie
    sau cazuri cand decriptarea client-side nu e posibila.
    
    Request Body:
    {
        "private_key": "-----BEGIN PRIVATE KEY-----..."
    }
    
    Response:
    {
        "success": true,
        "content": "Mesajul decriptat",
        "message_type": "text"
    }
    """
    user_id = get_current_user_id()
    data = request.get_json()
    
    private_key = data.get('private_key')
    if not private_key:
        return jsonify({'error': 'Cheia privata este necesara pentru decriptare'}), 400
    
    result = chat_service.decrypt_message(message_id, user_id, private_key)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    return jsonify({
        'success': True,
        'content': result['content'],
        'message_type': result['message_type'],
        'file_info': result.get('file_info')
    })


# ==================== ENDPOINTS UTILITARE ====================

@chat_bp.route('/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    """
    Obtine numarul total de mesaje necitite.
    Util pentru badge-uri in UI.
    """
    user_id = get_current_user_id()
    count = chat_service.get_unread_count(user_id)
    
    return jsonify({
        'unread_count': count
    })


@chat_bp.route('/conversations/<int:conversation_id>/crypto-info', methods=['GET'])
@login_required
def get_conversation_crypto_info(conversation_id):
    """
    Obtine informatii detaliate despre criptarea conversatiei.
    Endpoint educational pentru UI.
    """
    user_id = get_current_user_id()
    
    # Verificam accesul
    conversation = chat_service.get_conversation(conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Conversatie negasita sau acces interzis'}), 404
    
    crypto_info = chat_service.get_conversation_crypto_info(conversation_id)
    
    return jsonify(crypto_info)
