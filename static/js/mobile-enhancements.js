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
    
    // Skip mobile enhancements on profile pages
    if (window.location.pathname.includes('/profile/') || 
        window.location.pathname.includes('/user/') ||
        document.querySelector('.modern-profile-page')) {
        console.log('Skipping mobile enhancements on profile page');
        return;
    }
    
    // Skip mobile enhancements on availability page (has its own mobile handling)
    if (window.location.pathname.includes('/availability')) {
        console.log('Skipping mobile enhancements on availability page');
        return;
    }
    
    console.log('Initializing mobile enhancements...');
    
    initializeTouchGestures();
    initializeMobileCards();
    initializeMobileForms();
    // Skip navigation initialization as it's handled in base template
    // initializeMobileNavigation();
    initializeMobileUserMenu();
    initializeMobileSearch();
    initializeMobileBookings();
    initializeMobileProfile();
    initializeMobileScroll();
    initializeMobileViewport();
    initializeMobilePerformance();
    initializeMobileAccessibility();
}

/**
 * Add touch gesture support for better mobile interaction
 */
function initializeTouchGestures() {
    // Add swipe support for user cards
    const userCards = document.querySelectorAll('.user-card-enhanced');
    userCards.forEach(card => {
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
                <button class="quick-action-btn book-btn" onclick="quickBook('${card.dataset.userId}')">
                    <i class="fas fa-calendar-plus"></i>
                    <span>Book Now</span>
                </button>
                <button class="quick-action-btn message-btn" onclick="quickMessage('${card.dataset.userId}')">
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
    const cards = document.querySelectorAll('.card, .user-card-enhanced, .booking-card');
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
 * Enhance mobile navigation with modern hamburger menu
 */
function initializeMobileNavigation() {
    const hamburger = document.getElementById('topNavHamburger');
    const navMenu = document.getElementById('mobileNavMenu');
    const navOverlay = document.getElementById('mobileNavOverlay');
    const navClose = document.getElementById('mobileNavClose');

    if (!hamburger || !navMenu || !navOverlay || !navClose) {
        console.warn('Mobile navigation elements not found');
        return;
    }

    let isMenuOpen = false;

    // Toggle menu with modern animations
    function toggleMenu() {
        if (isMenuOpen) {
            closeMenu();
        } else {
            openMenu();
        }
    }

    // Open menu with smooth slide-in animation
    function openMenu() {
        navMenu.style.display = 'block';
        navOverlay.style.display = 'block';
        
        // Trigger animations
        setTimeout(() => {
            navMenu.classList.add('active');
            navOverlay.classList.add('active');
        }, 10);
        
        document.body.style.overflow = 'hidden';
        isMenuOpen = true;
        
        // Add haptic feedback
        if ('vibrate' in navigator) {
            navigator.vibrate(10);
        }
    }

    // Close menu with smooth slide-out animation
    function closeMenu() {
        navMenu.classList.remove('active');
        navOverlay.classList.remove('active');
        
        // Hide elements after animation
        setTimeout(() => {
            navMenu.style.display = 'none';
            navOverlay.style.display = 'none';
        }, 400);
        
        document.body.style.overflow = '';
        isMenuOpen = false;
    }

    // Event listeners
    hamburger.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        toggleMenu();
    });
    
    navClose.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        closeMenu();
    });
    
    navOverlay.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        closeMenu();
    });

    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isMenuOpen) {
            closeMenu();
        }
    });

    // Close menu on window resize (if switching to desktop)
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768 && isMenuOpen) {
            closeMenu();
        }
    });

    // Close menu when clicking on nav items
    const navItems = document.querySelectorAll('.mobile-nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            setTimeout(() => {
                closeMenu();
            }, 150);
        });
    });

    // Prevent body scroll when menu is open
    document.addEventListener('touchmove', function(e) {
        if (isMenuOpen) {
            e.preventDefault();
        }
    }, { passive: false });

    // Add haptic feedback for navigation links
    navItems.forEach(link => {
        link.addEventListener('click', function() {
            if ('vibrate' in navigator) {
                navigator.vibrate(10);
            }
        });
    });

    console.log('Modern mobile navigation initialized successfully');
}

