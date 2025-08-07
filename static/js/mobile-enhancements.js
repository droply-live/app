/**
 * Mobile Enhancements for Droply
 * Improves mobile user experience with touch-friendly interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeMobileEnhancements();
});

/**
 * Initialize all mobile-specific enhancements
 */
function initializeMobileEnhancements() {
    // Only run on mobile devices
    if (window.innerWidth > 768) return;
    
    initializeTouchGestures();
    initializeMobileCards();
    initializeMobileForms();
    initializeMobileNavigation();
    initializeMobileSearch();
    initializeMobileBookings();
    initializeMobileProfile();
}

/**
 * Add touch gesture support for better mobile interaction
 */
function initializeTouchGestures() {
    // Add swipe support for expert cards
    const expertCards = document.querySelectorAll('.expert-card-enhanced');
    expertCards.forEach(card => {
        let startX = 0;
        let startY = 0;
        let isSwiping = false;
        
        card.addEventListener('touchstart', function(e) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isSwiping = false;
        });
        
        card.addEventListener('touchmove', function(e) {
            if (!startX || !startY) return;
            
            const deltaX = e.touches[0].clientX - startX;
            const deltaY = e.touches[0].clientY - startY;
            
            if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) {
                isSwiping = true;
                e.preventDefault();
            }
        });
        
        card.addEventListener('touchend', function(e) {
            if (!isSwiping) return;
            
            const deltaX = e.changedTouches[0].clientX - startX;
            
            if (Math.abs(deltaX) > 50) {
                // Swipe detected - could be used for quick actions
                if (deltaX > 0) {
                    // Swipe right - could show quick book button
                    showQuickAction(card, 'book');
                } else {
                    // Swipe left - could show quick message button
                    showQuickAction(card, 'message');
                }
            }
            
            startX = 0;
            startY = 0;
            isSwiping = false;
        });
    });
}

/**
 * Show quick action buttons on swipe
 */
function showQuickAction(card, action) {
    // Create or show quick action overlay
    let overlay = card.querySelector('.quick-action-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'quick-action-overlay';
        overlay.innerHTML = `
            <div class="quick-action-buttons">
                <button class="quick-action-btn book-btn" onclick="quickBook('${card.dataset.expertId}')">
                    <i class="fas fa-calendar-plus"></i>
                    <span>Book Now</span>
                </button>
                <button class="quick-action-btn message-btn" onclick="quickMessage('${card.dataset.expertId}')">
                    <i class="fas fa-comment"></i>
                    <span>Message</span>
                </button>
            </div>
        `;
        card.appendChild(overlay);
    }
    
    overlay.style.display = 'flex';
    setTimeout(() => {
        overlay.style.display = 'none';
    }, 3000);
}

/**
 * Enhance mobile card interactions
 */
function initializeMobileCards() {
    // Add touch feedback to cards
    const cards = document.querySelectorAll('.card, .expert-card-enhanced, .booking-card');
    cards.forEach(card => {
        card.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        });
        
        card.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
        
        card.addEventListener('touchcancel', function() {
            this.style.transform = 'scale(1)';
        });
    });
    
    // Improve card spacing for mobile
    cards.forEach(card => {
        card.style.marginBottom = '1rem';
        card.style.borderRadius = '12px';
    });
}

/**
 * Enhance mobile form interactions
 */
function initializeMobileForms() {
    // Prevent zoom on input focus (iOS)
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            if (window.innerWidth <= 768) {
                // Add a small delay to prevent zoom
                setTimeout(() => {
                    this.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }, 300);
            }
        });
    });
    
    // Improve form validation feedback for mobile
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const invalidInputs = form.querySelectorAll(':invalid');
            if (invalidInputs.length > 0) {
                e.preventDefault();
                showMobileValidationMessage('Please check the highlighted fields');
                invalidInputs[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        });
    });
}

/**
 * Show mobile-friendly validation message
 */
function showMobileValidationMessage(message) {
    const notification = document.createElement('div');
    notification.className = 'mobile-notification';
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 20px;
        right: 20px;
        background: #ff4444;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        z-index: 10000;
        text-align: center;
        font-weight: 500;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

/**
 * Enhance mobile navigation with hamburger menu
 */
function initializeMobileNavigation() {
    const hamburger = document.getElementById('mobileHamburger');
    const navMenu = document.getElementById('mobileNavMenu');
    const navOverlay = document.getElementById('mobileNavOverlay');
    const navClose = document.getElementById('mobileNavClose');

    if (!hamburger || !navMenu || !navOverlay || !navClose) {
        console.warn('Mobile navigation elements not found');
        return;
    }

    // Toggle menu
    function toggleMenu() {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
        navOverlay.classList.toggle('active');
        document.body.style.overflow = navMenu.classList.contains('active') ? 'hidden' : '';
        
        // Add haptic feedback
        if ('vibrate' in navigator) {
            navigator.vibrate(10);
        }
    }

    // Close menu
    function closeMenu() {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
        navOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Event listeners
    hamburger.addEventListener('click', toggleMenu);
    navClose.addEventListener('click', closeMenu);
    navOverlay.addEventListener('click', closeMenu);

    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && navMenu.classList.contains('active')) {
            closeMenu();
        }
    });

    // Close menu on window resize (if switching to desktop)
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && navMenu.classList.contains('active')) {
            closeMenu();
        }
    });

    // Add haptic feedback for navigation links
    const navLinks = document.querySelectorAll('.mobile-nav-item');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if ('vibrate' in navigator) {
                navigator.vibrate(10);
            }
        });
    });

    console.log('Mobile navigation initialized');
}

