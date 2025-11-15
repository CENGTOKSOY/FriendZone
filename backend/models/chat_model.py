from backend.database.db_connection import db
from datetime import datetime


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')  # text, image, file, system
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)
    reply_to = db.Column(db.Integer, db.ForeignKey('chat_messages.id'))  # Yanıtlanan mesaj ID
    reactions = db.Column(db.Text)  # JSON formatında tepkiler

    # İlişkiler
    community = db.relationship('Community', backref=db.backref('messages', lazy=True))
    user = db.relationship('User', backref=db.backref('messages', lazy=True))
    parent_message = db.relationship('ChatMessage', remote_side=[id],
                                     backref=db.backref('replies', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'community_id': self.community_id,
            'user_id': self.user_id,
            'content': self.content,
            'message_type': self.message_type,
            'timestamp': self.timestamp.isoformat(),
            'edited': self.edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'reply_to': self.reply_to,
            'reactions': self.reactions
        }