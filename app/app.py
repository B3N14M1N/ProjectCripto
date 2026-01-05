# app.py
# Entry point pentru aplicatia Flask de chat securizat
# Configureaza Flask, baza de date si rutele API
#
# Aceasta aplicatie demonstreaza criptarea end-to-end folosind:
# - AES-256-CBC pentru criptarea continutului mesajelor
# - RSA-2048 pentru schimbul securizat de chei

import os
from datetime import timedelta
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from models import db


def create_app(config_class=Config):
    """
    Factory function pentru crearea aplicatiei Flask.
    
    Avantaje:
    - Permite crearea mai multor instante (pentru testare)
    - Configurare flexibila
    - Organizare clara a initializarii
    
    Args:
        config_class: Clasa de configurare
        
    Returns:
        Flask app instance
    """
    app = Flask(__name__, 
                static_folder='../web/build',  # React build folder
                static_url_path='')
    
    # Incarcam configurarea
    app.config.from_object(config_class)
    
    # Setam cheia secreta explicit pentru sesiuni
    app.secret_key = app.config.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    
    # Initializam directoarele necesare
    config_class.init_app(app)
    
    # Configurare sesiuni
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False  # True in productie cu HTTPS
    
    # Initializam CORS pentru a permite requesturi din React
    # Acceptam toate originile in development
    CORS(app, 
         supports_credentials=True,
         origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'http://frontend:3000'])
    
    # Initializam baza de date
    db.init_app(app)
    
    # Cream tabelele daca nu exista
    with app.app_context():
        db.create_all()
    
    # Inregistram blueprint-urile (rutele API)
    from routes import auth_bp, chat_bp, file_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(file_bp)
    
    # Ruta pentru servirea aplicatiei React (productie)
    @app.route('/')
    def serve_react():
        """Serveste aplicatia React din build folder."""
        return send_from_directory(app.static_folder, 'index.html')
    
    # Ruta catch-all pentru React Router (SPA)
    @app.route('/<path:path>')
    def serve_react_routes(path):
        """
        Serveste fisierele statice sau index.html pentru rutele React.
        Necesar pentru React Router cu browser history.
        """
        # Verificam daca e un fisier static
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        # Altfel, servim index.html (React va gestiona ruta)
        return send_from_directory(app.static_folder, 'index.html')
    
    # Endpoint pentru verificarea starii serverului
    @app.route('/api/health')
    def health_check():
        """Endpoint pentru health check."""
        return {
            'status': 'healthy',
            'service': 'SecureChat API',
            'version': '1.0.0',
            'encryption': {
                'symmetric': 'AES-256-CBC',
                'asymmetric': 'RSA-2048'
            }
        }
    
    return app


# Cream instanta aplicatiei
app = create_app()


if __name__ == '__main__':
    # Rulam serverul de dezvoltare
    # In productie, folositi un server WSGI precum Gunicorn
    print("=" * 60)
    print("SecureChat - Aplicatie de Chat cu Criptare End-to-End")
    print("=" * 60)
    print("Algoritmi de criptare:")
    print("  - AES-256-CBC: criptare continut mesaje")
    print("  - RSA-2048: schimb securizat de chei")
    print("=" * 60)
    print("Server pornit pe http://localhost:5000")
    print("API disponibil la http://localhost:5000/api")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
