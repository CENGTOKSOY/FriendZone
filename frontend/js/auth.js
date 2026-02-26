class AuthManager {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkExistingAuth();
    }

    setupEventListeners() {
        // Password toggle
        const passwordToggle = document.getElementById('passwordToggle');
        if (passwordToggle) {
            passwordToggle.addEventListener('click', this.togglePasswordVisibility.bind(this));
        }

        // Form submission
        const loginForm = document.getElementById('loginForm');
        const signupForm = document.getElementById('signupForm');

        if (loginForm) {
            loginForm.addEventListener('submit', this.handleLogin.bind(this));
        }

        if (signupForm) {
            signupForm.addEventListener('submit', this.handleSignup.bind(this));
        }

        // Real-time validation
        this.setupRealTimeValidation();
    }

    togglePasswordVisibility() {
        const passwordInput = document.getElementById('password');
        const toggleIcon = document.querySelector('#passwordToggle i');

        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            toggleIcon.className = 'fas fa-eye-slash';
        } else {
            passwordInput.type = 'password';
            toggleIcon.className = 'fas fa-eye';
        }
    }

    async handleLogin(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const data = {
            email: formData.get('email'),
            password: formData.get('password')
        };

        // Validation
        if (!this.validateLoginData(data)) {
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoadingState(submitBtn, true);

        try {
            // Demo giriş simülasyonu
            await this.simulateLogin(data.email, data.password);

            this.showSuccess('Başarıyla giriş yapıldı! Yönlendiriliyorsunuz...');

            setTimeout(() => {
                window.location.href = 'communities.html';
            }, 1500);

        } catch (error) {
            this.showError(error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    async handleSignup(e) {
        e.preventDefault();

        const formData = new FormData(e.target);
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            password: formData.get('password'),
            university: formData.get('university'),
            department: formData.get('department'),
            year: parseInt(formData.get('year'))
        };

        // Validation
        if (!this.validateSignupData(data)) {
            return;
        }

        const submitBtn = e.target.querySelector('button[type="submit"]');
        this.setLoadingState(submitBtn, true);

        try {
            // Demo kayıt simülasyonu
            await this.simulateSignup(data);

            this.showSuccess('Hesabınız başarıyla oluşturuldu! Yönlendiriliyorsunuz...');

            setTimeout(() => {
                window.location.href = 'personality_test.html';
            }, 1500);

        } catch (error) {
            this.showError(error.message);
        } finally {
            this.setLoadingState(submitBtn, false);
        }
    }

    async simulateLogin(email, password) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                // Demo amaçlı basit kontrol
                if (email && password.length >= 6) {
                    // Demo kullanıcı oluştur
                    const user = {
                        name: email.split('@')[0],
                        email: email,
                        is_test_completed: true
                    };

                    localStorage.setItem('friendzone_token', 'demo_token_' + Date.now());
                    localStorage.setItem('friendzone_user', JSON.stringify(user));

                    resolve({ success: true, user });
                } else {
                    reject(new Error('E-posta veya şifre hatalı.'));
                }
            }, 1500);
        });
    }

    async simulateSignup(data) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const user = {
                    name: data.name,
                    email: data.email,
                    university: data.university,
                    department: data.department,
                    year: data.year,
                    is_test_completed: false
                };

                localStorage.setItem('friendzone_token', 'demo_token_' + Date.now());
                localStorage.setItem('friendzone_user', JSON.stringify(user));

                resolve({ success: true });
            }, 1500);
        });
    }

    validateLoginData(data) {
        let isValid = true;

        // Email validation
        if (!data.email || !this.isValidEmail(data.email)) {
            this.showFieldError('email', 'Geçerli bir e-posta adresi girin');
            isValid = false;
        } else {
            this.clearFieldError('email');
        }

        // Password validation
        if (!data.password || data.password.length < 6) {
            this.showFieldError('password', 'Şifre en az 6 karakter olmalıdır');
            isValid = false;
        } else {
            this.clearFieldError('password');
        }

        return isValid;
    }

    validateSignupData(data) {
        let isValid = true;

        // Name validation
        if (!data.name || data.name.length < 2) {
            this.showFieldError('name', 'İsim en az 2 karakter olmalıdır');
            isValid = false;
        } else {
            this.clearFieldError('name');
        }

        // Email validation
        if (!data.email || !this.isValidEmail(data.email)) {
            this.showFieldError('email', 'Geçerli bir üniversite e-posta adresi girin');
            isValid = false;
        } else {
            this.clearFieldError('email');
        }

        // Password validation
        if (!data.password || data.password.length < 6) {
            this.showFieldError('password', 'Şifre en az 6 karakter olmalıdır');
            isValid = false;
        } else {
            this.clearFieldError('password');
        }

        // University validation
        if (!data.university) {
            this.showFieldError('university', 'Üniversite seçiniz');
            isValid = false;
        } else {
            this.clearFieldError('university');
        }

        return isValid;
    }

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    showFieldError(fieldName, message) {
        const field = document.getElementById(fieldName);
        if (!field) return;

        const formGroup = field.closest('.form-group');
        if (!formGroup) return;

        formGroup.classList.add('error');

        let messageElement = formGroup.querySelector('.form-message');
        if (!messageElement) {
            messageElement = document.createElement('div');
            messageElement.className = 'form-message error';
            formGroup.appendChild(messageElement);
        }

        messageElement.textContent = message;
    }

    clearFieldError(fieldName) {
        const field = document.getElementById(fieldName);
        if (!field) return;

        const formGroup = field.closest('.form-group');
        if (!formGroup) return;

        formGroup.classList.remove('error');

        const messageElement = formGroup.querySelector('.form-message');
        if (messageElement) {
            messageElement.remove();
        }
    }

    setLoadingState(button, isLoading) {
        if (isLoading) {
            button.classList.add('btn-loading');
            button.disabled = true;
        } else {
            button.classList.remove('btn-loading');
            button.disabled = false;
        }
    }

    showError(message) {
        this.removeMessages();

        const form = document.querySelector('.auth-form');
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;

        form.insertBefore(errorDiv, form.firstChild);

        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    showSuccess(message) {
        this.removeMessages();

        const form = document.querySelector('.auth-form');
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;

        form.insertBefore(successDiv, form.firstChild);
    }

    removeMessages() {
        const existingMessages = document.querySelectorAll('.error-message, .success-message');
        existingMessages.forEach(msg => msg.remove());
    }

    checkExistingAuth() {
        const token = localStorage.getItem('friendzone_token');
        if (token && (window.location.pathname.includes('login.html') ||
                      window.location.pathname.includes('signup.html'))) {
            this.checkTestStatusAndRedirect();
        }
    }

    async checkTestStatusAndRedirect() {
        try {
            const userStr = localStorage.getItem('friendzone_user');
            if (userStr) {
                const user = JSON.parse(userStr);
                if (user.is_test_completed) {
                    window.location.href = 'communities.html';
                } else {
                    window.location.href = 'personality_test.html';
                }
            }
        } catch (error) {
            console.error('Auth check failed:', error);
            localStorage.removeItem('friendzone_token');
            localStorage.removeItem('friendzone_user');
        }
    }

    setupRealTimeValidation() {
        // Email validation
        const emailInput = document.getElementById('email');
        if (emailInput) {
            emailInput.addEventListener('blur', () => {
                const value = emailInput.value.trim();
                if (value && !this.isValidEmail(value)) {
                    this.showFieldError('email', 'Geçerli bir e-posta adresi girin');
                } else if (value) {
                    this.clearFieldError('email');
                }
            });
        }
    }
}

// Initialize auth manager
document.addEventListener('DOMContentLoaded', () => {
    window.authManager = new AuthManager();
});