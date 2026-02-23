class TestHandler {
    constructor() {
        this.currentQuestion = 0;
        this.answers = {};
        this.questions = [];
        this.init();
    }

    async init() {
        await this.loadQuestions();
        this.setupEventListeners();
        this.showQuestion(0);
        this.updateProgress();
        this.loadUserData();
    }

    async loadQuestions() {
        try {
            const response = await fetch('/api/test/personality-questions');
            const data = await response.json();

            if (data.success) {
                this.questions = data.questions;
                this.updateQuestionCount();
            } else {
                throw new Error('Sorular yüklenemedi');
            }
        } catch (error) {
            console.error('Soru yükleme hatası:', error);
            this.showFallbackQuestions();
        }
    }

    showFallbackQuestions() {
        this.questions = [
            {
                id: 1,
                question: "Sosyal ortamlarda nasıl hissedersiniz?",
                type: "social",
                options: [
                    {
                        value: "introvert",
                        text: "Sessiz ve gözlemci",
                        description: "Küçük grupları tercih eder, dinlemeyi sever"
                    },
                    {
                        value: "extrovert",
                        text: "Enerjik ve konuşkan",
                        description: "Kalabalık ortamlarda enerji kazanır"
                    },
                    {
                        value: "ambivert",
                        text: "Duruma göre değişir",
                        description: "Ortama ve ruh haline göre davranır"
                    }
                ]
            },

            

            // Diğer sorular...
        ];
        this.updateQuestionCount();
    }

    updateQuestionCount() {
        document.getElementById('totalQuestions').textContent = this.questions.length;
    }

    setupEventListeners() {
        document.getElementById('prevBtn').addEventListener('click', () => this.previousQuestion());
        document.getElementById('nextBtn').addEventListener('click', () => this.nextQuestion());
        document.getElementById('submitBtn').addEventListener('click', () => this.submitTest());
    }

    showQuestion(index) {
        if (index < 0 || index >= this.questions.length) return;

        this.currentQuestion = index;
        const question = this.questions[index];

        const questionHTML = `
            <div class="question-card">
                <div class="question-number">Soru ${index + 1}</div>
                <h2 class="question-text">${question.question}</h2>
                <div class="options-grid">
                    ${question.options.map((option, optIndex) => `
                        <div class="option-card ${this.answers[index] === option.value ? 'selected' : ''}" 
                             data-value="${option.value}">
                            <div class="option-content">
                                <div class="option-icon">
                                    <i class="fas fa-${this.getOptionIcon(optIndex)}"></i>
                                </div>
                                <div class="option-text">
                                    <div class="option-title">${option.text}</div>
                                    <div class="option-description">${option.description}</div>
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        document.getElementById('questionContainer').innerHTML = questionHTML;

        // Option selection
        document.querySelectorAll('.option-card').forEach(card => {
            card.addEventListener('click', () => this.selectOption(card.dataset.value));
        });

        this.updateNavigation();
        this.updateProgress();
    }

    getOptionIcon(index) {
        const icons = ['user-friends', 'comments', 'balance-scale', 'star', 'heart'];
        return icons[index] || 'circle';
    }

    selectOption(value) {
        this.answers[this.currentQuestion] = value;

        // Update UI
        document.querySelectorAll('.option-card').forEach(card => {
            card.classList.remove('selected');
        });

        document.querySelector(`.option-card[data-value="${value}"]`).classList.add('selected');

        // Enable next button
        document.getElementById('nextBtn').disabled = false;
    }

    previousQuestion() {
        if (this.currentQuestion > 0) {
            this.showQuestion(this.currentQuestion - 1);
        }
    }

    nextQuestion() {
        if (this.currentQuestion < this.questions.length - 1) {
            this.showQuestion(this.currentQuestion + 1);
        }
    }

    updateNavigation() {
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const submitBtn = document.getElementById('submitBtn');

        prevBtn.disabled = this.currentQuestion === 0;

        if (this.currentQuestion === this.questions.length - 1) {
            nextBtn.style.display = 'none';
            submitBtn.style.display = 'flex';
        } else {
            nextBtn.style.display = 'flex';
            submitBtn.style.display = 'none';
        }

        // Disable next if no answer selected
        nextBtn.disabled = !this.answers[this.currentQuestion];
    }

    updateProgress() {
        const progress = ((this.currentQuestion + 1) / this.questions.length) * 100;
        document.getElementById('progressFill').style.width = `${progress}%`;
        document.getElementById('currentQuestion').textContent = this.currentQuestion + 1;
    }

    async submitTest() {
        if (Object.keys(this.answers).length !== this.questions.length) {
            alert('Lütfen tüm soruları cevaplayın');
            return;
        }

        const submitBtn = document.getElementById('submitBtn');
        this.setLoadingState(submitBtn, true);

        try {
            const user = JSON.parse(localStorage.getItem('friendzone_user'));
            const response = await fetch('/api/test/submit-personality', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('friendzone_token')}`
                },
                body: JSON.stringify({
                    user_id: user.id,
                    answers: this.formatAnswers()
                })
            });

            const result = await response.json();

            if (response.ok) {
                this.showResults(result.data);
            } else {
                throw new Error(result.message || 'Test gönderilemedi');
            }

        } catch (error) {
            console.error('Test gönderme hatası:', error);
            alert('Test gönderilirken bir hata oluştu: ' + error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    formatAnswers() {
        return this.questions.map((question, index) => ({
            question_id: question.id,
            type: question.type,
            value: this.answers[index],
            score: question.options.find(opt => opt.value === this.answers[index])?.score || 1
        }));
    }

    showResults(data) {
        const resultsHTML = `
            <div class="results-container">
                <div class="personality-result">
                    <div class="result-icon">
                        <i class="fas fa-award"></i>
                    </div>
                    <h1 class="result-title">${data.personality_type}</h1>
                    <p class="result-description">
                        Kişilik testini başarıyla tamamladın! 
                        Seninle en uyumlu toplulukları bulmak için hobilerini seçmeye hazır mısın?
                    </p>
                    
                    <div class="traits-grid">
                        ${Object.entries(data.scores).map(([category, traits]) => `
                            <div class="trait-card">
                                <div class="trait-name">${this.formatCategory(category)}</div>
                                <div class="trait-value">${this.getDominantTrait(traits)}</div>
                            </div>
                        `).join('')}
                    </div>
                    
                    <div class="test-navigation">
                        <a href="hobbies.html" class="btn btn-primary btn-large">
                            <i class="fas fa-arrow-right"></i>
                            Hobi Testine Geç
                        </a>
                    </div>
                </div>
            </div>
        `;

        document.querySelector('.test-content').innerHTML = resultsHTML;
    }

    formatCategory(category) {
        const categories = {
            'social': 'Sosyal',
            'problem_solving': 'Problem Çözme',
            'planning': 'Planlama',
            'team_role': 'Takım Rolü',
            'social_interaction': 'Sosyal Etkileşim'
        };
        return categories[category] || category;
    }

    getDominantTrait(traits) {
        return Object.entries(traits).reduce((a, b) => a[1] > b[1] ? a : b)[0];
    }

    setLoadingState(button, isLoading) {
        if (isLoading) {
            button.classList.add('btn-loading');
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> İşleniyor...';
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-paper-plane"></i> Testi Tamamla';
        }
    }

    loadUserData() {
        const user = JSON.parse(localStorage.getItem('friendzone_user'));
        if (user) {
            document.getElementById('userName').textContent = user.name;
            document.getElementById('userAvatar').textContent = user.name.charAt(0).toUpperCase();
        }
    }
}

// Initialize test handler
document.addEventListener('DOMContentLoaded', () => {
    window.testHandler = new TestHandler();
});