# services/chat_service.py
# Serviciu pentru gestionarea conversatiilor si mesajelor
# Integreaza criptarea AES+RSA pentru toate mesajele
#
# Principii SOLID:
# - Single Responsibility: doar logica de chat
# - Dependency Inversion: depinde de CryptoService pentru criptare

from datetime import datetime
from models import db, User, Conversation, ConversationParticipant, Message
from .crypto_service import CryptoService
from .auth_service import AuthService
import json


class ChatService:
    """
    Serviciu pentru gestionarea conversatiilor si mesajelor criptate.
    
    Responsabilitati:
    - Creare si gestionare conversatii
    - Trimitere si primire mesaje criptate
    - Gestionare participanti
    - Marcare mesaje ca citite
    
    Toate mesajele sunt criptate folosind schema hibrida AES+RSA:
    - Continutul e criptat cu AES-256
    - Cheia AES e criptata cu RSA pentru fiecare participant
    """
    
    def __init__(self, crypto_service=None, auth_service=None):
        """
        Initializeaza serviciul de chat.
        
        Args:
            crypto_service: Instanta CryptoService
            auth_service: Instanta AuthService
        """
        self.crypto_service = crypto_service or CryptoService()
        self.auth_service = auth_service or AuthService()
    
    # ==================== GESTIONARE CONVERSATII ====================
    
    def create_conversation(self, creator_id, participant_ids, name=None):
        """
        Creeaza o conversatie noua.
        
        Pentru conversatii 1-la-1, verifica daca exista deja o conversatie
        intre cei doi utilizatori.
        
        Args:
            creator_id: ID-ul utilizatorului care creeaza conversatia
            participant_ids: Lista ID-uri participanti (include creator_id)
            name: Nume optional (pentru grupuri)
            
        Returns:
            dict: {
                'success': bool,
                'conversation': Conversation sau None,
                'error': mesaj eroare sau None,
                'is_existing': bool - daca conversatia exista deja
            }
        """
        # Asiguram ca creatorul e in lista participantilor
        if creator_id not in participant_ids:
            participant_ids = [creator_id] + list(participant_ids)
        
        # Verificam daca toti utilizatorii exista
        users = User.query.filter(User.id.in_(participant_ids)).all()
        if len(users) != len(participant_ids):
            return {'success': False, 'error': 'Unul sau mai multi utilizatori nu exista'}
        
        # Verificam daca toti utilizatorii au chei publice
        for user in users:
            if not user.public_key:
                return {'success': False, 'error': f'Utilizatorul {user.username} nu are cheie publica configurata'}
        
        is_group = len(participant_ids) > 2
        
        # Pentru conversatii 1-la-1, verificam daca exista deja
        if not is_group:
            existing = self._find_existing_conversation(participant_ids)
            if existing:
                return {
                    'success': True,
                    'conversation': existing,
                    'is_existing': True,
                    'message': 'Conversatie existenta gasita'
                }
        
        try:
            # Cream conversatia
            conversation = Conversation(
                name=name if is_group else None,
                is_group=is_group
            )
            db.session.add(conversation)
            db.session.flush()  # Pentru a obtine ID-ul
            
            # Adaugam participantii
            for user_id in participant_ids:
                participant = ConversationParticipant(
                    conversation_id=conversation.id,
                    user_id=user_id
                )
                db.session.add(participant)
            
            db.session.commit()
            
            return {
                'success': True,
                'conversation': conversation,
                'is_existing': False,
                'message': 'Conversatie creata cu succes'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Eroare la crearea conversatiei: {str(e)}'}
    
    def _find_existing_conversation(self, participant_ids):
        """
        Cauta o conversatie existenta intre exact acesti participanti.
        
        Args:
            participant_ids: Lista ID-uri participanti
            
        Returns:
            Conversation sau None
        """
        # Pentru conversatii 1-la-1
        if len(participant_ids) == 2:
            # Gasim conversatiile in care participa primul utilizator
            subq = db.session.query(ConversationParticipant.conversation_id).filter(
                ConversationParticipant.user_id == participant_ids[0]
            ).subquery()
            
            # Verificam daca exista o conversatie non-grup cu ambii participanti
            conversations = Conversation.query.filter(
                Conversation.id.in_(subq),
                Conversation.is_group == False
            ).all()
            
            for conv in conversations:
                conv_participant_ids = set(p.user_id for p in conv.participants)
                if conv_participant_ids == set(participant_ids):
                    return conv
        
        return None
    
    def delete_conversation(self, conversation_id, user_id):
        """
        Sterge o conversatie si toate mesajele/atasamentele asociate.
        
        Args:
            conversation_id: ID conversatie
            user_id: ID utilizator (pentru verificare acces)
            
        Returns:
            dict: {'success': bool, 'error': mesaj eroare sau None}
        """
        from models import MessageAttachment
        
        # Verificam daca utilizatorul are acces la conversatie
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return {'success': False, 'error': 'Conversatie negasita sau acces interzis'}
        
        try:
            # Stergem atasamentele mesajelor din aceasta conversatie
            messages = Message.query.filter_by(conversation_id=conversation_id).all()
            for message in messages:
                MessageAttachment.query.filter_by(message_id=message.id).delete()
            
            # Stergem mesajele
            Message.query.filter_by(conversation_id=conversation_id).delete()
            
            # Stergem participantii
            ConversationParticipant.query.filter_by(conversation_id=conversation_id).delete()
            
            # Stergem conversatia
            db.session.delete(conversation)
            db.session.commit()
            
            return {'success': True}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Eroare la stergere: {str(e)}'}
    
    def get_user_conversations(self, user_id):
        """
        Obtine toate conversatiile unui utilizator, ordonate dupa activitate.
        
        Args:
            user_id: ID utilizator
            
        Returns:
            list: Lista de conversatii cu ultimele mesaje
        """
        # Gasim toate participarile utilizatorului
        participations = ConversationParticipant.query.filter_by(user_id=user_id).all()
        conversation_ids = [p.conversation_id for p in participations]
        
        # Obtinem conversatiile ordonate dupa updated_at (cele mai recente primele)
        conversations = Conversation.query.filter(
            Conversation.id.in_(conversation_ids)
        ).order_by(Conversation.updated_at.desc()).all()
        
        return conversations
    
    def get_conversation(self, conversation_id, user_id):
        """
        Obtine o conversatie specifica, verificand accesul utilizatorului.
        
        Args:
            conversation_id: ID conversatie
            user_id: ID utilizator (pentru verificare acces)
            
        Returns:
            Conversation sau None daca nu exista sau nu are acces
        """
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return None
        
        # Verificam daca utilizatorul e participant
        participant = ConversationParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=user_id
        ).first()
        
        return conversation if participant else None
    
    # ==================== GESTIONARE MESAJE ====================
    
    def send_message(self, conversation_id, sender_id, content, message_type='text', 
                     file_info=None):
        """
        Trimite un mesaj criptat intr-o conversatie.
        
        Procesul de criptare:
        1. Obtine cheile publice ale tuturor participantilor
        2. Genereaza cheie AES aleatorie
        3. Cripteaza continutul cu AES
        4. Cripteaza cheia AES cu RSA pentru fiecare participant
        5. Stocheaza mesajul criptat in baza de date
        
        Args:
            conversation_id: ID conversatie
            sender_id: ID expeditor
            content: Continutul mesajului (va fi criptat)
            message_type: 'text', 'image', sau 'file'
            file_info: Dict cu informatii fisier (optional)
            
        Returns:
            dict: {
                'success': bool,
                'message': Message sau None,
                'error': mesaj eroare sau None
            }
        """
        # Verificam accesul la conversatie
        conversation = self.get_conversation(conversation_id, sender_id)
        if not conversation:
            return {'success': False, 'error': 'Conversatie negasita sau acces interzis'}
        
        # Obtinem cheile publice ale tuturor participantilor
        participant_ids = [p.user_id for p in conversation.participants]
        public_keys = self.auth_service.get_public_keys_for_users(participant_ids)
        
        if len(public_keys) != len(participant_ids):
            return {'success': False, 'error': 'Nu toti participantii au chei publice configurate'}
        
        try:
            # Criptam mesajul pentru toti participantii
            encrypted_data = self.crypto_service.encrypt_message_for_recipients(
                content, public_keys
            )
            
            # Cream mesajul
            message = Message(
                conversation_id=conversation_id,
                sender_id=sender_id,
                encrypted_content=encrypted_data['encrypted_content'],
                encrypted_aes_keys=json.dumps(encrypted_data['encrypted_aes_keys']),
                iv=encrypted_data['iv'],
                message_type=message_type
            )
            
            # Adaugam informatii fisier daca exista
            if file_info and message_type in ['image', 'file']:
                message.file_name = file_info.get('name')
                message.file_path = file_info.get('path')
                message.file_size = file_info.get('size')
                message.file_mime_type = file_info.get('mime_type')
            
            db.session.add(message)
            
            # Actualizam timestamp conversatie
            conversation.update_timestamp()
            
            # Incrementam contorul de necitite pentru ceilalti participanti
            for participant in conversation.participants:
                if participant.user_id != sender_id:
                    participant.increment_unread()
            
            db.session.commit()
            
            return {
                'success': True,
                'message': message,
                'crypto_details': {
                    'algorithm_content': 'AES-256-CBC',
                    'algorithm_key_exchange': 'RSA-2048',
                    'recipients_count': len(participant_ids)
                }
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Eroare la trimiterea mesajului: {str(e)}'}
    
    def get_messages(self, conversation_id, user_id, limit=50, before_id=None):
        """
        Obtine mesajele dintr-o conversatie.
        
        Mesajele sunt returnate criptate - decriptarea se face pe client.
        
        Args:
            conversation_id: ID conversatie
            user_id: ID utilizator (pentru verificare acces)
            limit: Numar maxim de mesaje
            before_id: Pentru paginare - mesaje inainte de acest ID
            
        Returns:
            list: Lista de mesaje (criptate)
        """
        # Verificam accesul
        conversation = self.get_conversation(conversation_id, user_id)
        if not conversation:
            return []
        
        # Construim query-ul
        query = Message.query.filter_by(conversation_id=conversation_id)
        
        if before_id:
            query = query.filter(Message.id < before_id)
        
        # Ordonam descrescator si luam ultimele N mesaje
        messages = query.order_by(Message.created_at.desc()).limit(limit).all()
        
        # Returnam in ordine cronologica
        return list(reversed(messages))
    
    def mark_conversation_as_read(self, conversation_id, user_id):
        """
        Marcheaza toate mesajele dintr-o conversatie ca citite.
        
        Args:
            conversation_id: ID conversatie
            user_id: ID utilizator
            
        Returns:
            dict: Rezultat operatie
        """
        participant = ConversationParticipant.query.filter_by(
            conversation_id=conversation_id,
            user_id=user_id
        ).first()
        
        if not participant:
            return {'success': False, 'error': 'Nu esti participant in aceasta conversatie'}
        
        try:
            participant.mark_as_read()
            db.session.commit()
            return {'success': True}
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    # ==================== DECRIPTARE MESAJE ====================
    
    def decrypt_message(self, message_id, user_id, private_key_pem):
        """
        Decripteaza un mesaj pentru un utilizator specific.
        
        NOTA: In practica, decriptarea se face pe client pentru securitate maxima.
        Aceasta metoda este pentru demonstratie sau cazuri speciale.
        
        Args:
            message_id: ID mesaj
            user_id: ID utilizator
            private_key_pem: Cheia privata RSA a utilizatorului
            
        Returns:
            dict: {
                'success': bool,
                'content': continut decriptat sau None,
                'error': mesaj eroare sau None
            }
        """
        message = Message.query.get(message_id)
        if not message:
            return {'success': False, 'error': 'Mesaj negasit'}
        
        # Verificam accesul la conversatie
        participant = ConversationParticipant.query.filter_by(
            conversation_id=message.conversation_id,
            user_id=user_id
        ).first()
        
        if not participant:
            return {'success': False, 'error': 'Nu ai acces la acest mesaj'}
        
        # Obtinem cheia AES criptata pentru acest utilizator
        encrypted_aes_key = message.get_encrypted_key_for_user(user_id)
        if not encrypted_aes_key:
            return {'success': False, 'error': 'Nu exista cheie criptata pentru tine'}
        
        try:
            # Decriptam mesajul
            decrypted_content = self.crypto_service.decrypt_message(
                message.encrypted_content,
                encrypted_aes_key,
                message.iv,
                private_key_pem
            )
            
            return {
                'success': True,
                'content': decrypted_content,
                'message_type': message.message_type,
                'file_info': {
                    'name': message.file_name,
                    'size': message.file_size,
                    'mime_type': message.file_mime_type
                } if message.message_type != 'text' else None
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Eroare la decriptare: {str(e)}'}
    
    # ==================== STATISTICI SI INFO ====================
    
    def get_unread_count(self, user_id):
        """
        Obtine numarul total de mesaje necitite pentru un utilizator.
        
        Args:
            user_id: ID utilizator
            
        Returns:
            int: Numar mesaje necitite
        """
        participations = ConversationParticipant.query.filter_by(user_id=user_id).all()
        return sum(p.unread_count for p in participations)
    
    def get_conversation_crypto_info(self, conversation_id):
        """
        Obtine informatii despre criptarea folosita in conversatie.
        Util pentru afisarea in UI a detaliilor de securitate.
        
        Args:
            conversation_id: ID conversatie
            
        Returns:
            dict: Informatii despre criptare
        """
        conversation = Conversation.query.get(conversation_id)
        if not conversation:
            return None
        
        participants = [p.user for p in conversation.participants]
        
        return {
            'participants_count': len(participants),
            'participants': [
                {
                    'username': p.username,
                    'has_public_key': bool(p.public_key)
                } for p in participants
            ],
            'encryption_info': self.crypto_service.get_encryption_info(),
            'security_note_ro': (
                'Fiecare mesaj este criptat cu o cheie AES unica. '
                'Cheia AES este criptata individual cu cheia publica RSA '
                'a fiecarui participant, asigurand ca doar destinatarii '
                'pot decripta mesajele.'
            )
        }
