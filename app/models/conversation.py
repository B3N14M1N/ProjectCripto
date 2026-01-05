# models/conversation.py
# Model pentru conversatii si participanti
# Suporta conversatii intre doi sau mai multi utilizatori

from datetime import datetime
from . import db


class Conversation(db.Model):
    """
    Model pentru conversatii.
    
    O conversatie este un container pentru mesaje intre doi sau mai multi utilizatori.
    Poate fi conversatie privata (2 persoane) sau grup.
    
    Atribute:
        id: Identificator unic al conversatiei
        name: Nume optional pentru grupuri
        is_group: Flag pentru conversatie de grup
        created_at: Data crearii conversatiei
        updated_at: Data ultimei actualizari (ultim mesaj)
    """
    
    __tablename__ = 'conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)  # Nume pentru grupuri
    is_group = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relatii
    participants = db.relationship('ConversationParticipant', backref='conversation', 
                                   lazy='dynamic', cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='conversation', lazy='dynamic',
                               cascade='all, delete-orphan', order_by='Message.created_at')
    
    def get_other_participant(self, user_id):
        """
        Pentru conversatii 1-la-1, obtine celalalt participant.
        
        Args:
            user_id: ID-ul utilizatorului curent
            
        Returns:
            User: Celalalt participant sau None
        """
        for participant in self.participants:
            if participant.user_id != user_id:
                return participant.user
        return None
    
    def get_last_message(self):
        """
        Obtine ultimul mesaj din conversatie.
        
        Returns:
            Message: Ultimul mesaj sau None
        """
        return self.messages.order_by(db.desc('created_at')).first()
    
    def update_timestamp(self):
        """
        Actualizeaza timestamp-ul conversatiei.
        Apelat la fiecare mesaj nou.
        """
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, current_user_id=None):
        """
        Converteste conversatia la dictionar pentru raspuns JSON.
        
        Args:
            current_user_id: ID utilizator curent pentru context
            
        Returns:
            dict: Reprezentarea JSON a conversatiei
        """
        # Pentru conversatii 1-la-1, afisam numele celuilalt participant
        display_name = self.name
        other_user = None
        
        if not self.is_group and current_user_id:
            other_user = self.get_other_participant(current_user_id)
            if other_user:
                display_name = other_user.username
        
        # Obtinem numarul de mesaje necitite pentru utilizatorul curent
        unread_count = 0
        if current_user_id:
            participant = self.participants.filter_by(user_id=current_user_id).first()
            if participant:
                unread_count = participant.unread_count
        
        last_message = self.get_last_message()
        
        return {
            'id': self.id,
            'name': display_name,
            'is_group': self.is_group,
            'unread_count': unread_count,
            'other_user': other_user.to_dict() if other_user else None,
            'last_message': {
                'preview': '...',  # Nu afisam continutul criptat
                'created_at': last_message.created_at.isoformat() if last_message else None,
                'sender_id': last_message.sender_id if last_message else None
            } if last_message else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'participants': [p.user.to_dict() for p in self.participants]
        }
    
    def __repr__(self):
        return f'<Conversation {self.id}>'


class ConversationParticipant(db.Model):
    """
    Model pentru participantii unei conversatii.
    
    Leaga utilizatorii de conversatii si stocheaza informatii
    specifice participarii (ex: mesaje necitite).
    
    Atribute:
        id: Identificator unic
        conversation_id: Referinta la conversatie
        user_id: Referinta la utilizator
        joined_at: Data aderarii la conversatie
        unread_count: Numarul de mesaje necitite
        last_read_at: Timestamp-ul ultimei citiri
    """
    
    __tablename__ = 'conversation_participants'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    unread_count = db.Column(db.Integer, default=0)
    last_read_at = db.Column(db.DateTime, nullable=True)
    
    # Index compus pentru cautari rapide
    __table_args__ = (
        db.UniqueConstraint('conversation_id', 'user_id', name='unique_participant'),
    )
    
    def mark_as_read(self):
        """
        Marcheaza toate mesajele ca citite pentru acest participant.
        """
        self.unread_count = 0
        self.last_read_at = datetime.utcnow()
    
    def increment_unread(self):
        """
        Incrementeaza contorul de mesaje necitite.
        Apelat cand se primeste un mesaj nou.
        """
        self.unread_count += 1
    
    def __repr__(self):
        return f'<ConversationParticipant user={self.user_id} conv={self.conversation_id}>'
