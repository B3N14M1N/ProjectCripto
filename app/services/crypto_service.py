# services/crypto_service.py
# Serviciu pentru operatii criptografice
# Implementeaza schema hibrida AES+RSA pentru criptare end-to-end
#
# Schema de criptare:
# - AES-256-CBC pentru criptarea continutului (rapid si eficient)
# - RSA-2048 pentru criptarea cheii AES (schimb securizat de chei)
#
# Principii SOLID aplicate:
# - Single Responsibility: doar operatii criptografice
# - Open/Closed: poate fi extins pentru alti algoritmi
# - Interface Segregation: metode clare pentru fiecare operatie

import os
import base64
import json
from abc import ABC, abstractmethod
from cryptography.hazmat.primitives import hashes, padding, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class ICryptoService(ABC):
    """
    Interfata abstracta pentru serviciul de criptare.
    Permite inlocuirea implementarii fara modificarea codului client (SOLID - DIP).
    """
    
    @abstractmethod
    def generate_rsa_key_pair(self):
        """Genereaza o pereche de chei RSA."""
        pass
    
    @abstractmethod
    def generate_aes_key(self):
        """Genereaza o cheie AES aleatorie."""
        pass
    
    @abstractmethod
    def encrypt_with_aes(self, plaintext, key, iv=None):
        """Cripteaza text cu AES."""
        pass
    
    @abstractmethod
    def decrypt_with_aes(self, ciphertext, key, iv):
        """Decripteaza text cu AES."""
        pass
    
    @abstractmethod
    def encrypt_with_rsa(self, plaintext, public_key_pem):
        """Cripteaza date cu RSA (cheie publica)."""
        pass
    
    @abstractmethod
    def decrypt_with_rsa(self, ciphertext, private_key_pem):
        """Decripteaza date cu RSA (cheie privata)."""
        pass