/**
 * Initialize mobile user menu dropdown functionality
 */
function initializeMobileUserMenu() {
    const mobileUserMenuToggle = document.getElementById('mobileUserMenuToggle');
    const mobileUserDropdown = document.getElementById('mobileUserDropdown');

    if (!mobileUserMenuToggle || !mobileUserDropdown) {
        console.warn('Mobile user menu elements not found');
        return;
    }

    let isMobileDropdownOpen = false;

    // Toggle dropdown with smooth animations
    function toggleMobileDropdown() {
        if (isMobileDropdownOpen) {
            closeMobileDropdown();
        } else {
            openMobileDropdown();
        }
    }

    // Open dropdown with smooth animation
    function openMobileDropdown() {
        mobileUserDropdown.classList.add('show');
        mobileUserMenuToggle.classList.add('active');
        isMobileDropdownOpen = true;
        
        // Add haptic feedback
        if ('vibrate' in navigator) {
            navigator.vibrate(10);
        }
    }

    // Close dropdown with smooth animation
    function closeMobileDropdown() {
        mobileUserDropdown.classList.remove('show');
        mobileUserMenuToggle.classList.remove('active');
        isMobileDropdownOpen = false;
    }

    // Event listeners
    mobileUserMenuToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        toggleMobileDropdown();
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (isMobileDropdownOpen && !mobileUserMenuToggle.contains(e.target) && !mobileUserDropdown.contains(e.target)) {
            closeMobileDropdown();
        }
    });

    // Close dropdown on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isMobileDropdownOpen) {
            closeMobileDropdown();
        }
    });

    // Close dropdown when clicking on dropdown items
    const mobileDropdownItems = document.querySelectorAll('.mobile-dropdown-item');
    mobileDropdownItems.forEach(item => {
        item.addEventListener('click', function() {
            setTimeout(() => {
                closeMobileDropdown();
            }, 150);
        });
    });

    // Add touch feedback for mobile user menu
    mobileUserMenuToggle.addEventListener('touchstart', function() {
        this.style.transform = 'scale(0.98)';
    });

    mobileUserMenuToggle.addEventListener('touchend', function() {
        this.style.transform = 'scale(1)';
    });

    mobileUserMenuToggle.addEventListener('touchcancel', function() {
        this.style.transform = 'scale(1)';
    });

    console.log('Mobile user menu dropdown initialized successfully');
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
    // Add mobile-specific booking enhancements
    const bookingCards = document.querySelectorAll('.booking-card');
    bookingCards.forEach(card => {
        // Add swipe gesture support
        addSwipeGestures(card);
        
        // Add touch feedback
        addTouchFeedback(card);
        
        // Add mobile-specific status indicators
        addMobileStatusIndicators(card);
        
        // Add quick booking actions
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
    
    // Add mobile booking tab enhancements
    initializeMobileBookingTabs();
    
    // Add mobile booking search/filter
    initializeMobileBookingSearch();
}

/**
 * Add swipe gestures to booking cards
 */
function addSwipeGestures(card) {
    let startX = 0;
    let startY = 0;
    let isSwiping = false;
    let currentX = 0;
    
    card.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        isSwiping = false;
        currentX = 0;
    });
    
    card.addEventListener('touchmove', function(e) {
        if (!startX || !startY) return;
        
        const deltaX = e.touches[0].clientX - startX;
        const deltaY = e.touches[0].clientY - startY;
        
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) {
            isSwiping = true;
            e.preventDefault();
            
            // Limit swipe distance
            const maxSwipe = 100;
            currentX = Math.max(-maxSwipe, Math.min(maxSwipe, deltaX));
            
            // Apply transform
            this.style.transform = `translateX(${currentX}px)`;
            
            // Show/hide swipe action
            const swipeAction = this.querySelector('.swipe-action');
            if (swipeAction) {
                if (currentX < -20) {
                    swipeAction.style.right = `${Math.abs(currentX)}px`;
                } else {
                    swipeAction.style.right = '-100px';
                }
            }
        }
    });
    
    card.addEventListener('touchend', function(e) {
        if (!isSwiping) return;
        
        // Snap back or complete swipe
        if (Math.abs(currentX) > 50) {
            // Complete swipe action
            if (currentX < 0) {
                // Swipe left - show quick actions
                this.classList.add('swiped');
                showMobileQuickActions(this);
            }
        } else {
            // Snap back
            this.style.transform = 'translateX(0)';
            const swipeAction = this.querySelector('.swipe-action');
            if (swipeAction) {
                swipeAction.style.right = '-100px';
            }
        }
        
        startX = 0;
        startY = 0;
        isSwiping = false;
        currentX = 0;
    });
}

