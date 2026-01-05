# SecureChat - Documentație Tehnică

## Aplicație de Chat cu Criptare End-to-End

---

### Cuprins

1. [Introducere](#1-introducere)
2. [Arhitectura Sistemului](#2-arhitectura-sistemului)
3. [Fundamentele Criptografice](#3-fundamentele-criptografice)
4. [Implementarea Criptării](#4-implementarea-criptării)
5. [Structura Bazei de Date](#5-structura-bazei-de-date)
6. [Fluxul de Autentificare](#6-fluxul-de-autentificare)
7. [Fluxul de Mesagerie](#7-fluxul-de-mesagerie)
8. [Gestionarea Fișierelor](#8-gestionarea-fișierelor)
9. [Interfața Utilizator](#9-interfața-utilizator)
10. [Deployment și Configurare](#10-deployment-și-configurare)
11. [Concluzii](#11-concluzii)

---

## 1. Introducere

### 1.1 Scopul Proiectului

SecureChat este o aplicație de mesagerie instantanee care demonstrează implementarea practică a criptării end-to-end folosind algoritmii **AES (Advanced Encryption Standard)** și **RSA (Rivest-Shamir-Adleman)**. Proiectul a fost dezvoltat în scop educațional pentru a ilustra modul în care acești algoritmi criptografici sunt utilizați în aplicațiile moderne de comunicare securizată.

### 1.2 Obiective

- Demonstrarea practică a criptării simetrice (AES-256-CBC)
- Demonstrarea practică a criptării asimetrice (RSA-2048)
- Implementarea unei scheme hibride de criptare
- Transfer securizat de fișiere cu criptare
- Persistența securizată a mesajelor
- Interfață educațională cu explicații vizuale ale procesului criptografic

### 1.3 Tehnologii Utilizate

| Componentă | Tehnologie | Versiune |
|------------|------------|----------|
| Backend | Flask | 3.0.0 |
| Frontend | React | 18.2.0 |
| Bază de Date | SQLite + SQLAlchemy | 2.0.23 |
| Criptografie | cryptography (Python) | 41.0.7 |
| Containerizare | Docker | 20.10+ |
| HTTP Client | Axios | 1.6.2 |

---

## 2. Arhitectura Sistemului

### 2.1 Diagrama Arhitecturală

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (React)                           │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────────┐  ┌──────────────────────────┐│
│  │  Pagini   │  │  Componente   │  │      Servicii            ││
│  │ - Login   │  │ - Sidebar     │  │ - api.js (HTTP Client)   ││
│  │ - Register│  │ - MessageArea │  │ - Gestionare sesiune     ││
│  │ - Chat    │  │ - Message     │  │                          ││
│  │           │  │ - CryptoInfo  │  │                          ││
│  └───────────┘  └───────────────┘  └──────────────────────────┘│
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP/REST API
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       SERVER (Flask)                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                      API Routes                            │ │
│  │  /api/auth/*    /api/conversations/*    /api/files/*       │ │
│  └───────────────────────┬────────────────────────────────────┘ │
│                          │                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Service Layer                           │ │
│  │  AuthService  ChatService  CryptoService  FileService      │ │
│  └───────────────────────┬────────────────────────────────────┘ │
│                          │                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Data Layer (Models)                     │ │
│  │  User  Conversation  ConversationParticipant  Message      │ │
│  │                    MessageAttachment                       │ │
│  └───────────────────────┬────────────────────────────────────┘ │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │   SQLite Database       │
              │   + Encrypted Files     │
              │     (uploads/)          │
              └─────────────────────────┘
```

### 2.2 Principii de Design

Aplicația urmează principiile **SOLID**:

1. **S**ingle Responsibility Principle
   - Fiecare serviciu are o singură responsabilitate
   - `CryptoService` - doar operații criptografice
   - `AuthService` - doar autentificare și gestionare utilizatori
   - `ChatService` - doar logica de conversații și mesaje
   - `FileService` - doar gestionarea fișierelor criptate

2. **O**pen/Closed Principle
   - Serviciile sunt deschise pentru extensie
   - Interfețele abstracte permit înlocuirea implementărilor

3. **L**iskov Substitution Principle
   - Implementările pot fi substituite fără a afecta comportamentul

4. **I**nterface Segregation Principle
   - Interfețe mici, specifice pentru fiecare serviciu

5. **D**ependency Inversion Principle
   - Modulele de nivel înalt nu depind de cele de nivel jos
   - Ambele depind de abstracții (interfețe)

---

## 3. Fundamentele Criptografice

### 3.1 Criptarea Simetrică - AES

**AES (Advanced Encryption Standard)** este un algoritm de criptare simetrică adoptat de guvernul SUA și utilizat la nivel mondial pentru securizarea datelor.

#### Caracteristici AES-256-CBC

| Parametru | Valoare | Descriere |
|-----------|---------|-----------|
| Dimensiune cheie | 256 biți | Oferă securitate maximă |
| Dimensiune bloc | 128 biți | Standardul AES |
| Mod de operare | CBC | Cipher Block Chaining |
| IV (Vector de Inițializare) | 128 biți | Generat aleatoriu pentru fiecare mesaj |
| Padding | PKCS7 | Standard pentru completare blocuri |

#### Principiul de Funcționare

```
Plaintext: "Hello World!"
    │
    ▼
┌─────────────────┐
│  Padding PKCS7  │  ← Completare la multiplu de 16 bytes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  XOR cu IV      │  ← Pentru primul bloc
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Criptare AES    │  ← Cu cheia de 256 biți
│ (14 runde)      │
└────────┬────────┘
         │
         ▼
Ciphertext: "a7f3b2c1..."
```

#### Avantajele AES

1. **Viteză** - Foarte rapid pentru volume mari de date
2. **Securitate** - Nu există atacuri practice cunoscute contra AES-256
3. **Eficiență** - Suport hardware în procesoarele moderne (AES-NI)

### 3.2 Criptarea Asimetrică - RSA

**RSA (Rivest-Shamir-Adleman)** este un algoritm de criptare asimetrică bazat pe dificultatea factorizării numerelor mari.

#### Caracteristici RSA-2048

| Parametru | Valoare | Descriere |
|-----------|---------|-----------|
| Dimensiune cheie | 2048 biți | Standard recomandat până în 2030 |
| Padding | OAEP | Optimal Asymmetric Encryption Padding |
| Hash | SHA-256 | Pentru OAEP |
| Exponent public | 65537 | Număr prim Fermat standard |

#### Generarea Perechii de Chei

```
1. Alegere numere prime mari (p, q)
   p, q = numere prime de ~1024 biți fiecare
   
2. Calcul n = p × q
   n = modul de 2048 biți
   
3. Calcul φ(n) = (p-1)(q-1)
   φ(n) = totient Euler
   
4. Alegere e (exponent public)
   e = 65537 (coprim cu φ(n))
   
5. Calcul d (exponent privat)
   d × e ≡ 1 (mod φ(n))

Cheie Publică:  (e, n) - Poate fi distribuită public
Cheie Privată: (d, n) - Trebuie păstrată secretă
```

#### Criptare și Decriptare

```
Criptare: C = M^e mod n  (folosind cheia publică)
Decriptare: M = C^d mod n  (folosind cheia privată)
```

### 3.3 Schema Hibridă de Criptare

Aplicația folosește o schemă hibridă care combină avantajele ambilor algoritmi:

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXPEDITOR (Alice)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Generare cheie AES aleatorie (256 biți)                    │
│     AES_KEY = random_bytes(32)                                 │
│                                                                 │
│  2. Generare IV aleatoriu (128 biți)                           │
│     IV = random_bytes(16)                                      │
│                                                                 │
│  3. Criptare mesaj cu AES                                      │
│     CIPHERTEXT = AES_CBC_Encrypt(MESSAGE, AES_KEY, IV)         │
│                                                                 │
│  4. Criptare cheie AES cu RSA pentru fiecare destinatar        │
│     ENCRYPTED_KEY[alice] = RSA_Encrypt(AES_KEY, alice_pubkey)  │
│     ENCRYPTED_KEY[bob] = RSA_Encrypt(AES_KEY, bob_pubkey)      │
│                                                                 │
│  5. Trimitere: IV + CIPHERTEXT + ENCRYPTED_KEYS               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

                              │
                              ▼

┌─────────────────────────────────────────────────────────────────┐
│                    DESTINATAR (Bob)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Extrage cheia AES criptată pentru el                       │
│     encrypted_key = ENCRYPTED_KEY[bob]                         │
│                                                                 │
│  2. Decriptare cheie AES cu RSA                                │
│     AES_KEY = RSA_Decrypt(encrypted_key, bob_private_key)      │
│                                                                 │
│  3. Decriptare mesaj cu AES                                    │
│     MESSAGE = AES_CBC_Decrypt(CIPHERTEXT, AES_KEY, IV)         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### De Ce Schemă Hibridă?

| Criteriu | AES | RSA | Soluția Hibridă |
|----------|-----|-----|-----------------|
| Viteză | ✅ Foarte rapid | ❌ Lent | ✅ Rapid |
| Distribuție chei | ❌ Problematică | ✅ Simplă | ✅ Simplă |
| Dimensiune date | ✅ Nelimitat | ❌ Limitat | ✅ Nelimitat |
| Securitate | ✅ Ridicată | ✅ Ridicată | ✅ Maximă |

---

## 4. Implementarea Criptării

### 4.1 Serviciul de Criptografie (CryptoService)

Serviciul de criptografie este responsabil pentru toate operațiile criptografice:

```python
class CryptoService:
    """
    Serviciu pentru operații criptografice.
    
    Responsabilități:
    - Generare perechi de chei RSA
    - Criptare/decriptare AES-256-CBC
    - Criptare/decriptare RSA-2048
    - Criptare mesaje pentru destinatari multipli
    """
```

### 4.2 Generarea Cheilor RSA

```python
def generate_rsa_key_pair(self) -> Tuple[bytes, bytes]:
    """
    Generează o pereche de chei RSA-2048.
    
    Returns:
        Tuple[bytes, bytes]: (private_key_pem, public_key_pem)
    """
    # Generăm cheia privată RSA-2048
    private_key = rsa.generate_private_key(
        public_exponent=65537,  # Exponent standard
        key_size=2048,          # 2048 biți pentru securitate
        backend=default_backend()
    )
    
    # Serializăm cheia privată în format PEM
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Extragem și serializăm cheia publică
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return private_pem, public_pem
```

### 4.3 Criptarea cu AES-256-CBC

```python
def encrypt_with_aes(self, data: bytes, key: bytes) -> Tuple[bytes, bytes]:
    """
    Criptează date cu AES-256-CBC.
    
    Args:
        data: Datele de criptat
        key: Cheia AES de 32 bytes (256 biți)
        
    Returns:
        Tuple[bytes, bytes]: (encrypted_data, iv)
    """
    # Generăm un IV aleatoriu de 16 bytes
    iv = os.urandom(16)
    
    # Creăm cipher-ul AES în mod CBC
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    
    # Aplicăm padding PKCS7
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    # Criptăm datele
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    
    return encrypted_data, iv
```

### 4.4 Criptarea cu RSA-2048

```python
def encrypt_with_rsa(self, data: bytes, public_key_pem: bytes) -> bytes:
    """
    Criptează date cu cheia publică RSA.
    
    Args:
        data: Datele de criptat (max ~190 bytes pentru RSA-2048)
        public_key_pem: Cheia publică în format PEM
        
    Returns:
        bytes: Datele criptate
    """
    # Încărcăm cheia publică
    public_key = serialization.load_pem_public_key(
        public_key_pem,
        backend=default_backend()
    )
    
    # Criptăm cu OAEP padding pentru securitate maximă
    encrypted = public_key.encrypt(
        data,
        asym_padding.OAEP(
            mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    
    return encrypted
```

### 4.5 Criptarea Mesajelor pentru Conversații

```python
def encrypt_message_for_recipients(
    self, 
    message: str, 
    recipient_public_keys: Dict[int, bytes]
) -> Dict:
    """
    Criptează un mesaj pentru toți participanții unei conversații.
    
    Args:
        message: Mesajul în clar
        recipient_public_keys: Dict cu {user_id: public_key_pem}
        
    Returns:
        Dict cu encrypted_content, iv, encrypted_aes_keys
    """
    # Generăm o cheie AES temporară pentru acest mesaj
    aes_key = os.urandom(32)  # 256 biți
    
    # Criptăm mesajul cu AES
    encrypted_content, iv = self.encrypt_with_aes(
        message.encode('utf-8'), 
        aes_key
    )
    
    # Criptăm cheia AES cu RSA pentru fiecare destinatar
    encrypted_keys = {}
    for user_id, public_key in recipient_public_keys.items():
        encrypted_key = self.encrypt_with_rsa(aes_key, public_key)
        encrypted_keys[str(user_id)] = base64.b64encode(encrypted_key).decode()
    
    return {
        'encrypted_content': base64.b64encode(encrypted_content).decode(),
        'iv': base64.b64encode(iv).decode(),
        'encrypted_aes_keys': encrypted_keys
    }
```

---

## 5. Structura Bazei de Date

### 5.1 Diagrama Entitate-Relație

```
┌──────────────────┐       ┌─────────────────────────┐
│      User        │       │ ConversationParticipant │
├──────────────────┤       ├─────────────────────────┤
│ id (PK)          │───┐   │ id (PK)                 │
│ username         │   │   │ conversation_id (FK)    │
│ email            │   └──▶│ user_id (FK)            │
│ password_hash    │       │ joined_at               │
│ public_key       │       │ last_read_at            │
│ avatar_color     │       └─────────────────────────┘
│ created_at       │                   │
└──────────────────┘                   │
         │                             ▼
         │                ┌─────────────────────────┐
         │                │     Conversation        │
         │                ├─────────────────────────┤
         │                │ id (PK)                 │
         │                │ name                    │
         │                │ is_group                │
         │                │ created_at              │
         │                │ updated_at              │
         │                └─────────────────────────┘
         │                             │
         │                             ▼
         │                ┌─────────────────────────┐
         │                │       Message           │
         │                ├─────────────────────────┤
         └───────────────▶│ id (PK)                 │
                          │ conversation_id (FK)    │
                          │ sender_id (FK)          │
                          │ encrypted_content       │
                          │ iv                      │
                          │ encrypted_aes_keys      │
                          │ message_type            │
                          │ created_at              │
                          └─────────────────────────┘
                                       │
                                       ▼
                          ┌─────────────────────────┐
                          │   MessageAttachment     │
                          ├─────────────────────────┤
                          │ id (PK)                 │
                          │ message_id (FK)         │
                          │ original_filename       │
                          │ encrypted_path          │
                          │ mime_type               │
                          │ size                    │
                          │ encrypted_aes_keys      │
                          │ iv                      │
                          │ created_at              │
                          └─────────────────────────┘
```

### 5.2 Modelul User

```python
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Cheia publică RSA (vizibilă pentru toți)
    public_key = db.Column(db.Text, nullable=False)
    
    # Culoare avatar generată aleatoriu
    avatar_color = db.Column(db.String(7), default='#3b82f6')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Note despre securitate:**
- Parola este stocată ca hash folosind Werkzeug (bcrypt-like)
- Cheia privată este returnată utilizatorului la înregistrare și poate fi descărcată
- Cheia privată NU este stocată pe server după înregistrare

### 5.3 Modelul Message

```python
class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Conținutul criptat cu AES-256-CBC
    encrypted_content = db.Column(db.Text, nullable=False)
    iv = db.Column(db.String(32), nullable=False)  # Base64 encoded
    
    # Chei AES criptate cu RSA pentru fiecare participant
    encrypted_aes_keys = db.Column(db.Text, nullable=False)  # JSON
    
    # Tipul mesajului: text, image, file
    message_type = db.Column(db.String(20), default='text')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Structura `encrypted_aes_keys` (JSON):**
```json
{
    "1": "Base64EncodedRSAEncryptedKeyForUser1==",
    "2": "Base64EncodedRSAEncryptedKeyForUser2==",
    "3": "Base64EncodedRSAEncryptedKeyForUser3=="
}
```

### 5.4 Modelul MessageAttachment

```python
class MessageAttachment(db.Model):
    __tablename__ = 'message_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('messages.id'))
    
    # Informații despre fișier
    original_filename = db.Column(db.String(255), nullable=False)
    encrypted_path = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(100))
    size = db.Column(db.Integer)  # bytes
    
    # Criptare separată pentru fișiere
    encrypted_aes_keys = db.Column(db.Text, nullable=False)
    iv = db.Column(db.String(32), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

---

## 6. Fluxul de Autentificare

### 6.1 Înregistrare Utilizator

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUX ÎNREGISTRARE                            │
└─────────────────────────────────────────────────────────────────┘

Client                                                    Server
  │                                                          │
  │  1. POST /api/auth/register                              │
  │     {username, email, password}                          │
  │  ─────────────────────────────────────────────────────▶  │
  │                                                          │
  │                    2. Validare date                      │
  │                    3. Hash parolă                        │
  │                    4. Generare pereche RSA-2048          │
  │                    5. Stocare în DB (fără cheia privată) │
  │                                                          │
  │  6. Response                                             │
  │     {success: true, user: {...}, private_key: "..."}     │
  │  ◀─────────────────────────────────────────────────────  │
  │                                                          │
  │  7. Afișare modal cu cheia privată                       │
  │  8. Utilizatorul poate descărca cheia în fișier .pem     │
  │  9. Stocare cheie în localStorage                        │
  │                                                          │
```

**Important:** Cheia privată este returnată o singură dată, la înregistrare. Utilizatorul poate:
- Descărca cheia într-un fișier `.pem` pentru backup
- Cheia este salvată automat în browser (localStorage)

### 6.2 Autentificare

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUX AUTENTIFICARE                           │
└─────────────────────────────────────────────────────────────────┘

Client                                                    Server
  │                                                          │
  │  1. POST /api/auth/login                                 │
  │     {username, password}                                 │
  │  ─────────────────────────────────────────────────────▶  │
  │                                                          │
  │                    2. Căutare user în DB                 │
  │                    3. Verificare hash parolă             │
  │                    4. Creare sesiune Flask               │
  │                                                          │
  │  5. Response                                             │
  │     {success: true, user: {id, username, public_key}}    │
  │     + Cookie sesiune                                     │
  │  ◀─────────────────────────────────────────────────────  │
  │                                                          │
  │  6. Verificare cheie privată în localStorage             │
  │  7. Dacă lipsește, afișare modal pentru introducere      │
  │                                                          │
```

### 6.3 Gestionarea Cheii Private

Utilizatorul poate configura cheia privată din:
1. **Modal la înregistrare** - cu opțiune de descărcare
2. **Buton "Criptare end-to-end"** din sidebar - deschide modalul de configurare
3. **Import din fișier** - dacă a salvat cheia anterior

---

## 7. Fluxul de Mesagerie

### 7.1 Trimiterea unui Mesaj Text

```
┌─────────────────────────────────────────────────────────────────┐
│                 FLUX TRIMITERE MESAJ                            │
└─────────────────────────────────────────────────────────────────┘

                       Alice (Sender)
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │ 1. Compunere mesaj: "Hello Bob!"      │
        └───────────────────┬───────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │ 2. POST /api/conversations/{id}/messages
        │    {content: "Hello Bob!"}            │
        └───────────────────┬───────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SERVER                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  3. Obține participanții conversației                           │
│     participants = [alice, bob]                                 │
│                                                                  │
│  4. Obține cheile publice                                       │
│     public_keys = {alice_id: key1, bob_id: key2}                │
│                                                                  │
│  5. Generează cheie AES aleatorie                               │
│     aes_key = random_bytes(32)                                  │
│                                                                  │
│  6. Generează IV aleatoriu                                      │
│     iv = random_bytes(16)                                       │
│                                                                  │
│  7. Criptează conținutul cu AES-256-CBC                         │
│     encrypted = AES_CBC(content, aes_key, iv)                   │
│                                                                  │
│  8. Criptează cheia AES pentru fiecare participant              │
│     encrypted_keys = {                                          │
│       alice_id: RSA(aes_key, alice_public_key),                │
│       bob_id: RSA(aes_key, bob_public_key)                     │
│     }                                                           │
│                                                                  │
│  9. Salvează în baza de date                                    │
│     Message(encrypted_content, iv, encrypted_keys)              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │ 10. Response: mesaj creat cu succes   │
        └───────────────────────────────────────┘
```

### 7.2 Citirea și Decriptarea unui Mesaj

```
┌─────────────────────────────────────────────────────────────────┐
│                   FLUX DECRIPTARE MESAJ                         │
└─────────────────────────────────────────────────────────────────┘

                         Bob (Reader)
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │ 1. GET /api/conversations/{id}/messages
        └───────────────────┬───────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │ 2. Primește mesaje criptate           │
        │    [{encrypted_content, iv,           │
        │      encrypted_aes_keys}]             │
        └───────────────────┬───────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │ 3. Click buton "Decriptează"          │
        │    POST /api/messages/{id}/decrypt    │
        │    {private_key: "-----BEGIN..."}     │
        └───────────────────┬───────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                         SERVER                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  4. Extrage cheia AES criptată pentru Bob                       │
│     encrypted_aes = message.encrypted_aes_keys[bob_id]          │
│                                                                  │
│  5. Decriptează cheia AES cu RSA                                │
│     aes_key = RSA_Decrypt(encrypted_aes, bob_private_key)       │
│                                                                  │
│  6. Decriptează conținutul cu AES                               │
│     content = AES_Decrypt(encrypted_content, aes_key, iv)       │
│                                                                  │
│  7. Returnează mesajul decriptat                                │
│     {decrypted_content: "Hello Bob!"}                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3 Auto-Decriptare

Dacă utilizatorul are cheia privată configurată în browser, mesajele sunt decriptate automat la încărcarea conversației. Indicatori vizuali:
- 🔒 **Mesaj criptat** - cheia privată nu este configurată
- ✓ **Mesaj vizibil** - decriptat cu succes

---

## 8. Gestionarea Fișierelor

### 8.1 Upload Fișiere Multiple

Aplicația suportă upload de fișiere multiple într-un singur mesaj:

```
┌─────────────────────────────────────────────────────────────────┐
│                 FLUX UPLOAD FIȘIERE                             │
└─────────────────────────────────────────────────────────────────┘

  1. Utilizator selectează unul sau mai multe fișiere
            │
            ▼
  2. POST /api/files/upload/{conversation_id}
     - FormData cu fișierele
            │
            ▼
  ┌─────────────────────────────────────────────────────────────┐
  │                       SERVER                                 │
  ├─────────────────────────────────────────────────────────────┤
  │                                                              │
  │  3. Pentru fiecare fișier:                                  │
  │     a. Validare dimensiune (max 16MB)                       │
  │     b. Generare cheie AES unică                             │
  │     c. Criptare conținut cu AES-256-CBC                     │
  │     d. Salvare fișier criptat: /uploads/{uuid}.enc          │
  │     e. Criptare cheie AES pentru participanți               │
  │                                                              │
  │  4. Returnare informații fișiere temporare                  │
  │     [{temp_id, name, size, encrypted_path, ...}]            │
  │                                                              │
  └─────────────────────────────────────────────────────────────┘
            │
            ▼
  3. POST /api/files/send/{conversation_id}
     - content: "Textul mesajului (opțional)"
     - attachments: [informații fișiere]
            │
            ▼
  4. Creare mesaj cu atașamente în DB
```

### 8.2 Download Fișier Criptat

```python
def download_attachment(attachment_id: int, private_key: str):
    """
    Decriptează și returnează un fișier atașat.
    
    1. Obține atașamentul din DB
    2. Citește fișierul criptat de pe disk
    3. Extrage cheia AES criptată pentru utilizator
    4. Decriptează cheia AES cu RSA (cheia privată)
    5. Decriptează fișierul cu AES
    6. Returnează fișierul decriptat
    """
```

### 8.3 Tipuri de Fișiere Suportate

| Categorie | Extensii | Descriere |
|-----------|----------|-----------|
| Imagini | jpg, jpeg, png, gif, webp | Afișate inline cu preview |
| Documente | pdf, doc, docx, xls, xlsx | Download cu iconiță specifică |
| Arhive | zip, rar, 7z | Download standard |
| Altele | orice tip | Acceptate toate tipurile de fișiere |

**Limite:**
- Dimensiune maximă per fișier: 16 MB
- Fișierele sunt criptate individual

---

## 9. Interfața Utilizator

### 9.1 Structura Componentelor React

```
web/src/
├── App.js                 # Componenta principală, routing, AuthContext
├── index.js               # Entry point
├── index.css              # Variabile CSS și stiluri globale
│
├── services/
│   └── api.js             # Serviciu HTTP (axios) cu interceptori
│
├── pages/
│   ├── LoginPage.js       # Pagina de autentificare
│   ├── LoginPage.css
│   ├── RegisterPage.js    # Pagina de înregistrare + modal cheie privată
│   ├── AuthPages.css      # Stiluri comune autentificare
│   └── ChatPage.js        # Pagina principală de chat
│   └── ChatPage.css
│
└── components/
    ├── Sidebar.js         # Lista conversații, căutare utilizatori
    ├── Sidebar.css
    ├── MessageArea.js     # Zona de mesaje, input, upload fișiere
    ├── MessageArea.css
    ├── Message.js         # Componentă mesaj individual
    ├── Message.css
    └── CryptoInfoPanel.js # Panou educațional despre criptare
    └── CryptoInfoPanel.css
```

### 9.2 Componenta Sidebar

Funcționalități:
- **Profil utilizator** - avatar, nume, status
- **Căutare utilizatori** - pentru inițierea conversațiilor noi
- **Lista conversații** - ordonate după ultima activitate
- **Indicator mesaje necitite** - badge cu număr
- **Ștergere conversație** - buton cu confirmare (apare la hover)
- **Buton criptare** - deschide modalul pentru cheia privată

### 9.3 Componenta MessageArea

Funcționalități:
- **Header conversație** - nume partener, status criptare
- **Lista mesaje** - cu scroll automat la mesaje noi
- **Mesaje criptate/decriptate** - indicator vizual
- **Upload fișiere** - drag & drop sau buton
- **Preview atașamente** - înainte de trimitere
- **Input mesaj** - textarea cu auto-resize
- **Timestamp** - pentru fiecare mesaj

### 9.4 Componenta Message

Afișează un mesaj individual cu:
- **Avatar expeditor** - culoare unică per utilizator
- **Conținut** - text sau indicator criptat
- **Timestamp** - ora și data
- **Atașamente** - cu iconițe specifice tipului
- **Buton decriptare** - dacă nu e configurat auto-decrypt
- **Buton descărcare** - pentru fișiere atașate

---

## 10. Deployment și Configurare

### 10.1 Cerințe Sistem

- **Python** 3.9+
- **Node.js** 18+
- **Docker** 20.10+ (opțional)

### 10.2 Instalare Locală

```bash
# Clonare repository
git clone <repository-url>
cd SecureChat

# Backend
cd app
pip install -r ../requirements.txt
python app.py

# Frontend (terminal separat)
cd web
npm install
npm start
```

**Accesare:** http://localhost:3000

### 10.3 Docker Deployment

```bash
# Development (două containere separate)
docker-compose up backend frontend

# Accesare: http://localhost:3000
```

### 10.4 Structura Docker

```yaml
services:
  backend:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./app:/app
      - ./data:/app/data
    environment:
      - FLASK_ENV=development

  frontend:
    build:
      context: ./web
    ports:
      - "3000:3000"
    volumes:
      - ./web/src:/app/src
    depends_on:
      - backend
```

### 10.5 Variabile de Mediu

| Variabilă | Descriere | Default |
|-----------|-----------|---------|
| `FLASK_ENV` | development/production | development |
| `SECRET_KEY` | Cheie pentru sesiuni Flask | (auto-generat) |
| `DATABASE_URL` | URI bază de date | sqlite:///data/chat.db |
| `UPLOAD_FOLDER` | Director pentru fișiere | ./data/uploads |
| `MAX_CONTENT_LENGTH` | Dimensiune maximă upload | 16MB |

---

## 11. Concluzii

### 11.1 Rezumat Caracteristici

Aplicația SecureChat implementează:

1. **Criptare End-to-End Completă**
   - Mesajele sunt criptate pe server și decriptate doar de destinatari
   - Fiecare mesaj folosește o cheie AES unică
   - Cheile AES sunt criptate individual pentru fiecare participant

2. **Schema Hibridă AES+RSA**
   - AES-256-CBC pentru criptarea eficientă a conținutului
   - RSA-2048 pentru distribuția securizată a cheilor
   - IV aleatoriu pentru fiecare operațiune de criptare

3. **Gestionare Securizată a Fișierelor**
   - Upload multiple fișiere simultan
   - Criptare individuală per fișier
   - Suport pentru orice tip de fișier

4. **Interfață Intuitivă**
   - Design modern și responsive
   - Indicatori vizuali pentru starea criptării
   - Opțiune de descărcare a cheii private

### 11.2 Aspecte de Securitate

| Aspect | Implementare |
|--------|--------------|
| Criptare mesaje | AES-256-CBC + RSA-2048 |
| Stocare parole | Hash cu Werkzeug |
| Cheia privată | Păstrată doar de utilizator |
| Sesiuni | Flask session cu cookie securizat |
| Transport | HTTPS recomandat în producție |

### 11.3 Limitări și Îmbunătățiri Posibile

| Limitare Actuală | Îmbunătățire Propusă |
|------------------|----------------------|
| Polling pentru mesaje noi | WebSockets pentru timp real |
| Decriptare pe server | Decriptare exclusiv pe client |
| Fără PFS | Implementare Double Ratchet |
| SQLite | PostgreSQL pentru scalabilitate |

### 11.4 Referințe

1. NIST FIPS 197 - Advanced Encryption Standard (AES)
2. PKCS #1 v2.2 - RSA Cryptography Standard
3. RFC 8017 - PKCS #1: RSA Cryptography Specifications
4. cryptography.io - Python Cryptography Documentation
5. Flask Documentation - https://flask.palletsprojects.com/
6. React Documentation - https://react.dev/

---

## Anexe

### A. Glossar

| Termen | Definiție |
|--------|-----------|
| AES | Advanced Encryption Standard - algoritm de criptare simetrică standardizat |
| RSA | Rivest-Shamir-Adleman - algoritm de criptare asimetrică |
| CBC | Cipher Block Chaining - mod de operare pentru criptare pe blocuri |
| IV | Initialization Vector - vector de inițializare aleatoriu |
| OAEP | Optimal Asymmetric Encryption Padding - padding pentru RSA |
| PEM | Privacy Enhanced Mail - format text pentru chei criptografice |
| PKCS | Public Key Cryptography Standards - standarde pentru criptografie |
| End-to-End | Criptare de la expeditor la destinatar, fără intermediari |

### B. Performanță

| Operație | Timp Mediu | Note |
|----------|------------|------|
| Generare RSA-2048 | ~100ms | O singură dată, la înregistrare |
| Criptare AES (1KB) | <1ms | Foarte rapid |
| Criptare RSA | ~5ms | Pentru cheia AES (32 bytes) |
| Hash parolă | ~100ms | Intenționat lent pentru securitate |
| Upload fișier 1MB | ~200ms | Include criptare |

### C. API Endpoints

| Endpoint | Metodă | Descriere |
|----------|--------|-----------|
| `/api/auth/register` | POST | Înregistrare utilizator |
| `/api/auth/login` | POST | Autentificare |
| `/api/auth/logout` | POST | Deconectare |
| `/api/conversations` | GET | Lista conversații |
| `/api/conversations` | POST | Creare conversație |
| `/api/conversations/{id}` | DELETE | Ștergere conversație |
| `/api/conversations/{id}/messages` | GET | Mesaje conversație |
| `/api/conversations/{id}/messages` | POST | Trimitere mesaj |
| `/api/messages/{id}/decrypt` | POST | Decriptare mesaj |
| `/api/files/upload/{id}` | POST | Upload fișiere |
| `/api/files/download/{id}` | POST | Download fișier |

---

*Document generat pentru proiectul universitar SecureChat*
*Versiunea 2.0 - Ianuarie 2026*
