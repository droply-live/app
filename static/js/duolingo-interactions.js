/**
 * Duolingo-Style Button Interactions
 * Adds playful micro-interactions to enhance user engagement
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeDuolingoButtons();
});

function initializeDuolingoButtons() {
    const buttons = document.querySelectorAll('.duolingo-action');
    
    buttons.forEach(button => {
        // Add click animation
        button.addEventListener('click', function(e) {
            // Add bounce animation
            this.classList.add('animate-bounce');
            
            // Remove animation class after animation completes
            setTimeout(() => {
                this.classList.remove('animate-bounce');
            }, 1000);
        });
        
        // Add subtle hover feedback without zoom
        button.addEventListener('mouseenter', function() {
            // Just let the CSS color change handle hover
            // No transform needed
        });
        
        button.addEventListener('mouseleave', function() {
            // Reset any transforms
            this.style.transform = '';
        });
        
        // Add touch feedback for mobile devices - maintain robust tactile press effect
        button.addEventListener('touchstart', function() {
            // Let CSS handle the full tactile press effect
            // No additional transforms needed
        });
        
        button.addEventListener('touchend', function() {
            // Reset to normal state
            this.style.transform = '';
        });
        
        // Add success animation for specific actions
        if (button.classList.contains('find')) {
            button.addEventListener('click', function() {
                // Add success animation for finding experts
                setTimeout(() => {
                    this.classList.add('success');
                    setTimeout(() => {
                        this.classList.remove('success');
                    }, 600);
                }, 200);
            });
        }
    });
    
    // Add swipe gesture support for mobile
    addSwipeSupport();
}

/**
 * Add swipe gesture support for mobile devices
 */
function addSwipeSupport() {
    const container = document.querySelector('.duolingo-quick-actions');
    if (!container) return;
    
    let startX = 0;
    let startY = 0;
    let isScrolling = false;
    
    container.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
        isScrolling = false;
    });
    
    container.addEventListener('touchmove', function(e) {
        if (!isScrolling) {
            const deltaX = Math.abs(e.touches[0].clientX - startX);
            const deltaY = Math.abs(e.touches[0].clientY - startY);
            
            if (deltaX > deltaY) {
                isScrolling = true;
            }
        }
    });
    
    container.addEventListener('touchend', function(e) {
        if (isScrolling) {
            // Add momentum scrolling effect
            this.style.scrollBehavior = 'smooth';
            setTimeout(() => {
                this.style.scrollBehavior = 'auto';
            }, 300);
        }
    });
}

/**
 * Add loading state to a button
 * @param {HTMLElement} button - The button element
 */
function setButtonLoading(button) {
    button.classList.add('loading');
    button.style.pointerEvents = 'none';
}

/**
 * Remove loading state from a button
 * @param {HTMLElement} button - The button element
 */
function removeButtonLoading(button) {
    button.classList.remove('loading');
    button.style.pointerEvents = '';
}

/**
 * Add success animation to a button
 * @param {HTMLElement} button - The button element
 */
function animateButtonSuccess(button) {
    button.classList.add('success');
    setTimeout(() => {
        button.classList.remove('success');
    }, 600);
}

/**
 * Add celebration effect for completed actions
 * @param {HTMLElement} button - The button element
 */
function celebrateButton(button) {
    // Create confetti effect
    createConfettiEffect(button);
    
    // Add success animation
    animateButtonSuccess(button);
}

/**
 * Create a simple confetti effect
 * @param {HTMLElement} element - The element to create confetti around
 */
function createConfettiEffect(element) {
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    // Create confetti particles
    for (let i = 0; i < 12; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'fixed';
        confetti.style.left = centerX + 'px';
        confetti.style.top = centerY + 'px';
        confetti.style.width = '6px';
        confetti.style.height = '6px';
        confetti.style.backgroundColor = getRandomColor();
        confetti.style.borderRadius = '50%';
        confetti.style.pointerEvents = 'none';
        confetti.style.zIndex = '9999';
        
        document.body.appendChild(confetti);
        
        // Animate confetti
        const angle = (i / 12) * 360;
        const velocity = 50 + Math.random() * 50;
        const vx = Math.cos(angle * Math.PI / 180) * velocity;
        const vy = Math.sin(angle * Math.PI / 180) * velocity;
        
        confetti.animate([
            { transform: 'translate(0, 0) scale(1)', opacity: 1 },
            { transform: `translate(${vx}px, ${vy}px) scale(0)`, opacity: 0 }
        ], {
            duration: 1000,
            easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)'
        }).onfinish = () => {
            confetti.remove();
        };
    }
}

/**
 * Get a random bright color for confetti
 * @returns {string} A random bright color
 */
function getRandomColor() {
    const colors = [
        '#58cc02', '#1cb0f6', '#ff9600', '#ce82ff', '#ff4b4b',
        '#ff6b6b', '#4bb500', '#0ea5e9', '#ff8c00', '#b366ff'
    ];
    return colors[Math.floor(Math.random() * colors.length)];
}

/**
 * Add progress indication to buttons
 * @param {HTMLElement} button - The button element
 * @param {number} progress - Progress value (0-100)
 */
function setButtonProgress(button, progress) {
    // Remove existing progress indicator
    const existingProgress = button.querySelector('.progress-indicator');
    if (existingProgress) {
        existingProgress.remove();
    }
    
    // Create progress indicator
    const progressIndicator = document.createElement('div');
    progressIndicator.className = 'progress-indicator';
    progressIndicator.style.cssText = `
        position: absolute;
        bottom: 0;
        left: 0;
        height: 3px;
        width: ${progress}%;
        background: rgba(255, 255, 255, 0.8);
        border-radius: 0 0 16px 16px;
        transition: width 0.3s ease;
    `;
    
    button.style.position = 'relative';
    button.appendChild(progressIndicator);
}

/**
 * Remove progress indication from button
 * @param {HTMLElement} button - The button element
 */
function removeButtonProgress(button) {
    const progressIndicator = button.querySelector('.progress-indicator');
    if (progressIndicator) {
        progressIndicator.remove();
    }
}

// Export functions for use in other scripts
window.DuolingoButtons = {
    setButtonLoading,
    removeButtonLoading,
    animateButtonSuccess,
    celebrateButton,
    setButtonProgress,
    removeButtonProgress
};
