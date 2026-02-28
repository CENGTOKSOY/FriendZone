import json
from datetime import datetime, timezone
from backend.database.db_connection import db
from sqlalchemy.dialects.postgresql import JSONB  # PostgreSQL kullanıyorsan performansı uçurur


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # İçerik ve Tip
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text', index=True)  # Index eklendi

    # Zaman Damgaları (UTC kullanımı düzeltildi)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))

    # İlişkisel Yapı
    reply_to = db.Column(db.Integer, db.ForeignKey('chat_messages.id', ondelete='SET NULL'))

    # Esnek Veri (Reactions ve Metadata)
    # Eğer SQLite kullanıyorsan db.Text kalabilir, ama PostgreSQL ise JSONB kullanmalısın.
    reactions = db.Column(db.JSON, default=dict)
    metadata_json = db.Column(db.JSON, nullable=True)  # Dosya boyutu, resim çözünürlüğü vb. için

    # İlişkiler (Relationships)
    # back_populates kullanımı backref'ten daha moderndir ve debugging kolaylığı sağlar.
    user = db.relationship('User', back_populates='messages')
    community = db.relationship('Community', back_populates='messages')

    # Yanıt mekanizması için self-referential ilişki
    replies = db.relationship('ChatMessage',
                              backref=db.backref('parent', remote_side=[id]),
                              lazy='dynamic')

    def __repr__(self):
        return f"<ChatMessage {self.id} by User {self.user_id}>"

    def add_reaction(self, user_id: int, emoji: str):
        """Tepki ekleme mantığını model seviyesine taşıyoruz."""
        if not self.reactions:
            self.reactions = {}

        # mutable_json_type_support yoksa sözlüğü kopyalayıp güncellemelisin
        current_reactions = dict(self.reactions)
        if emoji not in current_reactions:
            current_reactions[emoji] = []

        if user_id not in current_reactions[emoji]:
            current_reactions[emoji].append(user_id)
            self.reactions = current_reactions
            return True
        return False

    def to_dict(self):
        """API yanıtları için optimize edilmiş dönüşüm."""
        return {
            'id': self.id,
            'sender': {
                'id': self.user_id,
                'username': self.user.username if self.user else "Unknown"
            },
            'community_id': self.community_id,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_edited': self.edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'reply_to': self.reply_to,
            'reactions': self.reactions or {},
            'has_replies': self.replies.count() > 0
        }