class CryptoService(ICryptoService):
    """
    Implementare completa a serviciului de criptare.
    
    Aceasta clasa implementeaza schema hibrida AES+RSA:
    
    1. GENERARE CHEI RSA (o singura data per utilizator):
       - Se genereaza o pereche de chei RSA-2048
       - Cheia publica este distribuita tuturor
       - Cheia privata ramane secreta la utilizator
    
    2. CRIPTARE MESAJ:
       - Se genereaza o cheie AES-256 aleatorie pentru fiecare mesaj
       - Mesajul este criptat cu AES-256-CBC
       - Cheia AES este criptata cu cheia publica RSA a destinatarului
       - Se trimite: mesaj_criptat + cheie_AES_criptata + IV
    
    3. DECRIPTARE MESAJ:
       - Destinatarul decripteaza cheia AES cu cheia sa privata RSA
       - Foloseste cheia AES pentru a decripta mesajul
    
    Avantaje schema hibrida:
    - AES este rapid pentru date mari
    - RSA permite schimb securizat de chei fara canal pre-partajat
    - Fiecare mesaj are cheie unica (forward secrecy partial)
    """
    
    # Constante pentru dimensiuni
    RSA_KEY_SIZE = 2048  # Biti - recomandat minim pentru securitate
    AES_KEY_SIZE = 32    # Bytes = 256 biti
    AES_BLOCK_SIZE = 16  # Bytes = 128 biti (standard AES)
    
    def __init__(self):
        """
        Initializeaza serviciul de criptare.
        Backend-ul default al cryptography este folosit.
        """
        self.backend = default_backend()
    
    # ==================== GENERARE CHEI ====================
    
    def generate_rsa_key_pair(self):
        """
        Genereaza o pereche de chei RSA-2048.
        
        RSA (Rivest-Shamir-Adleman) este un algoritm de criptare asimetrica.
        - Cheia publica: folosita pentru criptare, poate fi distribuita
        - Cheia privata: folosita pentru decriptare, trebuie pastrata secreta
        
        Returns:
            tuple: (private_key_pem, public_key_pem) - chei in format PEM
        """
        # Generam cheia privata RSA
        private_key = rsa.generate_private_key(
            public_exponent=65537,  # Standard, numar prim Fermat F4
            key_size=self.RSA_KEY_SIZE,
            backend=self.backend
        )
        
        # Extragem cheia publica din cea privata
        public_key = private_key.public_key()
        
        # Serializam cheile in format PEM (text, usor de stocat)
        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')
        
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_key_pem, public_key_pem
    
    def generate_aes_key(self):
        """
        Genereaza o cheie AES-256 aleatorie.
        
        AES (Advanced Encryption Standard) este un algoritm de criptare simetrica.
        Aceeasi cheie este folosita pentru criptare si decriptare.
        
        Returns:
            bytes: Cheie AES de 256 biti (32 bytes)
        """
        return os.urandom(self.AES_KEY_SIZE)
    
    def generate_iv(self):
        """
        Genereaza un vector de initializare (IV) pentru AES-CBC.
        
        IV-ul trebuie sa fie:
        - Unic pentru fiecare operatie de criptare
        - Nu trebuie sa fie secret (poate fi trimis alaturi de ciphertext)
        - Dimensiune: 16 bytes (dimensiunea blocului AES)
        
        Returns:
            bytes: IV de 16 bytes
        """
        return os.urandom(self.AES_BLOCK_SIZE)
    
    # ==================== CRIPTARE/DECRIPTARE AES ====================
    
    def encrypt_with_aes(self, plaintext, key, iv=None):
        """
        Cripteaza date folosind AES-256 in mod CBC.
        
        Mod CBC (Cipher Block Chaining):
        - Fiecare bloc este XOR-at cu blocul criptat anterior
        - Primul bloc este XOR-at cu IV
        - Ofera mai multa securitate decat ECB
        
        Padding PKCS7:
        - Datele sunt completate la multiplu de 16 bytes
        - Necesar pentru AES care lucreaza pe blocuri fixe
        
        Args:
            plaintext: Text de criptat (str sau bytes)
            key: Cheie AES (bytes, 32 bytes pentru AES-256)
            iv: Vector de initializare (bytes, 16 bytes) - optional
            
        Returns:
            dict: {
                'ciphertext': date criptate (base64),
                'iv': vector initializare (base64),
                'algorithm': 'AES-256-CBC'
            }
        """
        # Convertim plaintext la bytes daca e string
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Generam IV daca nu e furnizat
        if iv is None:
            iv = self.generate_iv()
        
        # Aplicam padding PKCS7 pentru a avea multiplu de block size
        padder = padding.PKCS7(algorithms.AES.block_size).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        
        # Cream cipher-ul AES in mod CBC
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(iv),
            backend=self.backend
        )
        
        # Criptam datele
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'iv': base64.b64encode(iv).decode('utf-8'),
            'algorithm': 'AES-256-CBC'
        }
    
    def decrypt_with_aes(self, ciphertext_b64, key, iv_b64):
        """
        Decripteaza date criptate cu AES-256-CBC.
        
        Procesul invers al criptarii:
        1. Decodifica base64
        2. Decripteaza cu AES-CBC folosind cheia si IV
        3. Elimina padding-ul PKCS7
        
        Args:
            ciphertext_b64: Date criptate (base64 string)
            key: Cheie AES (bytes)
            iv_b64: Vector de initializare (base64 string)
            
        Returns:
            str: Textul decriptat
            
        Raises:
            ValueError: Daca decriptarea esueaza
        """
        try:
            # Decodam din base64
            ciphertext = base64.b64decode(ciphertext_b64)
            iv = base64.b64decode(iv_b64)
            
            # Cream cipher-ul pentru decriptare
            cipher = Cipher(
                algorithms.AES(key),
                modes.CBC(iv),
                backend=self.backend
            )
            
            # Decriptam
            decryptor = cipher.decryptor()
            padded_data = decryptor.update(ciphertext) + decryptor.finalize()
            
            # Eliminam padding-ul
            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            plaintext = unpadder.update(padded_data) + unpadder.finalize()
            
            return plaintext.decode('utf-8')
            
        except Exception as e:
            raise ValueError(f"Eroare la decriptare AES: {str(e)}")
    
    # ==================== CRIPTARE/DECRIPTARE RSA ====================
    
    def encrypt_with_rsa(self, plaintext, public_key_pem):
        """
        Cripteaza date folosind RSA cu padding OAEP.
        
        OAEP (Optimal Asymmetric Encryption Padding):
        - Adauga randomizare la criptare
        - Protejeaza impotriva atacurilor known-plaintext
        - Standard recomandat pentru RSA
        
        Limitari RSA:
        - Poate cripta maxim (key_size - padding_overhead) bytes
        - Pentru RSA-2048: ~190 bytes maxim
        - De aceea folosim RSA doar pentru cheile AES (32 bytes)
        
        Args:
            plaintext: Date de criptat (bytes sau str)
            public_key_pem: Cheia publica RSA in format PEM
            
        Returns:
            str: Date criptate codificate base64
        """
        # Convertim la bytes daca e necesar
        if isinstance(plaintext, str):
            plaintext = plaintext.encode('utf-8')
        
        # Incarcam cheia publica din PEM
        public_key = serialization.load_pem_public_key(
            public_key_pem.encode('utf-8') if isinstance(public_key_pem, str) else public_key_pem,
            backend=self.backend
        )
        
        # Criptam cu OAEP padding
        ciphertext = public_key.encrypt(
            plaintext,
            asym_padding.OAEP(
                mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        
        return base64.b64encode(ciphertext).decode('utf-8')
    
    def decrypt_with_rsa(self, ciphertext_b64, private_key_pem):
        """
        Decripteaza date criptate cu RSA.
        
        Foloseste cheia privata pentru a decripta datele criptate
        cu cheia publica corespunzatoare.
        
        Args:
            ciphertext_b64: Date criptate (base64 string)
            private_key_pem: Cheia privata RSA in format PEM
            
        Returns:
            bytes: Datele decriptate
            
        Raises:
            ValueError: Daca decriptarea esueaza
        """
        try:
            # Decodam din base64
            ciphertext = base64.b64decode(ciphertext_b64)
            
            # Incarcam cheia privata
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8') if isinstance(private_key_pem, str) else private_key_pem,
                password=None,
                backend=self.backend
            )
            
            # Decriptam
            plaintext = private_key.decrypt(
                ciphertext,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            return plaintext
            
        except Exception as e:
            raise ValueError(f"Eroare la decriptare RSA: {str(e)}")
    
    # ==================== OPERATII COMBINATE (SCHEMA HIBRIDA) ====================
    
    def encrypt_message_for_recipients(self, message, recipient_public_keys):
        """
        Cripteaza un mesaj pentru mai multi destinatari folosind schema hibrida.
        
        Flux:
        1. Genereaza cheie AES aleatorie
        2. Cripteaza mesajul cu AES
        3. Pentru fiecare destinatar, cripteaza cheia AES cu cheia lui publica RSA
        
        Avantaj: mesajul e criptat o singura data, doar cheia AES e criptata
        pentru fiecare destinatar (eficient pentru grupuri).
        
        Args:
            message: Mesajul de criptat (str)
            recipient_public_keys: Dict {user_id: public_key_pem}
            
        Returns:
            dict: {
                'encrypted_content': mesaj criptat AES (base64),
                'iv': vector initializare (base64),
                'encrypted_aes_keys': {user_id: cheie_AES_criptata_RSA, ...}
            }
        """
        # Pas 1: Generam cheie AES pentru acest mesaj
        aes_key = self.generate_aes_key()
        
        # Pas 2: Criptam mesajul cu AES
        aes_result = self.encrypt_with_aes(message, aes_key)
        
        # Pas 3: Criptam cheia AES pentru fiecare destinatar
        encrypted_keys = {}
        for user_id, public_key_pem in recipient_public_keys.items():
            encrypted_keys[str(user_id)] = self.encrypt_with_rsa(aes_key, public_key_pem)
        
        return {
            'encrypted_content': aes_result['ciphertext'],
            'iv': aes_result['iv'],
            'encrypted_aes_keys': encrypted_keys
        }
    
    def decrypt_message(self, encrypted_content, encrypted_aes_key, iv, private_key_pem):
        """
        Decripteaza un mesaj primit folosind schema hibrida.
        
        Flux:
        1. Decripteaza cheia AES cu cheia privata RSA
        2. Decripteaza mesajul cu cheia AES obtinuta
        
        Args:
            encrypted_content: Mesaj criptat (base64)
            encrypted_aes_key: Cheie AES criptata cu RSA (base64)
            iv: Vector initializare (base64)
            private_key_pem: Cheia privata RSA a utilizatorului
            
        Returns:
            str: Mesajul decriptat
        """
        # Pas 1: Decriptam cheia AES
        aes_key = self.decrypt_with_rsa(encrypted_aes_key, private_key_pem)
        
        # Pas 2: Decriptam mesajul
        return self.decrypt_with_aes(encrypted_content, aes_key, iv)
    
    # ==================== CRIPTARE FISIERE ====================
    
    def encrypt_file(self, file_data, recipient_public_keys):
        """
        Cripteaza continutul unui fisier pentru mai multi destinatari.
        
        Similar cu encrypt_message_for_recipients, dar lucreaza cu bytes.
        
        Args:
            file_data: Continutul fisierului (bytes)
            recipient_public_keys: Dict {user_id: public_key_pem}
            
        Returns:
            dict: Acelasi format ca encrypt_message_for_recipients
        """
        # Generam cheie AES
        aes_key = self.generate_aes_key()
        
        # Criptam fisierul cu AES
        aes_result = self.encrypt_with_aes(file_data, aes_key)
        
        # Criptam cheia AES pentru fiecare destinatar
        encrypted_keys = {}
        for user_id, public_key_pem in recipient_public_keys.items():
            encrypted_keys[str(user_id)] = self.encrypt_with_rsa(aes_key, public_key_pem)
        
        return {
            'encrypted_content': aes_result['ciphertext'],
            'iv': aes_result['iv'],
            'encrypted_aes_keys': encrypted_keys
        }
    
    def decrypt_file(self, encrypted_content, encrypted_aes_key, iv, private_key_pem):
        """
        Decripteaza continutul unui fisier.
        
        Args:
            encrypted_content: Continut criptat (base64)
            encrypted_aes_key: Cheie AES criptata (base64)
            iv: Vector initializare (base64)
            private_key_pem: Cheia privata RSA
            
        Returns:
            bytes: Continutul fisierului decriptat
        """
        # Decriptam cheia AES
        aes_key = self.decrypt_with_rsa(encrypted_aes_key, private_key_pem)
        
        # Decriptam continutul
        ciphertext = base64.b64decode(encrypted_content)
        iv_bytes = base64.b64decode(iv)
        
        cipher = Cipher(
            algorithms.AES(aes_key),
            modes.CBC(iv_bytes),
            backend=self.backend
        )
        
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        return unpadder.update(padded_data) + unpadder.finalize()
    
    # ==================== UTILITARE ====================
    
    def get_encryption_info(self):
        """
        Returneaza informatii despre algoritmii folositi.
        Util pentru tooltip-urile educationale din UI.
        
        Returns:
            dict: Detalii despre criptare
        """
        return {
            'symmetric': {
                'algorithm': 'AES-256-CBC',
                'key_size_bits': 256,
                'block_size_bits': 128,
                'description_ro': (
                    'AES (Advanced Encryption Standard) este un algoritm de criptare '
                    'simetrica, adica foloseste aceeasi cheie pentru criptare si decriptare. '
                    'Modul CBC (Cipher Block Chaining) adauga securitate prin inlantuirea blocurilor.'
                )
            },
            'asymmetric': {
                'algorithm': 'RSA-2048',
                'key_size_bits': 2048,
                'padding': 'OAEP-SHA256',
                'description_ro': (
                    'RSA este un algoritm de criptare asimetrica cu doua chei: '
                    'publica (pentru criptare) si privata (pentru decriptare). '
                    'Folosit pentru schimbul securizat al cheilor AES.'
                )
            },
            'hybrid_schema': {
                'description_ro': (
                    'Schema hibrida combina avantajele ambelor tipuri de criptare: '
                    'viteza AES pentru date mari si securitatea RSA pentru schimbul de chei. '
                    'Fiecare mesaj are o cheie AES unica, criptata cu RSA pentru fiecare destinatar.'
                )
            }
        }
