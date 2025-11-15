from flask import Blueprint, request, jsonify
from backend.database.db_connection import db
from backend.models.user_model import User
from backend.models.community_model import Community, CommunityMember
from backend.models.chat_model import ChatMessage
from datetime import datetime
import json

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/api/chat/<int:community_id>/messages', methods=['GET'])
def get_chat_messages(community_id):
    """Topluluk sohbet mesajlarını getir"""
    try:
        # Sayfalama parametreleri
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = (page - 1) * limit

        # Mesajları getir (en yeni en üstte)
        messages = ChatMessage.query.filter_by(community_id=community_id) \
            .order_by(ChatMessage.timestamp.desc()) \
            .offset(offset) \
            .limit(limit) \
            .all()

        # Mesajları formatla
        messages_data = []
        for message in messages:
            user = User.query.get(message.user_id)
            messages_data.append({
                'id': message.id,
                'user_id': message.user_id,
                'user_name': user.name if user else 'Silinmiş Kullanıcı',
                'user_avatar': user.avatar if user else None,
                'content': message.content,
                'message_type': message.message_type,
                'timestamp': message.timestamp.isoformat(),
                'reactions': json.loads(message.reactions) if message.reactions else [],
                'reply_to': message.reply_to
            })

        return jsonify({
            'success': True,
            'messages': messages_data[::-1],  # Eski mesajlar üstte olacak şekilde ters çevir
            'has_more': len(messages) == limit
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Sohbet mesajları yüklenemedi: {str(e)}'
        }), 500


@chat_bp.route('/api/chat/<int:community_id>/send', methods=['POST'])
def send_message(community_id):
    """Yeni mesaj gönder"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        content = data.get('content')
        message_type = data.get('message_type', 'text')
        reply_to = data.get('reply_to')

        # Kullanıcı toplulukta mı kontrol et
        membership = CommunityMember.query.filter_by(
            community_id=community_id,
            user_id=user_id
        ).first()

        if not membership:
            return jsonify({
                'success': False,
                'message': 'Bu toplulukta mesaj gönderme yetkiniz yok'
            }), 403

        # Yeni mesaj oluştur
        new_message = ChatMessage(
            community_id=community_id,
            user_id=user_id,
            content=content,
            message_type=message_type,
            reply_to=reply_to,
            timestamp=datetime.utcnow()
        )

        db.session.add(new_message)
        db.session.commit()

        # Mesaj verisini hazırla
        user = User.query.get(user_id)
        message_data = {
            'id': new_message.id,
            'user_id': user_id,
            'user_name': user.name,
            'user_avatar': user.avatar,
            'content': content,
            'message_type': message_type,
            'timestamp': new_message.timestamp.isoformat(),
            'reactions': [],
            'reply_to': reply_to
        }

        return jsonify({
            'success': True,
            'message': message_data
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Mesaj gönderilemedi: {str(e)}'
        }), 500


@chat_bp.route('/api/chat/message/<int:message_id>/react', methods=['POST'])
def react_to_message(message_id):
    """Mesaja tepki ekle/kaldır"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        emoji = data.get('emoji')

        message = ChatMessage.query.get(message_id)
        if not message:
            return jsonify({
                'success': False,
                'message': 'Mesaj bulunamadı'
            }), 404

        # Mevcut tepkileri yükle
        reactions = json.loads(message.reactions) if message.reactions else []

        # Kullanıcının bu emoji için tepkisini kontrol et
        user_reaction = next((r for r in reactions if r['user_id'] == user_id and r['emoji'] == emoji), None)

        if user_reaction:
            # Tepkiyi kaldır
            reactions.remove(user_reaction)
        else:
            # Tepki ekle
            reactions.append({
                'user_id': user_id,
                'emoji': emoji,
                'timestamp': datetime.utcnow().isoformat()
            })

        # Tepkileri güncelle
        message.reactions = json.dumps(reactions)
        db.session.commit()

        return jsonify({
            'success': True,
            'reactions': reactions
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Tepki eklenemedi: {str(e)}'
        }), 500


@chat_bp.route('/api/chat/<int:community_id>/typing', methods=['POST'])
def user_typing(community_id):
    """Kullanıcı yazıyor durumunu güncelle"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        is_typing = data.get('is_typing', False)

        # Burada WebSocket veya başka bir real-time sistem kullanılabilir
        # Şimdilik basit bir yapı kullanıyoruz

        return jsonify({
            'success': True,
            'typing': is_typing,
            'user_id': user_id
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Yazma durumu güncellenemedi: {str(e)}'
        }), 500