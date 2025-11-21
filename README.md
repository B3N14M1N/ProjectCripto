# Secure Messaging System (AES + RSA)

This is a simple web application that demonstrates a hybrid encryption scheme using AES (Symmetric) and RSA (Asymmetric) algorithms.

## Features
- **RSA Key Generation**: Generate Public/Private key pairs.
- **Hybrid Encryption**:
  - Message is encrypted with a random AES key.
  - The AES key is encrypted with the Receiver's RSA Public Key.
- **Decryption**:
  - The Receiver uses their Private Key to decrypt the AES key.
  - The AES key is used to decrypt the message.
- **Debug Interface**: View internal states like generated keys, IVs, and encrypted blobs.

## Tech Stack
- **Backend**: Python (Flask), PyCryptodome
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Infrastructure**: Docker, Docker Compose

## How to Run

### Prerequisites
- Docker and Docker Compose installed.

### Steps
1. Open a terminal in this directory.
2. Run the application:
   ```bash
   docker-compose up --build
   ```
3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure
- `app/`: Source code
  - `crypto_service.py`: Core cryptography logic (SOLID principles).
  - `app.py`: Flask web server.
  - `templates/`: HTML frontend.
- `Dockerfile`: Container definition.
- `docker-compose.yml`: Service orchestration.
