/**
 * Form Validation and Enhancement JavaScript
 * Online Exam Management System
 */

// Wait for DOM to load
document.addEventListener('DOMContentLoaded', function() {
    
    // =====================================
    // 1. Real-time Form Validation
    // =====================================
    
    // Email validation
    const emailInputs = document.querySelectorAll('input[type="email"]');
    emailInputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateEmail(this);
        });
        
        input.addEventListener('input', function() {
            if (this.value.length > 0) {
                validateEmail(this);
            }
        });
    });
    
    function validateEmail(input) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const isValid = emailRegex.test(input.value);
        
        if (!isValid && input.value.length > 0) {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
            showError(input, 'Please enter a valid email address');
        } else if (isValid) {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            hideError(input);
        }
    }
    
    // =====================================
    // 2. Password Strength Checker
    // =====================================
    
    const passwordInputs = document.querySelectorAll('input[type="password"][name="password"], input[type="password"][name="new_password"]');
    passwordInputs.forEach(input => {
        // Create strength indicator
        const strengthDiv = document.createElement('div');
        strengthDiv.className = 'password-strength mt-2';
        strengthDiv.innerHTML = `
            <div class="progress" style="height: 5px;">
                <div class="progress-bar" role="progressbar" style="width: 0%"></div>
            </div>
            <small class="strength-text text-muted"></small>
        `;
        input.parentNode.appendChild(strengthDiv);
        
        input.addEventListener('input', function() {
            checkPasswordStrength(this, strengthDiv);
        });
    });
    
    function checkPasswordStrength(input, strengthDiv) {
        const password = input.value;
        const progressBar = strengthDiv.querySelector('.progress-bar');
        const strengthText = strengthDiv.querySelector('.strength-text');
        
        let strength = 0;
        let text = '';
        let color = '';
        
        if (password.length === 0) {
            progressBar.style.width = '0%';
            strengthText.textContent = '';
            return;
        }
        
        // Length check
        if (password.length >= 8) strength += 25;
        if (password.length >= 12) strength += 10;
        
        // Complexity checks
        if (/[a-z]/.test(password)) strength += 15;
        if (/[A-Z]/.test(password)) strength += 15;
        if (/[0-9]/.test(password)) strength += 15;
        if (/[^a-zA-Z0-9]/.test(password)) strength += 20;
        
        // Determine strength level
        if (strength < 40) {
            text = 'Weak';
            color = 'bg-danger';
        } else if (strength < 60) {
            text = 'Fair';
            color = 'bg-warning';
        } else if (strength < 80) {
            text = 'Good';
            color = 'bg-info';
        } else {
            text = 'Strong';
            color = 'bg-success';
        }
        
        progressBar.style.width = strength + '%';
        progressBar.className = 'progress-bar ' + color;
        strengthText.textContent = 'Password Strength: ' + text;
    }
    
    // =====================================
    // 3. Password Confirmation Match
    // =====================================
    
    const confirmPasswordInputs = document.querySelectorAll('input[name="confirm_password"]');
    confirmPasswordInputs.forEach(confirmInput => {
        const passwordInput = document.querySelector('input[name="password"], input[name="new_password"]');
        
        if (passwordInput) {
            confirmInput.addEventListener('input', function() {
                checkPasswordMatch(passwordInput, confirmInput);
            });
            
            passwordInput.addEventListener('input', function() {
                if (confirmInput.value.length > 0) {
                    checkPasswordMatch(passwordInput, confirmInput);
                }
            });
        }
    });
    
    function checkPasswordMatch(password, confirm) {
        if (confirm.value.length === 0) return;
        
        if (password.value !== confirm.value) {
            confirm.classList.add('is-invalid');
            confirm.classList.remove('is-valid');
            showError(confirm, 'Passwords do not match');
        } else {
            confirm.classList.remove('is-invalid');
            confirm.classList.add('is-valid');
            hideError(confirm);
        }
    }
    
    // =====================================
    // 4. File Upload Validation
    // =====================================
    
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            validateFileUpload(this);
        });
    });
    
    function validateFileUpload(input) {
        const file = input.files[0];
        if (!file) return;
        
        // Check file size (10MB max)
        const maxSize = 10 * 1024 * 1024; // 10MB in bytes
        if (file.size > maxSize) {
            input.classList.add('is-invalid');
            showError(input, 'File size must not exceed 10MB');
            input.value = '';
            return;
        }
        
        // Check file type
        const allowedTypes = ['.pdf', '.doc', '.docx', '.txt', '.zip'];
        const fileName = file.name.toLowerCase();
        const isValidType = allowedTypes.some(type => fileName.endsWith(type));
        
        if (!isValidType) {
            input.classList.add('is-invalid');
            showError(input, 'File type not allowed. Allowed: PDF, DOC, DOCX, TXT, ZIP');
            input.value = '';
            return;
        }
        
        // Valid file
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        hideError(input);
        
        // Show file name
        const fileNameDisplay = document.createElement('div');
        fileNameDisplay.className = 'file-name mt-2 text-success';
        fileNameDisplay.innerHTML = `<i class="fas fa-check-circle me-2"></i>${file.name} (${formatFileSize(file.size)})`;
        
        // Remove existing file name display
        const existingDisplay = input.parentNode.querySelector('.file-name');
        if (existingDisplay) existingDisplay.remove();
        
        input.parentNode.appendChild(fileNameDisplay);
    }
    
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }
    
    // =====================================
    // 5. Date/Time Validation
    // =====================================
    
    const dateTimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    dateTimeInputs.forEach(input => {
        // Set minimum date to current date
        const now = new Date();
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
        input.min = now.toISOString().slice(0, 16);
        
        input.addEventListener('change', function() {
            validateDateTime(this);
        });
    });
    
    function validateDateTime(input) {
        const selectedDate = new Date(input.value);
        const now = new Date();
        
        if (input.name === 'start_time' && selectedDate < now) {
            input.classList.add('is-invalid');
            showError(input, 'Start time cannot be in the past');
            return false;
        }
        
        // Check end time is after start time
        if (input.name === 'end_time') {
            const startTimeInput = document.querySelector('input[name="start_time"]');
            if (startTimeInput && startTimeInput.value) {
                const startTime = new Date(startTimeInput.value);
                if (selectedDate <= startTime) {
                    input.classList.add('is-invalid');
                    showError(input, 'End time must be after start time');
                    return false;
                }
            }
        }
        
        input.classList.remove('is-invalid');
        input.classList.add('is-valid');
        hideError(input);
        return true;
    }
    
    // =====================================
    // 6. Marks Validation (0-100)
    // =====================================
    
    const marksInputs = document.querySelectorAll('input[name="marks"]');
    marksInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateMarks(this);
        });
    });
    
    function validateMarks(input) {
        const value = parseFloat(input.value);
        
        if (isNaN(value) || value < 0 || value > 100) {
            input.classList.add('is-invalid');
            showError(input, 'Marks must be between 0 and 100');
        } else {
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            hideError(input);
            
            // Auto-calculate grade
            autoCalculateGrade(value);
        }
    }
    
    function autoCalculateGrade(marks) {
        const gradeSelect = document.querySelector('select[name="grade"]');
        if (!gradeSelect) return;
        
        let grade = '';
        if (marks >= 90) grade = 'A+';
        else if (marks >= 85) grade = 'A';
        else if (marks >= 80) grade = 'A-';
        else if (marks >= 75) grade = 'B+';
        else if (marks >= 70) grade = 'B';
        else if (marks >= 65) grade = 'B-';
        else if (marks >= 60) grade = 'C+';
        else if (marks >= 55) grade = 'C';
        else if (marks >= 50) grade = 'C-';
        else if (marks >= 40) grade = 'D';
        else grade = 'F';
        
        gradeSelect.value = grade;
    }
    
    // =====================================
    // 7. Form Submission Prevention on Invalid
    // =====================================
    
    const forms = document.querySelectorAll('form.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            // Check for invalid fields
            const invalidFields = form.querySelectorAll('.is-invalid');
            
            if (invalidFields.length > 0 || !form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Scroll to first error
                invalidFields[0]?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
                // Show error message
                showFormError(form, 'Please correct the errors before submitting');
            }
            
            form.classList.add('was-validated');
        });
    });
    
    // =====================================
    // 8. Helper Functions
    // =====================================
    
    function showError(input, message) {
        let errorDiv = input.parentNode.querySelector('.invalid-feedback');
        
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback d-block';
            input.parentNode.appendChild(errorDiv);
        }
        
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
    
    function hideError(input) {
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }
    
    function showFormError(form, message) {
        let errorDiv = form.querySelector('.form-error-message');
        
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger form-error-message';
            form.insertBefore(errorDiv, form.firstChild);
        }
        
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle me-2"></i>${message}`;
    }
    
    // =====================================
    // 9. Character Counter for Textareas
    // =====================================
    
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        const maxLength = textarea.getAttribute('maxlength');
        
        if (maxLength) {
            const counter = document.createElement('small');
            counter.className = 'form-text text-muted char-counter';
            textarea.parentNode.appendChild(counter);
            
            updateCounter();
            
            textarea.addEventListener('input', updateCounter);
            
            function updateCounter() {
                const remaining = maxLength - textarea.value.length;
                counter.textContent = `${textarea.value.length} / ${maxLength} characters`;
                
                if (remaining < 50) {
                    counter.classList.add('text-warning');
                } else {
                    counter.classList.remove('text-warning');
                }
            }
        }
    });
    
    // =====================================
    // 10. Confirm Before Leaving Form
    // =====================================
    
    let formChanged = false;
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            input.addEventListener('change', function() {
                formChanged = true;
            });
        });
        
        form.addEventListener('submit', function() {
            formChanged = false;
        });
    });
    
    window.addEventListener('beforeunload', function(e) {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            return e.returnValue;
        }
    });
    
    // =====================================
    // 11. Select All Checkboxes
    // =====================================
    
    const selectAllCheckboxes = document.querySelectorAll('input[type="checkbox"][data-select-all]');
    selectAllCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const target = this.getAttribute('data-select-all');
            const targetCheckboxes = document.querySelectorAll(`input[type="checkbox"][data-group="${target}"]`);
            
            targetCheckboxes.forEach(cb => {
                cb.checked = this.checked;
            });
        });
    });
    
    // =====================================
    // 12. Dynamic Search/Filter
    // =====================================
    
    const searchInputs = document.querySelectorAll('input[data-search-target]');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const target = this.getAttribute('data-search-target');
            const items = document.querySelectorAll(target);
            
            items.forEach(item => {
                const text = item.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    });
    
    console.log('Form validation JavaScript loaded successfully');
});

// =====================================
// Utility Functions (Global)
// =====================================

function confirmAction(message) {
    return confirm(message || 'Are you sure you want to perform this action?');
}

function confirmDelete(itemName) {
    return confirm(`Are you sure you want to delete "${itemName}"? This action cannot be undone.`);
}

function showLoadingSpinner(button) {
    const originalText = button.innerHTML;
    button.setAttribute('data-original-text', originalText);
    button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    button.disabled = true;
}

function hideLoadingSpinner(button) {
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.innerHTML = originalText;
        button.disabled = false;
    }
}