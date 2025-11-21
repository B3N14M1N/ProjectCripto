from flask import Flask, render_template, request, jsonify
from crypto_service import SecureMessagingService

app = Flask(__name__)
crypto_service = SecureMessagingService()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-keys', methods=['POST'])
def generate_keys():
    private_key, public_key = crypto_service.generate_rsa_keys()
    return jsonify({
        "private_key": private_key,
        "public_key": public_key
    })

@app.route('/api/encrypt', methods=['POST'])
def encrypt():
    data = request.json
    message = data.get('message')
    public_key = data.get('public_key')
    
    if not message or not public_key:
        return jsonify({"error": "Missing message or public key"}), 400

    result = crypto_service.encrypt_flow(message, public_key)
    return jsonify(result)

@app.route('/api/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    encrypted_message = data.get('encrypted_message')
    encrypted_key = data.get('encrypted_aes_key')
    iv = data.get('iv')
    private_key = data.get('private_key')

    if not all([encrypted_message, encrypted_key, iv, private_key]):
        return jsonify({"error": "Missing decryption parameters"}), 400

    result = crypto_service.decrypt_flow(encrypted_message, encrypted_key, iv, private_key)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
