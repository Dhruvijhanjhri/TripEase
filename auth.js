/**
 * TripEase Authentication System
 * Handles login and signup form validation and user management
 */

class AuthSystem {
    constructor() {
        this.users = JSON.parse(localStorage.getItem('tripease_users')) || [];
        this.currentUser = JSON.parse(localStorage.getItem('tripease_current_user')) || null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.updateAuthUI();
    }

    setupEventListeners() {
        // Login form submission
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }

        // Signup form submission
        const signupForm = document.getElementById('signupForm');
        if (signupForm) {
            signupForm.addEventListener('submit', (e) => this.handleSignup(e));
        }

        // Modal close buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-close') || e.target.classList.contains('modal-overlay')) {
                this.closeModal();
            }
        });

        // Login/Signup button clicks
        document.addEventListener('click', (e) => {
            if (e.target.id === 'loginBtn') {
                this.openModal('login');
            } else if (e.target.id === 'signupBtn') {
                this.openModal('signup');
            } else if (e.target.id === 'logoutBtn') {
                this.logout();
            } else if (e.target.id === 'switchToSignup') {
                e.preventDefault();
                this.openModal('signup');
            } else if (e.target.id === 'switchToLogin') {
                e.preventDefault();
                this.openModal('login');
            }
        });

        // Form input validation on blur
        document.addEventListener('blur', (e) => {
            if (e.target.matches('#loginForm input, #signupForm input')) {
                this.validateField(e.target);
            }
        }, true);

        // Form input validation on input
        document.addEventListener('input', (e) => {
            if (e.target.matches('#loginForm input, #signupForm input')) {
                this.clearFieldError(e.target);
            }
        });
    }

    // Validation Rules
    validationRules = {
        email: {
            required: true,
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Please enter a valid email address'
        },
        password: {
            required: true,
            minLength: 6,
            message: 'Password must be at least 6 characters long'
        },
        confirmPassword: {
            required: true,
            message: 'Passwords do not match'
        },
        firstName: {
            required: true,
            minLength: 2,
            pattern: /^[a-zA-Z\s]+$/,
            message: 'First name must be at least 2 characters and contain only letters'
        },
        lastName: {
            required: true,
            minLength: 2,
            pattern: /^[a-zA-Z\s]+$/,
            message: 'Last name must be at least 2 characters and contain only letters'
        },
        phone: {
            required: true,
            pattern: /^[\+]?[1-9][\d]{0,15}$/,
            message: 'Please enter a valid phone number'
        }
    };

    validateField(field) {
        const fieldName = field.name;
        const value = field.value.trim();
        const rules = this.validationRules[fieldName];

        if (!rules) return true;

        // Clear previous errors
        this.clearFieldError(field);

        // Required field check
        if (rules.required && !value) {
            this.showFieldError(field, `${this.getFieldLabel(fieldName)} is required`);
            return false;
        }

        // Pattern validation
        if (value && rules.pattern && !rules.pattern.test(value)) {
            this.showFieldError(field, rules.message);
            return false;
        }

        // Minimum length validation
        if (value && rules.minLength && value.length < rules.minLength) {
            this.showFieldError(field, rules.message);
            return false;
        }

        // Confirm password validation
        if (fieldName === 'confirmPassword') {
            const passwordField = document.getElementById('password');
            if (passwordField && value !== passwordField.value) {
                this.showFieldError(field, rules.message);
                return false;
            }
        }

        return true;
    }

    validateForm(form) {
        const fields = form.querySelectorAll('input[required]');
        let isValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    showFieldError(field, message) {
        field.classList.add('error');
        
        // Remove existing error message
        const existingError = field.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('error');
        const errorMessage = field.parentNode.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }

    getFieldLabel(fieldName) {
        const labels = {
            email: 'Email',
            password: 'Password',
            confirmPassword: 'Confirm Password',
            firstName: 'First Name',
            lastName: 'Last Name',
            phone: 'Phone Number'
        };
        return labels[fieldName] || fieldName;
    }

    async handleLogin(e) {
        e.preventDefault();
        
        const form = e.target;
        if (!this.validateForm(form)) {
            return;
        }

        const formData = new FormData(form);
        const email = formData.get('email').trim();
        const password = formData.get('password');

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Signing in...';
        submitBtn.disabled = true;

        try {
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 1000));

            const user = this.users.find(u => u.email === email && u.password === password);
            
            if (user) {
                this.currentUser = user;
                localStorage.setItem('tripease_current_user', JSON.stringify(user));
                this.showNotification('Login successful! Welcome back!', 'success');
                this.closeModal();
                this.updateAuthUI();
                form.reset();
            } else {
                this.showNotification('Invalid email or password', 'error');
            }
        } catch (error) {
            this.showNotification('Login failed. Please try again.', 'error');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    async handleSignup(e) {
        e.preventDefault();
        
        const form = e.target;
        if (!this.validateForm(form)) {
            return;
        }

        const formData = new FormData(form);
        const userData = {
            id: Date.now().toString(),
            email: formData.get('email').trim(),
            password: formData.get('password'),
            firstName: formData.get('firstName').trim(),
            lastName: formData.get('lastName').trim(),
            phone: formData.get('phone').trim(),
            createdAt: new Date().toISOString()
        };

        // Check if user already exists
        if (this.users.find(u => u.email === userData.email)) {
            this.showNotification('An account with this email already exists', 'error');
            return;
        }

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Creating account...';
        submitBtn.disabled = true;

        try {
            // Simulate API call delay
            await new Promise(resolve => setTimeout(resolve, 1500));

            this.users.push(userData);
            localStorage.setItem('tripease_users', JSON.stringify(this.users));
            
            this.currentUser = userData;
            localStorage.setItem('tripease_current_user', JSON.stringify(userData));
            
            this.showNotification('Account created successfully! Welcome to TripEase!', 'success');
            this.closeModal();
            this.updateAuthUI();
            form.reset();
        } catch (error) {
            this.showNotification('Signup failed. Please try again.', 'error');
        } finally {
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }
    }

    logout() {
        this.currentUser = null;
        localStorage.removeItem('tripease_current_user');
        this.showNotification('Logged out successfully', 'info');
        this.updateAuthUI();
    }

    openModal(type) {
        const modal = document.getElementById('authModal');
        const loginForm = document.getElementById('loginForm');
        const signupForm = document.getElementById('signupForm');
        const modalTitle = document.getElementById('modalTitle');

        if (type === 'login') {
            loginForm.style.display = 'block';
            signupForm.style.display = 'none';
            modalTitle.textContent = 'Sign In';
        } else {
            loginForm.style.display = 'none';
            signupForm.style.display = 'block';
            modalTitle.textContent = 'Create Account';
        }

        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    closeModal() {
        const modal = document.getElementById('authModal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        
        // Clear form errors
        const forms = modal.querySelectorAll('form');
        forms.forEach(form => {
            const errors = form.querySelectorAll('.error-message');
            errors.forEach(error => error.remove());
            const errorFields = form.querySelectorAll('.error');
            errorFields.forEach(field => field.classList.remove('error'));
        });
    }

    updateAuthUI() {
        const loginBtn = document.getElementById('loginBtn');
        const signupBtn = document.getElementById('signupBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        const userMenu = document.getElementById('userMenu');

        if (this.currentUser) {
            // User is logged in
            if (loginBtn) loginBtn.style.display = 'none';
            if (signupBtn) signupBtn.style.display = 'none';
            if (logoutBtn) logoutBtn.style.display = 'inline-block';
            if (userMenu) {
                userMenu.style.display = 'block';
                userMenu.innerHTML = `
                    <span>Welcome, ${this.currentUser.firstName}!</span>
                `;
            }
        } else {
            // User is not logged in
            if (loginBtn) loginBtn.style.display = 'inline-block';
            if (signupBtn) signupBtn.style.display = 'inline-block';
            if (logoutBtn) logoutBtn.style.display = 'none';
            if (userMenu) userMenu.style.display = 'none';
        }
    }

    showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        `;

        document.body.appendChild(notification);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);

        // Close button functionality
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => notification.remove());
    }

    // Utility method to check if user is logged in
    isLoggedIn() {
        return this.currentUser !== null;
    }

    // Utility method to get current user
    getCurrentUser() {
        return this.currentUser;
    }
}

// Initialize the authentication system when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.authSystem = new AuthSystem();
});

// Export for potential use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AuthSystem;
}
