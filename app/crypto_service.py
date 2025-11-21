from abc import ABC, abstractmethod
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

class ICryptoService(ABC):
    @abstractmethod
    def generate_rsa_keys(self):
        pass

    @abstractmethod
    def encrypt_flow(self, message: str, public_key_pem: str):
        pass

    @abstractmethod
    def decrypt_flow(self, encrypted_message_b64: str, encrypted_key_b64: str, iv_b64: str, private_key_pem: str):
        pass

class SecureMessagingService(ICryptoService):
    def __init__(self, key_size=2048):
        self.key_size = key_size

    def generate_rsa_keys(self):
        """Generates RSA Public and Private keys."""
        key = RSA.generate(self.key_size)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
        return private_key.decode('utf-8'), public_key.decode('utf-8')

    def encrypt_flow(self, message: str, public_key_pem: str):
        """
        1. Generate AES Key.
        2. Encrypt Message with AES.
        3. Encrypt AES Key with RSA.
        """
        # 1. Generate AES Key (16 bytes for AES-128, 32 for AES-256)
        aes_key = get_random_bytes(32) # AES-256
        
        # 2. Encrypt Message with AES (CBC mode)
        cipher_aes = AES.new(aes_key, AES.MODE_CBC)
        iv = cipher_aes.iv
        encrypted_message_bytes = cipher_aes.encrypt(pad(message.encode('utf-8'), AES.block_size))
        
        # 3. Encrypt AES Key with RSA
        recipient_key = RSA.import_key(public_key_pem)
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        encrypted_aes_key_bytes = cipher_rsa.encrypt(aes_key)

        # Encode for transport/display
        return {
            "original_message": message,
            "aes_key_debug": base64.b64encode(aes_key).decode('utf-8'),
            "iv": base64.b64encode(iv).decode('utf-8'),
            "encrypted_message": base64.b64encode(encrypted_message_bytes).decode('utf-8'),
            "encrypted_aes_key": base64.b64encode(encrypted_aes_key_bytes).decode('utf-8')
        }

    def decrypt_flow(self, encrypted_message_b64: str, encrypted_key_b64: str, iv_b64: str, private_key_pem: str):
        """
        1. Decrypt AES Key with RSA.
        2. Decrypt Message with AES.
        """
        try:
            # Decode inputs
            encrypted_aes_key_bytes = base64.b64decode(encrypted_key_b64)
            encrypted_message_bytes = base64.b64decode(encrypted_message_b64)
            iv = base64.b64decode(iv_b64)
            
            # 1. Decrypt AES Key with RSA
            private_key = RSA.import_key(private_key_pem)
            cipher_rsa = PKCS1_OAEP.new(private_key)
            aes_key = cipher_rsa.decrypt(encrypted_aes_key_bytes)
            
            # 2. Decrypt Message with AES
            cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
            decrypted_message_bytes = unpad(cipher_aes.decrypt(encrypted_message_bytes), AES.block_size)
            
            return {
                "decrypted_message": decrypted_message_bytes.decode('utf-8'),
                "decrypted_aes_key_debug": base64.b64encode(aes_key).decode('utf-8'),
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
