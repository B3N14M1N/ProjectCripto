# services/file_service.py
# Serviciu pentru gestionarea fisierelor uploadate
# Cripteaza fisierele cu AES+RSA inainte de stocare
#
# Principii SOLID:
# - Single Responsibility: doar operatii cu fisiere
# - Open/Closed: poate fi extins pentru alte tipuri de stocare (S3, etc.)

import os
import uuid
import mimetypes
from werkzeug.utils import secure_filename
from config import Config
from .crypto_service import CryptoService


class FileService:
    """
    Serviciu pentru gestionarea fisierelor criptate.
    
    Responsabilitati:
    - Upload fisiere criptate
    - Download si decriptare fisiere
    - Validare tipuri de fisiere
    - Gestionare stocare
    
    Toate fisierele sunt criptate cu AES inainte de stocare.
    Cheia AES este criptata cu RSA pentru fiecare destinatar.
    """
    
    # Extensii permise pentru upload
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'zip'}
    
    # Tipuri MIME pentru imagini (afisate inline)
    IMAGE_MIME_TYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp'}
    
    def __init__(self, crypto_service=None, upload_folder=None):
        """
        Initializeaza serviciul de fisiere.
        
        Args:
            crypto_service: Instanta CryptoService
            upload_folder: Directorul pentru fisiere uploadate
        """
        self.crypto_service = crypto_service or CryptoService()
        self.upload_folder = upload_folder or Config.UPLOAD_FOLDER
        
        # Cream directorul daca nu exista
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def allowed_file(self, filename):
        """
        Verifica daca extensia fisierului este permisa.
        
        Args:
            filename: Numele fisierului
            
        Returns:
            bool: True daca extensia e permisa
        """
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def get_file_type(self, filename):
        """
        Determina tipul fisierului (image sau file).
        
        Args:
            filename: Numele fisierului
            
        Returns:
            str: 'image' sau 'file'
        """
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type in self.IMAGE_MIME_TYPES:
            return 'image'
        return 'file'
    
    def upload_file(self, file, recipient_public_keys):
        """
        Uploadeaza si cripteaza un fisier.
        
        Procesul:
        1. Valideaza fisierul
        2. Citeste continutul
        3. Cripteaza cu AES+RSA
        4. Salveaza fisierul criptat
        
        Args:
            file: Obiect fisier (din request.files)
            recipient_public_keys: Dict {user_id: public_key_pem}
            
        Returns:
            dict: {
                'success': bool,
                'file_info': informatii fisier sau None,
                'encrypted_data': date pentru mesaj sau None,
                'error': mesaj eroare sau None
            }
        """
        if not file or not file.filename:
            return {'success': False, 'error': 'Niciun fisier furnizat'}
        
        filename = secure_filename(file.filename)
        if not filename:
            return {'success': False, 'error': 'Nume fisier invalid'}
        
        if not self.allowed_file(filename):
            return {
                'success': False, 
                'error': f'Tip de fisier nepermis. Extensii permise: {", ".join(self.ALLOWED_EXTENSIONS)}'
            }
        
        try:
            # Citim continutul fisierului
            file_data = file.read()
            file_size = len(file_data)
            
            # Verificam dimensiunea (max 16MB)
            max_size = 16 * 1024 * 1024
            if file_size > max_size:
                return {'success': False, 'error': 'Fisierul este prea mare (max 16MB)'}
            
            # Criptam fisierul
            encrypted_data = self.crypto_service.encrypt_file(file_data, recipient_public_keys)
            
            # Generam un nume unic pentru fisierul criptat
            unique_id = str(uuid.uuid4())
            encrypted_filename = f"{unique_id}.enc"
            file_path = os.path.join(self.upload_folder, encrypted_filename)
            
            # Salvam fisierul criptat (base64 encoded)
            with open(file_path, 'w') as f:
                f.write(encrypted_data['encrypted_content'])
            
            # Determinam tipul si MIME type
            file_type = self.get_file_type(filename)
            mime_type, _ = mimetypes.guess_type(filename)
            
            return {
                'success': True,
                'file_info': {
                    'name': filename,
                    'path': encrypted_filename,
                    'size': file_size,
                    'mime_type': mime_type or 'application/octet-stream',
                    'type': file_type
                },
                'encrypted_data': {
                    'iv': encrypted_data['iv'],
                    'encrypted_aes_keys': encrypted_data['encrypted_aes_keys']
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Eroare la upload: {str(e)}'}
    
    def download_file(self, file_path, encrypted_aes_key, iv, private_key_pem):
        """
        Descarca si decripteaza un fisier.
        
        Args:
            file_path: Calea fisierului criptat
            encrypted_aes_key: Cheia AES criptata cu RSA
            iv: Vector initializare
            private_key_pem: Cheia privata RSA
            
        Returns:
            dict: {
                'success': bool,
                'data': continut decriptat (bytes) sau None,
                'error': mesaj eroare sau None
            }
        """
        full_path = os.path.join(self.upload_folder, file_path)
        
        if not os.path.exists(full_path):
            return {'success': False, 'error': 'Fisier negasit'}
        
        try:
            # Citim fisierul criptat
            with open(full_path, 'r') as f:
                encrypted_content = f.read()
            
            # Decriptam
            decrypted_data = self.crypto_service.decrypt_file(
                encrypted_content,
                encrypted_aes_key,
                iv,
                private_key_pem
            )
            
            return {
                'success': True,
                'data': decrypted_data
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Eroare la decriptare fisier: {str(e)}'}
    
    def delete_file(self, file_path):
        """
        Sterge un fisier din stocare.
        
        Args:
            file_path: Calea fisierului
            
        Returns:
            bool: True daca stergerea a reusit
        """
        full_path = os.path.join(self.upload_folder, file_path)
        
        try:
            if os.path.exists(full_path):
                os.remove(full_path)
                return True
            return False
        except Exception:
            return False
    
    def get_storage_info(self):
        """
        Obtine informatii despre spatiul de stocare folosit.
        
        Returns:
            dict: Statistici stocare
        """
        total_size = 0
        file_count = 0
        
        for filename in os.listdir(self.upload_folder):
            file_path = os.path.join(self.upload_folder, filename)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
                file_count += 1
        
        return {
            'total_files': file_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
