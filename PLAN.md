# Plan Implementare - Aplicatie Chat Securizat cu AES și RSA

## Arhitectura Generală

```
ProjectCripto/
├── app/                      # Backend Flask
│   ├── __init__.py
│   ├── app.py               # Entry point Flask
│   ├── config.py            # Configurari aplicatie
│   ├── models/              # Modele SQLAlchemy
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── conversation.py
│   │   └── message.py
│   ├── services/            # Business logic (SOLID)
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── chat_service.py
│   │   ├── crypto_service.py
│   │   └── file_service.py
│   ├── routes/              # API endpoints
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── chat_routes.py
│   │   └── file_routes.py
│   └── utils/               # Utilitare
│       └── __init__.py
├── web/                      # Frontend React
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.js
│   └── package.json
├── data/                     # SQLite database & uploads
├── docs/                     # Documentatie
│   └── DOCUMENTATIE.md
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Schema Baza de Date (SQLite)

### Tabela: users
| Coloana | Tip | Descriere |
|---------|-----|-----------|
| id | INTEGER PK | ID unic utilizator |
| username | VARCHAR(50) | Nume utilizator unic |
| email | VARCHAR(100) | Email unic |
| password_hash | VARCHAR(255) | Parola hash (bcrypt) |
| public_key | TEXT | Cheie publica RSA (PEM) |
| private_key_encrypted | TEXT | Cheie privata criptata cu parola |
| created_at | DATETIME | Data creare cont |
| last_seen | DATETIME | Ultima activitate |

### Tabela: conversations
| Coloana | Tip | Descriere |
|---------|-----|-----------|
| id | INTEGER PK | ID conversatie |
| created_at | DATETIME | Data creare |
| updated_at | DATETIME | Ultima actualizare |

### Tabela: conversation_participants
| Coloana | Tip | Descriere |
|---------|-----|-----------|
| id | INTEGER PK | ID |
| conversation_id | INTEGER FK | Referinta conversatie |
| user_id | INTEGER FK | Referinta utilizator |
| joined_at | DATETIME | Data aderare |
| unread_count | INTEGER | Mesaje necitite |

### Tabela: messages
| Coloana | Tip | Descriere |
|---------|-----|-----------|
| id | INTEGER PK | ID mesaj |
| conversation_id | INTEGER FK | Referinta conversatie |
| sender_id | INTEGER FK | Expeditor |
| encrypted_content | TEXT | Continut criptat AES |
| encrypted_aes_key | TEXT | Cheie AES criptata RSA |
| iv | VARCHAR(32) | Vector initializare AES |
| message_type | VARCHAR(20) | text/image/file |
| file_name | VARCHAR(255) | Nume fisier original |
| file_path | VARCHAR(255) | Cale fisier pe server |
| created_at | DATETIME | Data trimitere |

## Fluxul de Criptare

### Trimitere Mesaj:
1. Generare cheie AES aleatorie (256 bit)
2. Criptare mesaj cu AES-CBC
3. Pentru fiecare destinatar:
   - Criptare cheie AES cu cheia publica RSA a destinatarului
4. Stocare: mesaj_criptat + cheie_AES_criptata + IV

### Primire Mesaj:
1. Decriptare cheie AES cu cheia privata RSA proprie
2. Decriptare mesaj cu cheia AES si IV
3. Afisare mesaj in clar

## API Endpoints

### Autentificare
- POST /api/auth/register - Inregistrare cont nou
- POST /api/auth/login - Autentificare
- POST /api/auth/logout - Deconectare
- GET /api/auth/me - Date utilizator curent

### Utilizatori
- GET /api/users/search?q= - Cautare utilizatori
- GET /api/users/:id - Profil utilizator

### Conversatii
- GET /api/conversations - Lista conversatii
- POST /api/conversations - Creare conversatie noua
- GET /api/conversations/:id - Detalii conversatie
- GET /api/conversations/:id/messages - Mesaje conversatie
- POST /api/conversations/:id/messages - Trimitere mesaj
- PUT /api/conversations/:id/read - Marcare ca citit

### Fisiere
- POST /api/files/upload - Incarcare fisier criptat
- GET /api/files/:id - Descarcare fisier

## Pasi Implementare

1. **Setup Database** - Modele SQLAlchemy, migrari
2. **Services Layer** - AuthService, ChatService, CryptoService
3. **API Routes** - Endpoints REST
4. **Frontend React** - Componente UI
5. **Integrare** - Conectare frontend-backend
6. **Tooltips** - Explicatii educationale
7. **Documentatie** - MD cu detalii tehnice
