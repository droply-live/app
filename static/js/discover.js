// Clean Discover Page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeDiscover();
});

function initializeDiscover() {
    // Add smooth animations to category cards
    const categoryCards = document.querySelectorAll('.category-card');
    categoryCards.forEach(card => {
        card.addEventListener('click', function(e) {
            // Add a subtle animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });

    // Add hover effects to expert cards
    const expertCards = document.querySelectorAll('.expert-card-enhanced');
    expertCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add loading states to action buttons
    const actionButtons = document.querySelectorAll('.action-btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Prevent event bubbling for buttons inside cards
            e.stopPropagation();
            
            // Add loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading">Loading...</span>';
            this.disabled = true;
            
            // Simulate loading (remove in production)
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 1000);
        });
    });

    // Add search input enhancements
    const searchInput = document.querySelector('.search-input-enhanced');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.parentElement.style.boxShadow = '0 6px 25px rgba(102, 126, 234, 0.15)';
        });
        
        searchInput.addEventListener('blur', function() {
            this.parentElement.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        });
    }

    // Add smooth animations for expert cards
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    expertCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Add loading spinner styles
const style = document.createElement('style');
style.textContent = `
    .loading {
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid #ffffff;
        border-radius: 50%;
        border-top-color: transparent;
        animation: spin 1s ease-in-out infinite;
        margin-right: 8px;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .expert-card-enhanced {
        transition: all 0.3s ease;
    }
    
    .category-card {
        transition: transform 0.15s ease;
    }
`;
document.head.appendChild(style); 