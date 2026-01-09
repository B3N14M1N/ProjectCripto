# routes/file_routes.py
# Rute API pentru upload si download fisiere criptate
# Suporta fisiere multiple per mesaj

from flask import Blueprint, request, jsonify, session, send_file
from functools import wraps
from io import BytesIO
from services import FileService, ChatService, AuthService
from models import Message, MessageAttachment, db

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
def upload_files(conversation_id):
    """
    Uploadeaza si cripteaza unul sau mai multe fisiere pentru o conversatie.
    Nu trimite mesajul automat - doar uploadeaza fisierele si returneaza info.
    
    Form Data:
        files: Lista de fisiere de uploadat (multiple)
    
    Response:
    {
        "success": true,
        "uploaded_files": [
            {
                "temp_id": "abc123",
                "name": "document.pdf",
                "size": 102400,
                "mime_type": "application/pdf",
                "file_type": "document",
                "file_icon": "pdf",
                "encrypted_path": "/uploads/abc123.enc",
                "encrypted_aes_keys": {...},
                "iv": "..."
            }
        ]
    }
    """
    user_id = get_current_user_id()
    
    # Verificam accesul la conversatie
    conversation = chat_service.get_conversation(conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Conversatie negasita sau acces interzis'}), 404
    
    # Verificam daca exista fisiere
    if 'files' not in request.files and 'file' not in request.files:
        return jsonify({'error': 'Niciun fisier furnizat'}), 400
    
    # Suportam atat 'files' (multiple) cat si 'file' (singular) pentru compatibilitate
    files = request.files.getlist('files')
    if not files or files[0].filename == '':
        files = request.files.getlist('file')
    
    if not files or files[0].filename == '':
        return jsonify({'error': 'Niciun fisier furnizat'}), 400
    
    # Obtinem cheile publice ale participantilor
    participant_ids = [p.user_id for p in conversation.participants]
    public_keys = auth_service.get_public_keys_for_users(participant_ids)
    
    if len(public_keys) != len(participant_ids):
        return jsonify({'error': 'Nu toti participantii au chei publice'}), 400
    
    # Procesam fiecare fisier
    uploaded_files = []
    for file in files:
        if file.filename == '':
            continue
            
        # Uploadam si criptam fisierul
        upload_result = file_service.upload_file(file, public_keys)
        
        if not upload_result['success']:
            # Continuam cu celelalte fisiere daca unul esueaza
            continue
        
        file_info = upload_result['file_info']
        uploaded_files.append({
            'temp_id': upload_result.get('temp_id', file_info['path'].split('/')[-1].replace('.enc', '')),
            'name': file_info['name'],
            'size': file_info['size'],
            'mime_type': file_info['mime_type'],
            'file_type': file_info['type'],
            'file_icon': MessageAttachment.get_file_icon(file_info['type'], file_info['mime_type']),
            'encrypted_path': file_info['path'],
            'encrypted_aes_keys': upload_result.get('encrypted_aes_keys', {}),
            'iv': upload_result.get('iv', '')
        })
    
    if not uploaded_files:
        return jsonify({'error': 'Niciun fisier uploadat cu succes'}), 400
    
    return jsonify({
        'success': True,
        'uploaded_files': uploaded_files,
        'crypto_info': {
            'algorithm': 'AES-256-CBC',
            'key_exchange': 'RSA-2048'
        }
    }), 201


@file_bp.route('/send/<int:conversation_id>', methods=['POST'])
@login_required
def send_message_with_files(conversation_id):
    """
    Trimite un mesaj cu fisiere atasate.
    Foloseste fisierele deja uploadate (temp_id-uri).
    
    Request Body:
    {
        "content": "Text optional al mesajului",
        "attachments": [
            {
                "temp_id": "abc123",
                "name": "document.pdf",
                "encrypted_path": "/uploads/abc123.enc",
                "encrypted_aes_keys": {...},
                "iv": "...",
                "size": 102400,
                "mime_type": "application/pdf",
                "file_type": "document"
            }
        ]
    }
    """
    user_id = get_current_user_id()
    data = request.get_json()
    
    # Verificam accesul la conversatie
    conversation = chat_service.get_conversation(conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Conversatie negasita sau acces interzis'}), 404
    
    content = data.get('content', '').strip()
    attachments_data = data.get('attachments', [])
    
    # Trebuie sa avem cel putin continut sau atasamente
    if not content and not attachments_data:
        return jsonify({'error': 'Mesajul trebuie sa contina text sau fisiere'}), 400
    
    # Determinam tipul mesajului
    message_type = 'text'
    if attachments_data:
        # Verificam daca toate sunt imagini
        all_images = all(att.get('file_type') == 'image' for att in attachments_data)
        if all_images:
            message_type = 'image'
        else:
            message_type = 'file'
    
    # Daca nu avem continut text, setam un placeholder gol (nu mai trimitem numele fisierului)
    if not content and attachments_data:
        content = ''  # Nu mai setam numele fisierului ca text
    
    # Trimitem mesajul
    message_result = chat_service.send_message(
        conversation_id,
        user_id,
        content,
        message_type
    )
    
    if not message_result['success']:
        return jsonify({'error': message_result['error']}), 400
    
    message = message_result['message']
    
    # Adaugam atasamentele la mesaj
    import json
    for att_data in attachments_data:
        # encrypted_aes_keys poate fi dict sau string
        enc_keys = att_data.get('encrypted_aes_keys', {})
        if isinstance(enc_keys, str):
            enc_keys_str = enc_keys
        else:
            enc_keys_str = json.dumps(enc_keys)
        
        attachment = MessageAttachment(
            message_id=message.id,
            file_name=att_data.get('name', 'file'),
            file_path=att_data.get('encrypted_path', ''),
            file_size=att_data.get('size', 0),
            file_mime_type=att_data.get('mime_type', 'application/octet-stream'),
            file_type=att_data.get('file_type', 'other'),
            encrypted_aes_keys=enc_keys_str,
            iv=att_data.get('iv', '')
        )
        db.session.add(attachment)
    
    db.session.commit()
    
    # Refresh message to load attachments
    db.session.refresh(message)
    
    return jsonify({
        'success': True,
        'message': message.to_dict(user_id)
    }), 201


@file_bp.route('/download/<int:attachment_id>', methods=['POST'])
@login_required
def download_attachment(attachment_id):
    """
    Descarca si decripteaza un atasament.
    
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
    
    # Obtinem atasamentul
    attachment = MessageAttachment.query.get(attachment_id)
    if not attachment:
        return jsonify({'error': 'Atasament negasit'}), 404
    
    # Verificam accesul la conversatie
    message = Message.query.get(attachment.message_id)
    if not message:
        return jsonify({'error': 'Mesaj negasit'}), 404
        
    conversation = chat_service.get_conversation(message.conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Acces interzis'}), 403
    
    # Obtinem cheia AES criptata pentru utilizatorul curent
    import json
    try:
        encrypted_keys = json.loads(attachment.encrypted_aes_keys)
        encrypted_aes_key = encrypted_keys.get(str(user_id))
    except Exception:
        encrypted_aes_key = None
    
    if not encrypted_aes_key:
        return jsonify({'error': 'Nu ai acces la acest fisier'}), 403
    
    # Decriptam fisierul
    result = file_service.download_file(
        attachment.file_path,
        encrypted_aes_key,
        attachment.iv,
        private_key
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    # Returnam fisierul decriptat
    return send_file(
        BytesIO(result['data']),
        mimetype=attachment.file_mime_type or 'application/octet-stream',
        as_attachment=True,
        download_name=attachment.file_name or 'file'
    )


@file_bp.route('/download-legacy/<int:message_id>', methods=['POST'])
@login_required
def download_file_legacy(message_id):
    """
    Descarca fisier din mesajele vechi (fara model Attachment).
    Pentru compatibilitate cu mesajele existente.
    """
    user_id = get_current_user_id()
    data = request.get_json()
    
    private_key = data.get('private_key')
    if not private_key:
        return jsonify({'error': 'Cheia privata este necesara'}), 400
    
    message = Message.query.get(message_id)
    if not message:
        return jsonify({'error': 'Mesaj negasit'}), 404
    
    conversation = chat_service.get_conversation(message.conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Acces interzis'}), 403
    
    if message.message_type not in ['image', 'file'] or not message.file_path:
        return jsonify({'error': 'Mesajul nu contine un fisier'}), 400
    
    encrypted_aes_key = message.get_encrypted_key_for_user(user_id)
    if not encrypted_aes_key:
        return jsonify({'error': 'Nu ai acces la acest fisier'}), 403
    
    result = file_service.download_file(
        message.file_path,
        encrypted_aes_key,
        message.iv,
        private_key
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    return send_file(
        BytesIO(result['data']),
        mimetype=message.file_mime_type or 'application/octet-stream',
        as_attachment=True,
        download_name=message.file_name or 'file'
    )


@file_bp.route('/image/<int:attachment_id>', methods=['POST'])
@login_required
def get_image(attachment_id):
    """
    Obtine imaginea decriptata pentru afisare inline.
    Returneaza base64 pentru a fi afisata direct in browser.
    """
    user_id = get_current_user_id()
    data = request.get_json()
    
    private_key = data.get('private_key')
    if not private_key:
        return jsonify({'error': 'Cheia privata este necesara'}), 400
    
    attachment = MessageAttachment.query.get(attachment_id)
    if not attachment:
        return jsonify({'error': 'Atasament negasit'}), 404
    
    if attachment.file_type != 'image':
        return jsonify({'error': 'Atasamentul nu este o imagine'}), 400
    
    message = Message.query.get(attachment.message_id)
    if not message:
        return jsonify({'error': 'Mesaj negasit'}), 404
        
    conversation = chat_service.get_conversation(message.conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Acces interzis'}), 403
    
    import json
    import base64
    
    try:
        encrypted_keys = json.loads(attachment.encrypted_aes_keys)
        encrypted_aes_key = encrypted_keys.get(str(user_id))
    except:
        encrypted_aes_key = None
    
    if not encrypted_aes_key:
        return jsonify({'error': 'Nu ai acces la aceasta imagine'}), 403
    
    result = file_service.download_file(
        attachment.file_path,
        encrypted_aes_key,
        attachment.iv,
        private_key
    )
    
    if not result['success']:
        return jsonify({'error': result['error']}), 400
    
    # Returnam imaginea ca base64
    image_base64 = base64.b64encode(result['data']).decode('utf-8')
    
    return jsonify({
        'success': True,
        'image_data': f"data:{attachment.file_mime_type};base64,{image_base64}",
        'file_name': attachment.file_name
    })


# ==================== ENDPOINTS PENTRU DECRIPTARE CLIENT-SIDE (E2E) ====================

@file_bp.route('/encrypted/<int:attachment_id>', methods=['GET'])
@login_required
def get_encrypted_file(attachment_id):
    """
    Descarca fisierul criptat (fara decriptare).
    Decriptarea se face pe client pentru end-to-end encryption.
    
    Returneaza fisierul criptat ca binary.
    Clientul trebuie sa obtina cheia AES de la /meta/<attachment_id>
    """
    user_id = get_current_user_id()
    
    attachment = MessageAttachment.query.get(attachment_id)
    if not attachment:
        return jsonify({'error': 'Atasament negasit'}), 404
    
    message = Message.query.get(attachment.message_id)
    if not message:
        return jsonify({'error': 'Mesaj negasit'}), 404
        
    conversation = chat_service.get_conversation(message.conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Acces interzis'}), 403
    
    # Verificam ca utilizatorul are acces la fisier
    import json
    try:
        encrypted_keys = json.loads(attachment.encrypted_aes_keys)
        if str(user_id) not in encrypted_keys:
            return jsonify({'error': 'Nu ai acces la acest fisier'}), 403
    except:
        return jsonify({'error': 'Eroare la verificarea accesului'}), 500
    
    # Citim fisierul criptat
    result = file_service.get_encrypted_file(attachment.file_path)
    
    if not result['success']:
        return jsonify({'error': result['error']}), 404
    
    return send_file(
        BytesIO(result['data']),
        mimetype='application/octet-stream',
        as_attachment=False
    )


@file_bp.route('/meta/<int:attachment_id>', methods=['GET'])
@login_required
def get_attachment_meta(attachment_id):
    """
    Obtine metadatele unui atasament necesare pentru decriptare client-side.
    
    Response:
    {
        "success": true,
        "encrypted_aes_key": "base64...",  // Cheia AES criptata pentru utilizatorul curent
        "iv": "base64...",
        "file_name": "document.pdf",
        "file_size": 102400,
        "file_mime_type": "application/pdf"
    }
    """
    user_id = get_current_user_id()
    
    attachment = MessageAttachment.query.get(attachment_id)
    if not attachment:
        return jsonify({'error': 'Atasament negasit'}), 404
    
    message = Message.query.get(attachment.message_id)
    if not message:
        return jsonify({'error': 'Mesaj negasit'}), 404
        
    conversation = chat_service.get_conversation(message.conversation_id, user_id)
    if not conversation:
        return jsonify({'error': 'Acces interzis'}), 403
    
    import json
    try:
        encrypted_keys = json.loads(attachment.encrypted_aes_keys)
        encrypted_aes_key = encrypted_keys.get(str(user_id))
    except:
        encrypted_aes_key = None
    
    if not encrypted_aes_key:
        return jsonify({'error': 'Nu ai acces la acest fisier'}), 403
    
    return jsonify({
        'success': True,
        'encrypted_aes_key': encrypted_aes_key,
        'iv': attachment.iv,
        'file_name': attachment.file_name,
        'file_size': attachment.file_size,
        'file_mime_type': attachment.file_mime_type
    })


@file_bp.route('/delete-temp/<temp_id>', methods=['DELETE'])
@login_required
def delete_temp_file(temp_id):
    """
    Sterge un fisier uploadat temporar (daca utilizatorul se razgandeste).
    """
    result = file_service.delete_temp_file(temp_id)
    return jsonify(result)


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
