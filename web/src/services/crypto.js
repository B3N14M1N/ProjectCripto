// src/services/crypto.js
// Serviciu pentru operatii criptografice pe client
// Implementeaza decriptarea End-to-End folosind Web Crypto API
// Serverul nu are acces la datele decriptate

/**
 * Decripteaza mesaje si fisiere folosind Web Crypto API
 * 
 * Procesul:
 * 1. Importa cheia privata RSA din format PEM
 * 2. Decripteaza cheia AES cu RSA-OAEP
 * 3. Decripteaza continutul cu AES-CBC
 * 
 * Aceasta implementare asigura End-to-End Encryption (E2E) -
 * serverul nu poate decripta mesajele, doar clientul cu cheia privata.
 */

// Converteste string PEM la ArrayBuffer
function pemToArrayBuffer(pem) {
  const lines = pem.split('\n');
  let base64 = '';
  for (let i = 0; i < lines.length; i++) {
    if (!lines[i].startsWith('-----')) {
      base64 += lines[i];
    }
  }
  const binaryString = window.atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

// Converteste base64 la ArrayBuffer
function base64ToArrayBuffer(base64) {
  const binaryString = window.atob(base64);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes.buffer;
}

// Converteste ArrayBuffer la string
function arrayBufferToString(buffer) {
  return new TextDecoder().decode(buffer);
}

/**
 * Clasa pentru operatii criptografice client-side (E2E)
 * 
 * Implementeaza decriptarea completa pe client:
 * - RSA-OAEP pentru decriptarea cheii AES
 * - AES-256-CBC pentru decriptarea continutului
 * Serverul nu are acces la datele decriptate.
 */
export class CryptoClient {
  /**
   * Importa o cheie privata RSA din format PEM
   */
  async importPrivateKey(pemKey) {
    const keyData = pemToArrayBuffer(pemKey);
    
    return await window.crypto.subtle.importKey(
      'pkcs8',
      keyData,
      {
        name: 'RSA-OAEP',
        hash: 'SHA-256',
      },
      false,
      ['decrypt']
    );
  }
  
  /**
   * Decripteaza date cu RSA-OAEP
   */
  async decryptRSA(encryptedData, privateKey) {
    const encryptedBuffer = base64ToArrayBuffer(encryptedData);
    
    const decrypted = await window.crypto.subtle.decrypt(
      { name: 'RSA-OAEP' },
      privateKey,
      encryptedBuffer
    );
    
    return new Uint8Array(decrypted);
  }
  
  /**
   * Importa o cheie AES din bytes
   */
  async importAESKey(keyBytes) {
    return await window.crypto.subtle.importKey(
      'raw',
      keyBytes,
      { name: 'AES-CBC' },
      false,
      ['decrypt']
    );
  }
  
  /**
   * Decripteaza date cu AES-CBC
   */
  async decryptAES(encryptedData, key, iv) {
    const encryptedBuffer = base64ToArrayBuffer(encryptedData);
    const ivBuffer = base64ToArrayBuffer(iv);
    
    const decrypted = await window.crypto.subtle.decrypt(
      {
        name: 'AES-CBC',
        iv: ivBuffer,
      },
      key,
      encryptedBuffer
    );
    
    return arrayBufferToString(decrypted);
  }
  
  /**
   * Decripteaza date binare cu AES-CBC (pentru fisiere)
   * Returneaza ArrayBuffer in loc de string
   */
  async decryptAESBinary(encryptedBuffer, key, ivBuffer) {
    const decrypted = await window.crypto.subtle.decrypt(
      {
        name: 'AES-CBC',
        iv: ivBuffer,
      },
      key,
      encryptedBuffer
    );
    
    return decrypted;
  }
  
  /**
   * Decripteaza un mesaj complet (schema hibrida AES+RSA)
   */
  async decryptMessage(encryptedContent, encryptedAESKey, iv, privateKeyPEM) {
    try {
      // 1. Importam cheia privata RSA
      const privateKey = await this.importPrivateKey(privateKeyPEM);
      
      // 2. Decriptam cheia AES cu RSA
      const aesKeyBytes = await this.decryptRSA(encryptedAESKey, privateKey);
      
      // 3. Importam cheia AES
      const aesKey = await this.importAESKey(aesKeyBytes);
      
      // 4. Decriptam mesajul cu AES
      const decrypted = await this.decryptAES(encryptedContent, aesKey, iv);
      
      return decrypted;
    } catch (error) {
      console.error('Eroare la decriptare client-side:', error);
      throw new Error('Decriptarea a esuat. Verificati cheia privata.');
    }
  }
  
  /**
   * Decripteaza un fisier criptat (schema hibrida AES+RSA)
   * 
   * @param {ArrayBuffer} encryptedFileBuffer - Continutul criptat al fisierului
   * @param {string} encryptedAESKey - Cheia AES criptata cu RSA (base64)
   * @param {string} iv - Vector de initializare (base64)
   * @param {string} privateKeyPEM - Cheia privata RSA in format PEM
   * @returns {ArrayBuffer} - Continutul decriptat al fisierului
   */
  async decryptFile(encryptedFileBuffer, encryptedAESKey, iv, privateKeyPEM) {
    try {
      // 1. Importam cheia privata RSA
      const privateKey = await this.importPrivateKey(privateKeyPEM);
      
      // 2. Decriptam cheia AES cu RSA
      const aesKeyBytes = await this.decryptRSA(encryptedAESKey, privateKey);
      
      // 3. Importam cheia AES
      const aesKey = await this.importAESKey(aesKeyBytes);
      
      // 4. Decriptam fisierul cu AES
      const ivBuffer = base64ToArrayBuffer(iv);
      const decrypted = await this.decryptAESBinary(encryptedFileBuffer, aesKey, ivBuffer);
      
      return decrypted;
    } catch (error) {
      console.error('Eroare la decriptare fisier client-side:', error);
      throw new Error('Decriptarea fisierului a esuat. Verificati cheia privata.');
    }
  }
}

// Export instanta singleton
export const cryptoClient = new CryptoClient();

/**
 * Informatii educationale despre algoritmii folositi
 */
export const encryptionInfo = {
  aes: {
    name: 'AES-256-CBC',
    fullName: 'Advanced Encryption Standard',
    keySize: '256 biti',
    blockSize: '128 biti',
    mode: 'CBC (Cipher Block Chaining)',
    description: 'AES este un algoritm de criptare simetrica - foloseste aceeasi cheie pentru criptare si decriptare. Este rapid si eficient pentru date mari.',
    usage: 'Cripteaza continutul mesajelor si fisierelor',
    security: 'Considerat sigur impotriva tuturor atacurilor cunoscute. Folosit de guverne si institutii financiare.',
  },
  rsa: {
    name: 'RSA-2048',
    fullName: 'Rivest-Shamir-Adleman',
    keySize: '2048 biti',
    padding: 'OAEP (Optimal Asymmetric Encryption Padding)',
    hash: 'SHA-256',
    description: 'RSA este un algoritm de criptare asimetrica - foloseste doua chei diferite: publica (pentru criptare) si privata (pentru decriptare).',
    usage: 'Cripteaza cheile AES pentru schimb securizat',
    security: 'Securitatea se bazeaza pe dificultatea factorizarii numerelor mari.',
  },
  hybrid: {
    name: 'Schema Hibrida',
    description: 'Combina avantajele ambelor tipuri de criptare: viteza AES pentru date mari si securitatea RSA pentru schimbul de chei.',
    flow: [
      '1. Se genereaza o cheie AES aleatorie pentru fiecare mesaj',
      '2. Mesajul este criptat cu AES-256-CBC',
      '3. Cheia AES este criptata cu RSA pentru fiecare destinatar',
      '4. Se trimite: mesaj_criptat + cheie_AES_criptata + IV',
    ],
    advantages: [
      'Viteza: AES este mult mai rapid decat RSA pentru date mari',
      'Securitate: RSA permite schimb de chei fara canal pre-partajat',
      'Forward secrecy partial: fiecare mesaj are cheie unica',
    ],
  },
};
