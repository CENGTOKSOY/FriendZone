class ChatHandler {
    constructor(communityId) {
        this.communityId = communityId;
        this.messages = [];
        this.currentUser = null;
        this.replyTo = null;
        this.isTyping = false;
        this.typingUsers = new Set();
        this.init();
    }

    async init() {
        await this.loadUserData();
        await this.loadMessages();
        this.setupEventListeners();
        this.startPolling();
        this.loadCommunityMembers();
    }

    async loadUserData() {
        try {
            const userData = localStorage.getItem('friendzone_user');
            if (userData) {
                this.currentUser = JSON.parse(userData);
            }
        } catch (error) {
            console.error('Kullanıcı verisi yüklenemedi:', error);
        }
    }

    async loadMessages() {
        try {
            const response = await fetch(`/api/chat/${this.communityId}/messages`);
            const data = await response.json();

            if (data.success) {
                this.messages = data.messages;
                this.renderMessages();
                this.scrollToBottom();
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Mesajlar yüklenemedi:', error);
            this.showError('Mesajlar yüklenemedi');
        }
    }

    async loadCommunityMembers() {
        try {
            // Topluluk üyelerini yükle
            const response = await fetch(`/api/community/${this.communityId}/members`);
            const data = await response.json();

            if (data.success) {
                this.renderMembers(data.members);
            }
        } catch (error) {
            console.error('Üyeler yüklenemedi:', error);
        }
    }

    setupEventListeners() {
        // Mesaj gönderme
        const sendBtn = document.getElementById('sendMessageBtn');
        const messageInput = document.getElementById('messageInput');

        sendBtn.addEventListener('click', () => this.sendMessage());
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Yazma durumu
        messageInput.addEventListener('input', () => {
            this.handleTyping();
        });

        // Dosya yükleme
        const fileInput = document.getElementById('fileInput');
        fileInput.addEventListener('change', (e) => {
            this.handleFileUpload(e.target.files[0]);
        });

        // Emoji seçimi
        const emojiBtn = document.getElementById('emojiBtn');
        emojiBtn.addEventListener('click', () => {
            this.toggleEmojiPicker();
        });

        // Yanıtı iptal etme
        const cancelReplyBtn = document.getElementById('cancelReplyBtn');
        if (cancelReplyBtn) {
            cancelReplyBtn.addEventListener('click', () => {
                this.cancelReply();
            });
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const content = messageInput.value.trim();

        if (!content || !this.currentUser) return;

        try {
            const messageData = {
                user_id: this.currentUser.id,
                content: content,
                message_type: 'text'
            };

            if (this.replyTo) {
                messageData.reply_to = this.replyTo;
            }

            const response = await fetch(`/api/chat/${this.communityId}/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify(messageData)
            });

            const data = await response.json();

            if (data.success) {
                // Mesajı listeye ekle
                this.messages.push(data.message);
                this.renderMessages();
                this.scrollToBottom();

                // Input'u temizle
                messageInput.value = '';
                this.cancelReply();

                // Yazma durumunu sıfırla
                this.stopTyping();

                // GPT asistanını tetikle (belirli koşullarda)
                this.maybeTriggerAssistant(content);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Mesaj gönderilemedi:', error);
            this.showError('Mesaj gönderilemedi');
        }
    }

    async handleFileUpload(file) {
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('user_id', this.currentUser.id);

            const response = await fetch(`/api/chat/${this.communityId}/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.messages.push(data.message);
                this.renderMessages();
                this.scrollToBottom();
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Dosya yüklenemedi:', error);
            this.showError('Dosya yüklenemedi');
        }
    }

    async reactToMessage(messageId, emoji) {
        try {
            const response = await fetch(`/api/chat/message/${messageId}/react`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    user_id: this.currentUser.id,
                    emoji: emoji
                })
            });

            const data = await response.json();

            if (data.success) {
                // Mesajı güncelle
                const messageIndex = this.messages.findIndex(m => m.id === messageId);
                if (messageIndex !== -1) {
                    this.messages[messageIndex].reactions = data.reactions;
                    this.renderMessages();
                }
            }
        } catch (error) {
            console.error('Tepki eklenemedi:', error);
        }
    }

    handleTyping() {
        if (!this.isTyping) {
            this.isTyping = true;
            this.sendTypingStatus(true);

            // 3 saniye sonra yazma durumunu durdur
            this.typingTimeout = setTimeout(() => {
                this.stopTyping();
            }, 3000);
        } else {
            clearTimeout(this.typingTimeout);
            this.typingTimeout = setTimeout(() => {
                this.stopTyping();
            }, 3000);
        }
    }

    async sendTypingStatus(isTyping) {
        try {
            await fetch(`/api/chat/${this.communityId}/typing`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    user_id: this.currentUser.id,
                    is_typing: isTyping
                })
            });
        } catch (error) {
            console.error('Yazma durumu gönderilemedi:', error);
        }
    }

    stopTyping() {
        this.isTyping = false;
        this.sendTypingStatus(false);
        if (this.typingTimeout) {
            clearTimeout(this.typingTimeout);
        }
    }

    replyToMessage(message) {
        this.replyTo = message.id;
        this.showReplyPreview(message);
    }

    cancelReply() {
        this.replyTo = null;
        this.hideReplyPreview();
    }

    showReplyPreview(message) {
        const replyPreview = document.getElementById('replyPreview');
        const replyContent = document.getElementById('replyContent');

        replyContent.innerHTML = `
            <div class="reply-author">${message.user_name}</div>
            <div class="reply-content">${this.formatMessageContent(message.content)}</div>
        `;

        replyPreview.style.display = 'block';
    }

    hideReplyPreview() {
        const replyPreview = document.getElementById('replyPreview');
        replyPreview.style.display = 'none';
    }

    renderMessages() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.innerHTML = '';

        this.messages.forEach(message => {
            const messageElement = this.createMessageElement(message);
            messagesContainer.appendChild(messageElement);
        });
    }

    createMessageElement(message) {
        const messageGroup = document.createElement('div');
        messageGroup.className = 'message-group';
        messageGroup.dataset.messageId = message.id;

        const isCurrentUser = message.user_id === this.currentUser?.id;

        messageGroup.innerHTML = `
            <div class="message-avatar">
                ${message.user_name?.charAt(0).toUpperCase() || '?'}
            </div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-author">${message.user_name}</span>
                    <span class="message-time">${this.formatTime(message.timestamp)}</span>
                </div>
                ${message.reply_to ? this.createReplyPreview(message.reply_to) : ''}
                <div class="message-text">${this.formatMessageContent(message.content)}</div>
                ${message.reactions?.length > 0 ? this.createReactions(message.reactions, message.id) : ''}
                <div class="message-actions">
                    <button class="message-action" onclick="chatHandler.replyToMessage(${JSON.stringify(message).replace(/"/g, '&quot;')})">
                        <i class="fas fa-reply"></i>
                    </button>
                    <button class="message-action" onclick="chatHandler.reactToMessage(${message.id}, '👍')">
                        <i class="fas fa-thumbs-up"></i>
                    </button>
                    <button class="message-action" onclick="chatHandler.reactToMessage(${message.id}, '❤️')">
                        <i class="fas fa-heart"></i>
                    </button>
                </div>
            </div>
        `;

        return messageGroup;
    }

    createReplyPreview(replyToId) {
        const repliedMessage = this.messages.find(m => m.id === replyToId);
        if (!repliedMessage) return '';

        return `
            <div class="message-reply" onclick="chatHandler.scrollToMessage(${replyToId})">
                <div class="reply-author">${repliedMessage.user_name}</div>
                <div class="reply-content">${this.formatMessageContent(repliedMessage.content)}</div>
            </div>
        `;
    }

    createReactions(reactions, messageId) {
        const reactionCounts = {};
        const userReactions = new Set();

        reactions.forEach(reaction => {
            if (!reactionCounts[reaction.emoji]) {
                reactionCounts[reaction.emoji] = 0;
            }
            reactionCounts[reaction.emoji]++;

            if (reaction.user_id === this.currentUser?.id) {
                userReactions.add(reaction.emoji);
            }
        });

        const reactionElements = Object.entries(reactionCounts).map(([emoji, count]) => {
            const isActive = userReactions.has(emoji);
            return `
                <div class="reaction ${isActive ? 'active' : ''}" 
                     onclick="chatHandler.reactToMessage(${messageId}, '${emoji}')">
                    <span class="reaction-emoji">${emoji}</span>
                    <span class="reaction-count">${count}</span>
                </div>
            `;
        });

        return `<div class="message-reactions">${reactionElements.join('')}</div>`;
    }

    renderMembers(members) {
        const membersList = document.getElementById('membersList');
        membersList.innerHTML = '';

        members.forEach(member => {
            const memberElement = document.createElement('div');
            memberElement.className = 'member-item';
            memberElement.innerHTML = `
                <div class="member-avatar">
                    ${member.name.charAt(0).toUpperCase()}
                    <div class="status-indicator ${member.status || 'online'}"></div>
                </div>
                <div class="member-info">
                    <div class="member-name">${member.name}</div>
                    <div class="member-role">
                        ${member.role === 'admin' ? '<span class="role-badge">Admin</span>' : 'Üye'}
                    </div>
                </div>
            `;
            membersList.appendChild(memberElement);
        });
    }

    formatMessageContent(content) {
        // Basit markdown ve link formatlama
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>')
            .replace(/\n/g, '<br>');
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);

        if (diffMins < 1) return 'şimdi';
        if (diffMins < 60) return `${diffMins} dk önce`;
        if (diffHours < 24) return `${diffHours} sa önce`;

        return date.toLocaleDateString('tr-TR', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatMessages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    scrollToMessage(messageId) {
        const messageElement = document.querySelector(`[data-message-id="${messageId}"]`);
        if (messageElement) {
            messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            messageElement.style.background = 'var(--bg-accent)';
            setTimeout(() => {
                messageElement.style.background = '';
            }, 2000);
        }
    }

    startPolling() {
        // Yeni mesajları kontrol et
        setInterval(async () => {
            await this.checkNewMessages();
            await this.updateTypingIndicator();
        }, 3000);
    }

    async checkNewMessages() {
        try {
            const response = await fetch(`/api/chat/${this.communityId}/messages?limit=1`);
            const data = await response.json();

            if (data.success && data.messages.length > 0) {
                const latestMessage = data.messages[0];
                const hasNewMessage = !this.messages.some(m => m.id === latestMessage.id);

                if (hasNewMessage) {
                    await this.loadMessages();
                }
            }
        } catch (error) {
            console.error('Yeni mesajlar kontrol edilemedi:', error);
        }
    }

    async updateTypingIndicator() {
        // Yazma durumunu güncelle (gerçek uygulamada WebSocket kullanılır)
        const typingIndicator = document.getElementById('typingIndicator');
        if (this.typingUsers.size > 0) {
            const users = Array.from(this.typingUsers).slice(0, 3);
            const names = users.map(userId => {
                const user = this.getUserById(userId);
                return user ? user.name : 'Birisi';
            });

            typingIndicator.textContent = `${names.join(', ')} yazıyor...`;
            typingIndicator.style.display = 'block';
        } else {
            typingIndicator.style.display = 'none';
        }
    }

    getUserById(userId) {
        // Kullanıcıyı ID'ye göre bul (gerçek uygulamada üye listesinden)
        return null;
    }

    maybeTriggerAssistant(content) {
        // GPT asistanını tetikleme koşulları
        const triggerWords = ['yardım', 'öneri', 'fikir', 'ne yapalım', 'sıkıldım', 'yeni'];
        const shouldTrigger = triggerWords.some(word =>
            content.toLowerCase().includes(word)
        );

        if (shouldTrigger) {
            setTimeout(() => {
                this.triggerAssistantSuggestion();
            }, 2000);
        }
    }

    async triggerAssistantSuggestion() {
        try {
            const response = await fetch('/api/assistant/suggest', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    community_id: this.communityId,
                    context: 'sohbet_devam'
                })
            });

            const data = await response.json();

            if (data.success && data.suggestion) {
                // GPT önerisini sohbete ekle
                this.addAssistantMessage(data.suggestion);
            }
        } catch (error) {
            console.error('GPT önerisi alınamadı:', error);
        }
    }

    addAssistantMessage(content) {
        const assistantMessage = {
            id: Date.now(),
            user_id: 0, // GPT asistanı ID'si
            user_name: 'FriendZone Asistanı 🤖',
            content: content,
            message_type: 'system',
            timestamp: new Date().toISOString(),
            reactions: []
        };

        this.messages.push(assistantMessage);
        this.renderMessages();
        this.scrollToBottom();
    }

    showError(message) {
        // Hata mesajı göster
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        errorDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f56565;
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            z-index: 1000;
        `;

        document.body.appendChild(errorDiv);
        setTimeout(() => {
            errorDiv.remove();
        }, 3000);
    }

    toggleEmojiPicker() {
        // Emoji picker implementasyonu
        console.log('Emoji picker aç/kapat');
    }
}

// Global chat handler instance
let chatHandler = null;

// Sayfa yüklendiğinde chat handler'ı başlat
document.addEventListener('DOMContentLoaded', function() {
    const communityId = getCommunityIdFromURL(); // URL'den topluluk ID'sini al
    chatHandler = new ChatHandler(communityId);
});

function getCommunityIdFromURL() {
    // URL'den topluluk ID'sini çıkar
    const urlParams = new URLSearchParams(window.location.search);
    return parseInt(urlParams.get('id')) || 1; // Varsayılan değer
}