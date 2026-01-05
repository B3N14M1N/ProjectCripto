# routes/__init__.py
# Modul pentru rutele API
# Separa endpoint-urile in module logice (SOLID - Single Responsibility)

from .auth_routes import auth_bp
from .chat_routes import chat_bp
from .file_routes import file_bp

__all__ = ['auth_bp', 'chat_bp', 'file_bp']