/**
 * Enhance mobile search experience
 */
function initializeMobileSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        // Add search suggestions for mobile
        searchInput.addEventListener('input', function() {
            if (this.value.length > 2) {
                showMobileSearchSuggestions(this.value);
            } else {
                hideMobileSearchSuggestions();
            }
        });
        
        // Add voice search button for mobile
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const voiceBtn = document.createElement('button');
            voiceBtn.className = 'voice-search-btn';
            voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>';
            voiceBtn.style.cssText = `
                position: absolute;
                right: 10px;
                top: 50%;
                transform: translateY(-50%);
                background: none;
                border: none;
                color: #666;
                padding: 8px;
                border-radius: 50%;
            `;
            
            voiceBtn.addEventListener('click', function() {
                startVoiceSearch(searchInput);
            });
            
            searchInput.parentElement.style.position = 'relative';
            searchInput.parentElement.appendChild(voiceBtn);
        }
    }
}

/**
 * Show mobile search suggestions
 */
function showMobileSearchSuggestions(query) {
    let suggestions = document.getElementById('mobile-search-suggestions');
    if (!suggestions) {
        suggestions = document.createElement('div');
        suggestions.id = 'mobile-search-suggestions';
        suggestions.style.cssText = `
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            z-index: 1000;
            max-height: 200px;
            overflow-y: auto;
        `;
        
        const searchContainer = document.querySelector('.search-section');
        searchContainer.appendChild(suggestions);
    }
    
    // Mock suggestions - in real app, this would be AJAX
    const mockSuggestions = [
        'Business Coach',
        'Life Coach',
        'Career Advisor',
        'Wellness Expert',
        'Design Consultant'
    ].filter(s => s.toLowerCase().includes(query.toLowerCase()));
    
    suggestions.innerHTML = mockSuggestions.map(s => 
        `<div class="suggestion-item" onclick="selectSuggestion('${s}')">${s}</div>`
    ).join('');
    
    suggestions.style.display = 'block';
}

/**
 * Hide mobile search suggestions
 */
function hideMobileSearchSuggestions() {
    const suggestions = document.getElementById('mobile-search-suggestions');
    if (suggestions) {
        suggestions.style.display = 'none';
    }
}

/**
 * Select a search suggestion
 */
function selectSuggestion(text) {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.value = text;
        searchInput.form.submit();
    }
    hideMobileSearchSuggestions();
}

/**
 * Start voice search
 */
function startVoiceSearch(input) {
    if ('webkitSpeechRecognition' in window) {
        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            input.value = transcript;
            input.form.submit();
        };
        
        recognition.start();
    }
}

/**
 * Enhance mobile booking experience
 */
function initializeMobileBookings() {
    // Add quick booking actions
    const bookingCards = document.querySelectorAll('.booking-card');
    bookingCards.forEach(card => {
        const quickActions = document.createElement('div');
        quickActions.className = 'quick-booking-actions';
        quickActions.innerHTML = `
            <button class="quick-action-btn" onclick="quickReschedule(this)">
                <i class="fas fa-calendar-alt"></i>
                <span>Reschedule</span>
            </button>
            <button class="quick-action-btn" onclick="quickCancel(this)">
                <i class="fas fa-times"></i>
                <span>Cancel</span>
            </button>
        `;
        
        card.appendChild(quickActions);
    });
}

/**
 * Enhance mobile profile experience
 */
function initializeMobileProfile() {
    // Add profile image upload enhancement
    const profileImageInput = document.querySelector('input[type="file"]');
    if (profileImageInput) {
        profileImageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                showMobileImagePreview(file);
            }
        });
    }
}

/**
 * Show mobile image preview
 */
function showMobileImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const preview = document.createElement('div');
        preview.className = 'mobile-image-preview';
        preview.innerHTML = `
            <img src="${e.target.result}" alt="Preview" style="max-width: 100%; border-radius: 8px;">
            <button onclick="this.parentElement.remove()" style="position: absolute; top: 10px; right: 10px; background: #ff4444; color: white; border: none; border-radius: 50%; width: 30px; height: 30px;">×</button>
        `;
        preview.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            z-index: 10000;
            max-width: 90vw;
        `;
        
        document.body.appendChild(preview);
    };
    reader.readAsDataURL(file);
}

/**
 * Quick book function
 */
function quickBook(expertId) {
    // Navigate to booking page
    window.location.href = `/book/${expertId}`;
}

/**
 * Quick message function
 */
function quickMessage(expertId) {
    // Navigate to messaging page
    window.location.href = `/message/${expertId}`;
}

/**
 * Quick reschedule function
 */
function quickReschedule(button) {
    const bookingId = button.closest('.booking-card').dataset.bookingId;
    window.location.href = `/booking/${bookingId}/reschedule`;
}

/**
 * Quick cancel function
 */
function quickCancel(button) {
    const bookingId = button.closest('.booking-card').dataset.bookingId;
    if (confirm('Are you sure you want to cancel this booking?')) {
        window.location.href = `/booking/${bookingId}/cancel`;
    }
}

// Export functions for global access
window.quickBook = quickBook;
window.quickMessage = quickMessage;
window.quickReschedule = quickReschedule;
window.quickCancel = quickCancel;
window.selectSuggestion = selectSuggestion;
