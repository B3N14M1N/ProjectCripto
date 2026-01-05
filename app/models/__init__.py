# models/__init__.py
# Modul pentru modelele bazei de date
# Exporta toate modelele si instanta SQLAlchemy

from flask_sqlalchemy import SQLAlchemy

# Instanta globala SQLAlchemy - va fi initializata in app.py
db = SQLAlchemy()

# Import modele dupa initializarea db pentru a evita dependinte circulare
from .user import User
from .conversation import Conversation, ConversationParticipant
from .message import Message
from .attachment import MessageAttachment

# Exportam toate modelele pentru acces facil
__all__ = ['db', 'User', 'Conversation', 'ConversationParticipant', 'Message', 'MessageAttachment']

