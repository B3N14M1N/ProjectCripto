# SecureChat - Aplicație de Chat cu Criptare End-to-End

O aplicație completă de mesagerie care demonstrează implementarea practică a criptării hibride folosind AES-256-CBC și RSA-2048.

## 🔐 Caracteristici

- **Autentificare securizată** cu conturi de utilizator
- **Criptare end-to-end** pentru toate mesajele
- **Schema hibridă AES+RSA**:
  - Mesajele sunt criptate cu AES-256-CBC
  - Cheile AES sunt criptate cu RSA pentru fiecare destinatar
- **Suport pentru fișiere multiple** - upload/download criptat
- **Descărcare cheie privată** - backup în fișier .pem la înregistrare
- **Ștergere conversații** - cu confirmare
- **Interfață educațională** - vizualizarea procesului de criptare
- **Persistență** - SQLite pentru stocarea datelor

## 🛠️ Stack Tehnic

| Componentă | Tehnologie |
|------------|------------|
| Backend | Flask 3.0.0 |
| Frontend | React 18.2.0 |
| Database | SQLite + SQLAlchemy |
| Criptografie | cryptography 41.0.7 |
| Container | Docker |

## 🚀 Instalare și Rulare

### Opțiunea 1: Local (Development)

**Backend:**
```bash
cd app
pip install -r ../requirements.txt
python app.py
```

**Frontend (terminal separat):**
```bash
cd web
npm install
npm start
```

Accesează: http://localhost:3000

### Opțiunea 2: Docker Compose (Development)

```bash
docker-compose up backend frontend
```

Accesează: http://localhost:3000

### Opțiunea 3: Docker Production

```bash
docker-compose --profile prod up production
```

Accesează: http://localhost:5000

## 📁 Structura Proiectului

```
├── app/
│   ├── app.py              # Entry point Flask
│   ├── config.py           # Configurări
│   ├── models/             # Modele DB (User, Message, etc.)
│   ├── services/           # Servicii (Crypto, Auth, Chat, File)
│   └── routes/             # API endpoints
├── web/
│   ├── public/             # Static files
│   └── src/
│       ├── pages/          # React pages
│       ├── components/     # React components
│       └── services/       # API & crypto services
├── data/                   # SQLite DB & uploads
├── Dockerfile              # Production build
├── Dockerfile.dev          # Development build
├── docker-compose.yml      # Container orchestration
├── DOCUMENTATIE.md         # Documentație tehnică (RO)
└── requirements.txt        # Python dependencies
```

## 📖 Documentație

Consultă [DOCUMENTATIE.md](DOCUMENTATIE.md) pentru documentația tehnică completă în limba română, incluzând:
- Arhitectura sistemului
- Fundamentele criptografice
- Fluxuri de date
- Diagrame și explicații

## 🔒 Cum Funcționează Criptarea

1. **La înregistrare**: 
   - Se generează o pereche de chei RSA-2048 pentru utilizator
   - Cheia privată poate fi descărcată într-un fișier .pem pentru backup
   - Cheia este salvată și în localStorage-ul browserului
   
2. **La trimiterea mesajului**:
   - Se generează o cheie AES temporară (256 biți)
   - Mesajul este criptat cu AES-256-CBC
   - Cheia AES este criptată cu RSA pentru fiecare destinatar
   
3. **La citirea mesajului**:
   - Destinatarul decriptează cheia AES cu cheia sa privată RSA
   - Mesajul este decriptat cu cheia AES

## 📝 Note pentru Proiect Universitar

Acest proiect demonstrează:
- Principiile SOLID în design
- Separarea responsabilităților (MVC)
- Criptare simetrică (AES) și asimetrică (RSA)
- Schema hibridă de criptare
- Autentificare și autorizare
- REST API design

## 📄 Licență

Proiect educațional - MIT License

