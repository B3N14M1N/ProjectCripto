# routes/file_routes.py
# Rute API pentru upload si download fisiere criptate
# Toate fisierele sunt criptate cu AES+RSA inainte de stocare

from flask import Blueprint, request, jsonify, session, send_file
from functools import wraps
from io import BytesIO
from services import FileService, ChatService, AuthService
from models import Message

# Cream blueprint-ul pentru fisiere
file_bp = Blueprint('files', __name__, url_prefix='/api/files')

# Instantiem serviciile
file_service = FileService()
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


@file_bp.route('/upload/<int:conversation_id>', methods=['POST'])
@login_required
def upload_file(conversation_id):
    """
    Uploadeaza si cripteaza un fisier pentru o conversatie.
    
    Procesul:
    1. Verifica accesul la conversatie
    2. Obtine cheile publice ale participantilor
    3. Cripteaza fisierul cu AES+RSA
    4. Salveaza fisierul criptat
    5. Creeaza mesajul cu informatiile fisierului
    
    Form Data:
        file: Fisierul de uploadat
        caption: Descriere optionala (va fi criptata ca mesaj)
    
    Response:
    {
        "success": true,
        "message": {...},  // Mesajul cu fisierul atasat
        "file_info": {...}
    }
    """
    user_id = get_current_user_id()
    
    # Verificam accesul la conversatie
    conversation = chat_service.get_conversation(conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Conversatie negasita sau acces interzis'}), 404
    
    # Verificam daca exista fisier
    if 'file' not in request.files:
        return jsonify({'error': 'Niciun fisier furnizat'}), 400
    
    file = request.files['file']
    caption = request.form.get('caption', '')
    
    # Obtinem cheile publice ale participantilor
    participant_ids = [p.user_id for p in conversation.participants]
    public_keys = auth_service.get_public_keys_for_users(participant_ids)
    
    if len(public_keys) != len(participant_ids):
        return jsonify({'error': 'Nu toti participantii au chei publice'}), 400
    
    # Uploadam si criptam fisierul
    upload_result = file_service.upload_file(file, public_keys)
    
    if not upload_result['success']:
        return jsonify({'error': upload_result['error']}), 400
    
    # Determinam tipul mesajului
    file_info = upload_result['file_info']
    message_type = file_info['type']  # 'image' sau 'file'
    
    # Continutul mesajului - numele fisierului sau descrierea
    content = caption if caption else file_info['name']
    
    # Trimitem mesajul cu fisierul atasat
    message_result = chat_service.send_message(
        conversation_id,
        user_id,
        content,
        message_type,
        file_info={
            'name': file_info['name'],
            'path': file_info['path'],
            'size': file_info['size'],
            'mime_type': file_info['mime_type']
        }
    )
    
    if not message_result['success']:
        # Stergem fisierul daca mesajul a esuat
        file_service.delete_file(file_info['path'])
        return jsonify({'error': message_result['error']}), 400
    
    return jsonify({
        'success': True,
        'message': message_result['message'].to_dict(user_id),
        'file_info': {
            'name': file_info['name'],
            'size': file_info['size'],
            'mime_type': file_info['mime_type'],
            'type': file_info['type']
        },
        'crypto_info': {
            'file_encrypted': True,
            'algorithm': 'AES-256-CBC',
            'key_exchange': 'RSA-2048',
            'description': 'Fisierul este criptat cu o cheie AES unica, '
                          'care este criptata cu cheia RSA a fiecarui participant.'
        }
    }), 201


@file_bp.route('/download/<int:message_id>', methods=['POST'])
@login_required
def download_file(message_id):
    """
    Descarca si decripteaza un fisier.
    
    Fisierul este decriptat pe server folosind cheia privata furnizata.
    
    Request Body:
    {
        "private_key": "-----BEGIN PRIVATE KEY-----..."
    }
    
    Response: Fisierul decriptat (binary)
    """
    user_id = get_current_user_id()
    data = request.get_json()
    
    private_key = data.get('private_key')
    if not private_key:
        return jsonify({'error': 'Cheia privata este necesara'}), 400
    
    # Obtinem mesajul
    message = Message.query.get(message_id)
    if not message:
        return jsonify({'error': 'Mesaj negasit'}), 404
    
    # Verificam accesul la conversatie
    conversation = chat_service.get_conversation(message.conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Acces interzis'}), 403
    
    # Verificam ca mesajul are fisier
    if message.message_type not in ['image', 'file'] or not message.file_path:
        return jsonify({'error': 'Mesajul nu contine un fisier'}), 400
    
    # Obtinem cheia AES criptata pentru utilizatorul curent
    encrypted_aes_key = message.get_encrypted_key_for_user(user_id)
    if not encrypted_aes_key:
        return jsonify({'error': 'Nu ai acces la acest fisier'}), 403
    
    # Decriptam fisierul
    result = file_service.download_file(
        message.file_path,
        encrypted_aes_key,
        message.iv,
        private_key
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    # Returnam fisierul decriptat
    return send_file(
        BytesIO(result['data']),
        mimetype=message.file_mime_type or 'application/octet-stream',
        as_attachment=True,
        download_name=message.file_name or 'file'
    )


@file_bp.route('/info/<int:message_id>', methods=['GET'])
@login_required
def get_file_info(message_id):
    """
    Obtine informatii despre un fisier fara a-l descarca.
    
    Response:
    {
        "file_info": {
            "name": "document.pdf",
            "size": 102400,
            "mime_type": "application/pdf",
            "type": "file"
        },
        "crypto_info": {...}
    }
    """
    user_id = get_current_user_id()
    
    message = Message.query.get(message_id)
    if not message:
        return jsonify({'error': 'Mesaj negasit'}), 404
    
    # Verificam accesul
    conversation = chat_service.get_conversation(message.conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Acces interzis'}), 403
    
    if message.message_type not in ['image', 'file']:
        return jsonify({'error': 'Mesajul nu contine un fisier'}), 400
    
    return jsonify({
        'file_info': {
            'name': message.file_name,
            'size': message.file_size,
            'mime_type': message.file_mime_type,
            'type': message.message_type,
            'created_at': message.created_at.isoformat() if message.created_at else None
        },
        'crypto_info': {
            'is_encrypted': True,
            'algorithm': 'AES-256-CBC',
            'key_exchange': 'RSA-2048',
            'can_decrypt': message.get_encrypted_key_for_user(user_id) is not None
        }
    })


@file_bp.route('/storage-info', methods=['GET'])
@login_required
def get_storage_info():
    """
    Obtine informatii despre spatiul de stocare.
    Doar pentru administrare/debugging.
    """
    info = file_service.get_storage_info()
    return jsonify(info)