/**
 * Add touch feedback to booking cards
 */
function addTouchFeedback(card) {
    card.addEventListener('touchstart', function() {
        this.style.transform = 'scale(0.98)';
        this.style.transition = 'transform 0.1s ease';
    });
    
    card.addEventListener('touchend', function() {
        this.style.transform = 'scale(1)';
        setTimeout(() => {
            this.style.transition = '';
        }, 100);
    });
    
    card.addEventListener('touchcancel', function() {
        this.style.transform = 'scale(1)';
        this.style.transition = '';
    });
}

/**
 * Add mobile status indicators
 */
function addMobileStatusIndicators(card) {
    const status = card.classList.contains('pending') ? 'pending' : 
                  card.classList.contains('confirmed') ? 'confirmed' : 'normal';
    
    // Add priority indicator
    const priority = document.createElement('div');
    priority.className = `booking-priority ${status}`;
    card.appendChild(priority);
    
    // Add status badge
    const statusBadge = document.createElement('span');
    statusBadge.className = `status-badge ${status}`;
    statusBadge.textContent = status.toUpperCase();
    
    const header = card.querySelector('.booking-header');
    if (header) {
        header.appendChild(statusBadge);
    }
}

/**
 * Show mobile quick actions
 */
function showMobileQuickActions(card) {
    const bookingId = card.dataset.bookingId;
    if (!bookingId) return;
    
    // Create mobile action sheet
    const actionSheet = document.createElement('div');
    actionSheet.className = 'mobile-action-sheet';
    actionSheet.innerHTML = `
        <div class="action-sheet-overlay" onclick="closeMobileActionSheet()"></div>
        <div class="action-sheet-content">
            <div class="action-sheet-header">
                <h3>Booking Actions</h3>
                <button onclick="closeMobileActionSheet()" class="action-sheet-close">×</button>
            </div>
            <div class="action-sheet-actions">
                <button class="action-sheet-btn primary" onclick="quickJoinMeeting('${bookingId}')">
                    <i class="fas fa-video"></i>
                    <span>Join Meeting</span>
                </button>
                <button class="action-sheet-btn" onclick="quickReschedule('${bookingId}')">
                    <i class="fas fa-calendar-alt"></i>
                    <span>Reschedule</span>
                </button>
                <button class="action-sheet-btn" onclick="quickMessage('${bookingId}')">
                    <i class="fas fa-comment"></i>
                    <span>Message</span>
                </button>
                <button class="action-sheet-btn danger" onclick="quickCancel('${bookingId}')">
                    <i class="fas fa-times"></i>
                    <span>Cancel</span>
                </button>
            </div>
        </div>
    `;
    
    // Add styles
    actionSheet.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        z-index: 10000;
        display: flex;
        align-items: flex-end;
    `;
    
    const overlay = actionSheet.querySelector('.action-sheet-overlay');
    overlay.style.cssText = `
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
    `;
    
    const content = actionSheet.querySelector('.action-sheet-content');
    content.style.cssText = `
        background: white;
        border-radius: 20px 20px 0 0;
        width: 100%;
        max-height: 50vh;
        animation: slideUp 0.3s ease;
    `;
    
    document.body.appendChild(actionSheet);
    
    // Add animation keyframes
    if (!document.querySelector('#mobile-action-sheet-styles')) {
        const style = document.createElement('style');
        style.id = 'mobile-action-sheet-styles';
        style.textContent = `
            @keyframes slideUp {
                from { transform: translateY(100%); }
                to { transform: translateY(0); }
            }
            .action-sheet-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 1rem;
                border-bottom: 1px solid #e5e7eb;
            }
            .action-sheet-actions {
                padding: 1rem;
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }
            .action-sheet-btn {
                display: flex;
                align-items: center;
                gap: 1rem;
                padding: 1rem;
                border: none;
                background: #f8f9fa;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 500;
                text-align: left;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .action-sheet-btn.primary {
                background: #10b981;
                color: white;
            }
            .action-sheet-btn.danger {
                background: #fee2e2;
                color: #dc2626;
            }
            .action-sheet-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * Close mobile action sheet
 */
function closeMobileActionSheet() {
    const actionSheet = document.querySelector('.mobile-action-sheet');
    if (actionSheet) {
        actionSheet.remove();
    }
}

/**
 * Initialize mobile booking tabs
 */
function initializeMobileBookingTabs() {
    const tabNav = document.querySelector('.tab-nav');
    if (!tabNav) return;
    
    // Add horizontal scroll behavior
    tabNav.addEventListener('scroll', function() {
        // Add scroll indicators
        const scrollLeft = this.scrollLeft;
        const scrollWidth = this.scrollWidth;
        const clientWidth = this.clientWidth;
        
        if (scrollLeft > 0) {
            this.classList.add('scrolled-left');
        } else {
            this.classList.remove('scrolled-left');
        }
        
        if (scrollLeft < scrollWidth - clientWidth) {
            this.classList.add('scrolled-right');
        } else {
            this.classList.remove('scrolled-right');
        }
    });
    
    // Add scroll indicators
    const leftIndicator = document.createElement('div');
    leftIndicator.className = 'scroll-indicator left';
    leftIndicator.innerHTML = '<i class="fas fa-chevron-left"></i>';
    leftIndicator.style.cssText = `
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    const rightIndicator = document.createElement('div');
    rightIndicator.className = 'scroll-indicator right';
    rightIndicator.innerHTML = '<i class="fas fa-chevron-right"></i>';
    rightIndicator.style.cssText = `
        position: absolute;
        right: 0;
        top: 50%;
        transform: translateY(-50%);
        background: rgba(255, 255, 255, 0.9);
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    tabNav.style.position = 'relative';
    tabNav.appendChild(leftIndicator);
    tabNav.appendChild(rightIndicator);
    
    // Show/hide indicators based on scroll position
    function updateScrollIndicators() {
        const scrollLeft = tabNav.scrollLeft;
        const scrollWidth = tabNav.scrollWidth;
        const clientWidth = tabNav.clientWidth;
        
        if (scrollLeft > 0) {
            leftIndicator.style.opacity = '1';
        } else {
            leftIndicator.style.opacity = '0';
        }
        
        if (scrollLeft < scrollWidth - clientWidth) {
            rightIndicator.style.opacity = '1';
        } else {
            rightIndicator.style.opacity = '0';
        }
    }
    
    // Update indicators on scroll
    tabNav.addEventListener('scroll', updateScrollIndicators);
    
    // Initial check
    updateScrollIndicators();
}

/**
 * Initialize mobile booking search
 */
function initializeMobileBookingSearch() {
    // Add search functionality for mobile
    const searchInput = document.createElement('input');
    searchInput.type = 'text';
    searchInput.placeholder = 'Search bookings...';
    searchInput.className = 'mobile-booking-search';
    searchInput.style.cssText = `
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        font-size: 16px;
        margin-bottom: 1rem;
        background: white;
    `;
    
    // Insert search input at the top of bookings content
    const bookingsContent = document.querySelector('#bookings-content');
    if (bookingsContent) {
        bookingsContent.insertBefore(searchInput, bookingsContent.firstChild);
    }
    
    // Add search functionality
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        const bookingCards = document.querySelectorAll('.booking-card');
        
        bookingCards.forEach(card => {
            const text = card.textContent.toLowerCase();
            if (text.includes(query)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
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
function quickBook(userId) {
    // Navigate to booking page
    window.location.href = `/book/${userId}`;
}

/**
 * Quick message function
 */
function quickMessage(userId) {
    // Navigate to messaging page
    window.location.href = `/message/${userId}`;
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

/**
 * Initialize mobile scroll behavior
 */
function initializeMobileScroll() {
    // Prevent horizontal scroll
    document.addEventListener('touchmove', function(e) {
        if (e.touches.length > 1) {
            e.preventDefault();
        }
    }, { passive: false });

    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add scroll-to-top functionality
    const scrollToTopBtn = document.createElement('button');
    scrollToTopBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollToTopBtn.className = 'scroll-to-top';
    scrollToTopBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #059669;
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
        display: none;
        cursor: pointer;
        font-size: 1.2rem;
    `;
    
    document.body.appendChild(scrollToTopBtn);
    
    // Show/hide scroll to top button
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollToTopBtn.style.display = 'block';
        } else {
            scrollToTopBtn.style.display = 'none';
        }
    });
    
    // Scroll to top functionality
    scrollToTopBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

/**
 * Initialize mobile viewport handling
 */
function initializeMobileViewport() {
    // Set viewport meta tag if not present
    let viewport = document.querySelector('meta[name="viewport"]');
    if (!viewport) {
        viewport = document.createElement('meta');
        viewport.name = 'viewport';
        viewport.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
        document.head.appendChild(viewport);
    }
    
    // Prevent zoom on double tap
    let lastTouchEnd = 0;
    document.addEventListener('touchend', function(e) {
        const now = (new Date()).getTime();
        if (now - lastTouchEnd <= 300) {
            e.preventDefault();
        }
        lastTouchEnd = now;
    }, false);
    
    // Handle orientation changes
    window.addEventListener('orientationchange', function() {
        setTimeout(function() {
            window.scrollTo(0, 0);
        }, 100);
    });
}

/**
 * Initialize mobile-specific form enhancements
 */
function initializeMobileFormEnhancements() {
    // Add input type detection for better mobile keyboards
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        if (input.type === 'text' && input.name.includes('email')) {
            input.type = 'email';
        }
        if (input.type === 'text' && input.name.includes('phone')) {
            input.type = 'tel';
        }
        if (input.type === 'text' && input.name.includes('url')) {
            input.type = 'url';
        }
    });
    
    // Add form validation feedback
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let hasErrors = false;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('error');
                    hasErrors = true;
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (hasErrors) {
                e.preventDefault();
                showMobileValidationMessage('Please fill in all required fields');
            }
        });
    });
}

/**
 * Initialize mobile-specific card enhancements
 */
function initializeMobileCardEnhancements() {
    // Add pull-to-refresh functionality
    let startY = 0;
    let currentY = 0;
    let isRefreshing = false;
    
    document.addEventListener('touchstart', function(e) {
        if (window.scrollY === 0) {
            startY = e.touches[0].clientY;
        }
    });
    
    document.addEventListener('touchmove', function(e) {
        if (window.scrollY === 0 && startY > 0) {
            currentY = e.touches[0].clientY;
            const pullDistance = currentY - startY;
            
            if (pullDistance > 0 && pullDistance < 100) {
                // Show pull-to-refresh indicator
                showPullToRefreshIndicator(pullDistance);
            }
        }
    });
    
    document.addEventListener('touchend', function(e) {
        if (window.scrollY === 0 && startY > 0) {
            const pullDistance = currentY - startY;
            
            if (pullDistance > 100 && !isRefreshing) {
                isRefreshing = true;
                refreshPage();
            }
            
            hidePullToRefreshIndicator();
            startY = 0;
            currentY = 0;
        }
    });
}

/**
 * Show pull-to-refresh indicator
 */
function showPullToRefreshIndicator(distance) {
    let indicator = document.getElementById('pull-to-refresh-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'pull-to-refresh-indicator';
        indicator.innerHTML = '<i class="fas fa-sync-alt"></i> Pull to refresh';
        indicator.style.cssText = `
            position: fixed;
            top: -50px;
            left: 50%;
            transform: translateX(-50%);
            background: #059669;
            color: white;
            padding: 10px 20px;
            border-radius: 20px;
            font-size: 14px;
            z-index: 1000;
            transition: all 0.3s ease;
        `;
        document.body.appendChild(indicator);
    }
    
    const progress = Math.min(distance / 100, 1);
    indicator.style.top = `${-50 + (distance * 0.5)}px`;
    indicator.style.opacity = progress;
}

/**
 * Hide pull-to-refresh indicator
 */
function hidePullToRefreshIndicator() {
    const indicator = document.getElementById('pull-to-refresh-indicator');
    if (indicator) {
        indicator.style.top = '-50px';
        indicator.style.opacity = '0';
    }
}

/**
 * Refresh page
 */
function refreshPage() {
    window.location.reload();
}

/**
 * Initialize mobile performance optimizations
 */
function initializeMobilePerformance() {
    // Lazy load images for better performance
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Debounce scroll events for better performance
    let scrollTimeout;
    window.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(function() {
            // Handle scroll-based functionality here
        }, 100);
    });

    // Optimize touch events
    document.addEventListener('touchstart', function() {}, { passive: true });
    document.addEventListener('touchmove', function() {}, { passive: true });
    document.addEventListener('touchend', function() {}, { passive: true });
}

/**
 * Initialize mobile accessibility enhancements
 */
function initializeMobileAccessibility() {
    // Add ARIA labels to interactive elements
    const buttons = document.querySelectorAll('button:not([aria-label])');
    buttons.forEach(button => {
        if (!button.getAttribute('aria-label') && button.textContent.trim()) {
            button.setAttribute('aria-label', button.textContent.trim());
        }
    });

    // Enhance focus management for mobile
    const focusableElements = document.querySelectorAll('a, button, input, textarea, select, [tabindex]');
    focusableElements.forEach(element => {
        element.addEventListener('focus', function() {
            this.style.outline = '2px solid #10b981';
            this.style.outlineOffset = '2px';
        });
        
        element.addEventListener('blur', function() {
            this.style.outline = '';
            this.style.outlineOffset = '';
        });
    });

    // Add skip links for better navigation
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.textContent = 'Skip to main content';
    skipLink.className = 'skip-link';
    skipLink.style.cssText = `
        position: absolute;
        top: -40px;
        left: 6px;
        background: #10b981;
        color: white;
        padding: 8px;
        text-decoration: none;
        z-index: 10000;
        border-radius: 4px;
    `;
    
    skipLink.addEventListener('focus', function() {
        this.style.top = '6px';
    });
    
    skipLink.addEventListener('blur', function() {
        this.style.top = '-40px';
    });
    
    document.body.insertBefore(skipLink, document.body.firstChild);

    // Add high contrast mode support
    if (window.matchMedia('(prefers-contrast: high)').matches) {
        document.body.classList.add('high-contrast');
    }

    // Add reduced motion support
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        document.body.classList.add('reduced-motion');
    }
}

/**
 * Initialize mobile-specific loading states
 */
function initializeMobileLoadingStates() {
    // Add loading states for better UX
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    });

    // Add skeleton loading for cards
    const cards = document.querySelectorAll('.user-card-enhanced, .booking-card');
    cards.forEach(card => {
        if (!card.querySelector('.card-content')) {
            card.classList.add('loading');
        }
    });
}

/**
 * Initialize mobile-specific error handling
 */
function initializeMobileErrorHandling() {
    // Global error handler for mobile
    window.addEventListener('error', function(e) {
        console.error('Mobile error:', e.error);
        
        // Show user-friendly error message
        const errorNotification = document.createElement('div');
        errorNotification.className = 'mobile-error-notification';
        errorNotification.innerHTML = `
            <div style="
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
            ">
                <i class="fas fa-exclamation-triangle"></i>
                Something went wrong. Please try again.
                <button onclick="this.parentElement.parentElement.remove()" style="
                    background: none;
                    border: none;
                    color: white;
                    float: right;
                    font-size: 1.2rem;
                    cursor: pointer;
                ">×</button>
            </div>
        `;
        
        document.body.appendChild(errorNotification);
        
        setTimeout(() => {
            if (errorNotification.parentElement) {
                errorNotification.remove();
            }
        }, 5000);
    });
}

// Export functions for global access
window.quickBook = quickBook;
window.quickMessage = quickMessage;
window.quickReschedule = quickReschedule;
window.quickCancel = quickCancel;
window.selectSuggestion = selectSuggestion;
window.closeMobileActionSheet = closeMobileActionSheet;
window.quickJoinMeeting = quickJoinMeeting;

/**
 * Quick join meeting function
 */
function quickJoinMeeting(bookingId) {
    window.location.href = `/join-meeting/${bookingId}`;
}
