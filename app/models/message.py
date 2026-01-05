# models/message.py
# Model pentru mesaje criptate
# Stocheaza mesajele criptate cu AES si cheia AES criptata cu RSA

from datetime import datetime
from . import db


class Message(db.Model):
    """
    Model pentru mesaje criptate.
    
    Fiecare mesaj este criptat folosind schema hibrida AES+RSA:
    1. Continutul este criptat cu o cheie AES generata aleator
    2. Cheia AES este criptata cu cheia publica RSA a destinatarului
    3. Se stocheaza: continut_criptat + cheie_AES_criptata + IV
    
    Aceasta schema permite criptare rapida (AES) cu schimb securizat de chei (RSA).
    
    Atribute:
        id: Identificator unic al mesajului
        conversation_id: Referinta la conversatie
        sender_id: ID-ul expeditorului
        encrypted_content: Continutul criptat cu AES-256-CBC (base64)
        encrypted_aes_key: Cheia AES criptata cu RSA pentru fiecare destinatar (JSON)
        iv: Vector de initializare pentru AES-CBC (base64)
        message_type: Tipul mesajului (text/image/file)
        file_name: Numele original al fisierului (pentru atasamente)
        file_path: Calea pe server a fisierului criptat
        file_size: Dimensiunea fisierului in bytes
        created_at: Data trimiterii mesajului
        is_read: Flag pentru mesaj citit (deprecated, folosim ConversationParticipant)
    """
    
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Date criptate - schema hibrida AES+RSA
    # Continutul mesajului criptat cu AES-256 in mod CBC
    encrypted_content = db.Column(db.Text, nullable=False)
    
    # Cheia AES criptata cu RSA pentru fiecare participant
    # Format JSON: {"user_id_1": "encrypted_key_base64", "user_id_2": "..."}
    # Fiecare utilizator poate decripta cheia AES cu propria cheie privata RSA
    encrypted_aes_keys = db.Column(db.Text, nullable=False)
    
    # Vectorul de initializare pentru AES-CBC (16 bytes, base64 encoded)
    # IV trebuie sa fie unic pentru fiecare mesaj dar nu trebuie sa fie secret
    iv = db.Column(db.String(32), nullable=False)
    
    # Tipul mesajului: text, image, file
    message_type = db.Column(db.String(20), default='text')
    
    # Informatii despre fisiere atasate
    file_name = db.Column(db.String(255), nullable=True)
    file_path = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)
    file_mime_type = db.Column(db.String(100), nullable=True)
    
    # Timestamp trimitere
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def get_encrypted_key_for_user(self, user_id):
        """
        Obtine cheia AES criptata pentru un utilizator specific.
        
        Args:
            user_id: ID-ul utilizatorului
            
        Returns:
            str: Cheia AES criptata (base64) sau None
        """
        import json
        try:
            keys = json.loads(self.encrypted_aes_keys)
            return keys.get(str(user_id))
        except (json.JSONDecodeError, TypeError):
            return None
    
    def to_dict(self, current_user_id=None):
        """
        Converteste mesajul la dictionar pentru raspuns JSON.
        
        Include doar cheia AES criptata pentru utilizatorul curent,
        nu pentru toti participantii (securitate).
        
        Args:
            current_user_id: ID-ul utilizatorului care solicita mesajul
            
        Returns:
            dict: Reprezentarea JSON a mesajului
        """
        result = {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'sender_username': self.sender.username if self.sender else None,
            'sender_avatar_color': self.sender.avatar_color if self.sender else None,
            'encrypted_content': self.encrypted_content,
            'iv': self.iv,
            'message_type': self.message_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Adaugam cheia AES criptata doar pentru utilizatorul curent
        if current_user_id:
            result['encrypted_aes_key'] = self.get_encrypted_key_for_user(current_user_id)
        
        # Informatii fisier daca exista
        if self.message_type in ['image', 'file']:
            result['file_info'] = {
                'name': self.file_name,
                'size': self.file_size,
                'mime_type': self.file_mime_type
            }
        
        return result
    
    def to_dict_with_crypto_info(self, current_user_id=None):
        """
        Versiune extinsa care include informatii educationale despre criptare.
        Folosita pentru tooltip-urile explicative din UI.
        
        Args:
            current_user_id: ID-ul utilizatorului curent
            
        Returns:
            dict: Reprezentare JSON cu detalii despre criptare
        """
        base_dict = self.to_dict(current_user_id)
        
        # Adaugam informatii despre procesul de criptare
        base_dict['crypto_info'] = {
            'encryption_algorithm': 'AES-256-CBC',
            'key_exchange': 'RSA-2048',
            'iv_size_bytes': 16,
            'aes_key_size_bits': 256,
            'description_ro': (
                'Mesajul este criptat cu AES-256 in mod CBC. '
                'Cheia AES este generata aleator pentru fiecare mesaj si '
                'este criptata cu cheia publica RSA a fiecarui destinatar. '
                'Doar destinatarii pot decripta cheia AES cu cheile lor private.'
            )
        }
        
        return base_dict
    
    def __repr__(self):
        return f'<Message {self.id} in conv {self.conversation_id}>'
