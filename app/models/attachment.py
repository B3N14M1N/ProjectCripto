# models/attachment.py
# Model pentru atasamente la mesaje (fisiere multiple)
# Permite atasarea mai multor fisiere la un singur mesaj

from datetime import datetime
from . import db


class MessageAttachment(db.Model):
    """
    Model pentru atasamente la mesaje.
    
    Permite mai multe fisiere per mesaj.
    Fiecare fisier este criptat separat cu AES si cheia AES
    este criptata cu RSA pentru fiecare participant.
    
    Atribute:
        id: Identificator unic
        message_id: Referinta la mesaj
        file_name: Numele original al fisierului
        file_path: Calea pe server (fisier criptat)
        file_size: Dimensiunea in bytes
        file_mime_type: Tipul MIME (image/png, application/pdf, etc.)
        file_type: Categorie (image, document, video, audio, other)
        encrypted_aes_keys: Cheile AES criptate cu RSA pentru fiecare utilizator (JSON)
        iv: Vector de initializare pentru decriptare
        thumbnail_path: Cale catre thumbnail pentru imagini (optional)
        created_at: Data uploadarii
    """
    
    __tablename__ = 'message_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'), nullable=False, index=True)
    
    # Informatii fisier
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    file_mime_type = db.Column(db.String(100), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # image, document, video, audio, other
    
    # Criptare
    encrypted_aes_keys = db.Column(db.Text, nullable=False)  # JSON cu chei criptate per user
    iv = db.Column(db.String(32), nullable=False)
    
    # Optional: thumbnail pentru imagini
    thumbnail_path = db.Column(db.String(500), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relatia cu mesajul
    message = db.relationship('Message', backref=db.backref('attachments', lazy='select'))
    
    # Mapare extensii -> tip fisier (SINGLE SOURCE OF TRUTH)
    EXTENSION_TO_TYPE = {
        # Imagini
        'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image',
        'webp': 'image', 'svg': 'image', 'bmp': 'image', 'ico': 'image',
        # Video
        'mp4': 'video', 'webm': 'video', 'avi': 'video', 'mov': 'video',
        'mkv': 'video', 'wmv': 'video', 'flv': 'video',
        # Audio
        'mp3': 'audio', 'wav': 'audio', 'ogg': 'audio', 'flac': 'audio',
        'm4a': 'audio', 'aac': 'audio', 'wma': 'audio',
        # Documente
        'pdf': 'document', 'doc': 'document', 'docx': 'document',
        'xls': 'document', 'xlsx': 'document', 'ppt': 'document', 'pptx': 'document',
        'txt': 'document', 'rtf': 'document', 'csv': 'document',
    }
    
    # Mapare extensii -> iconita specifica
    EXTENSION_TO_ICON = {
        'pdf': 'pdf',
        'doc': 'word', 'docx': 'word', 'odt': 'word', 'rtf': 'word',
        'xls': 'excel', 'xlsx': 'excel', 'ods': 'excel', 'csv': 'excel',
        'ppt': 'powerpoint', 'pptx': 'powerpoint', 'odp': 'powerpoint',
        'txt': 'text',
    }
    
    @staticmethod
    def get_extension(filename):
        """Extrage extensia din numele fisierului."""
        if not filename or '.' not in filename:
            return ''
        return filename.rsplit('.', 1)[-1].lower()
    
    @staticmethod
    def get_file_type_from_name(filename):
        """Determina tipul fisierului bazat pe extensie."""
        ext = MessageAttachment.get_extension(filename)
        return MessageAttachment.EXTENSION_TO_TYPE.get(ext, 'other')
    
    @staticmethod
    def get_file_type(mime_type):
        """Fallback: determina categoria bazat pe MIME type."""
        if not mime_type:
            return 'other'
        if mime_type.startswith('image/'):
            return 'image'
        elif mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif 'pdf' in mime_type or 'word' in mime_type or 'document' in mime_type:
            return 'document'
        elif 'excel' in mime_type or 'spreadsheet' in mime_type:
            return 'document'
        elif 'powerpoint' in mime_type or 'presentation' in mime_type:
            return 'document'
        elif mime_type == 'text/plain':
            return 'document'
        return 'other'
    
    @staticmethod
    def get_file_icon_from_name(filename):
        """Determina iconita bazat pe extensia fisierului."""
        ext = MessageAttachment.get_extension(filename)
        # Iconita specifica (pdf, word, etc)
        if ext in MessageAttachment.EXTENSION_TO_ICON:
            return MessageAttachment.EXTENSION_TO_ICON[ext]
        # Iconita generica bazata pe tip
        file_type = MessageAttachment.EXTENSION_TO_TYPE.get(ext, 'other')
        return file_type if file_type != 'other' else 'file'
    
    @staticmethod
    def get_file_icon(file_type, mime_type):
        """Fallback: returneaza iconita bazat pe tip si MIME."""
        if mime_type:
            if 'pdf' in mime_type:
                return 'pdf'
            elif 'word' in mime_type or mime_type == 'application/msword':
                return 'word'
            elif 'powerpoint' in mime_type or 'presentation' in mime_type:
                return 'powerpoint'
            elif 'excel' in mime_type or 'spreadsheet' in mime_type:
                return 'excel'
            elif mime_type == 'text/plain':
                return 'text'
        icons = {'image': 'image', 'video': 'video', 'audio': 'audio', 'document': 'file'}
        return icons.get(file_type, 'file')
    
    def to_dict(self, user_id=None):
        """
        Converteste atasamentul la dictionar pentru JSON.
        Foloseste extensia fisierului pentru a determina tipul si iconita.
        """
        # Determinam tipul si iconita bazat pe extensie (prioritate) sau MIME
        file_type = self.get_file_type_from_name(self.file_name) or self.file_type
        file_icon = self.get_file_icon_from_name(self.file_name)
        
        return {
            'id': self.id,
            'message_id': self.message_id,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'file_mime_type': self.file_mime_type,
            'file_type': file_type,
            'file_icon': file_icon,
            'iv': self.iv,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'has_key': user_id is not None and str(user_id) in (self.encrypted_aes_keys or ''),
            'can_download': True
        }
    
    def format_file_size(self):
        """
        Formateaza dimensiunea fisierului human-readable.
        """
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
