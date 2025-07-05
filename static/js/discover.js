// Discover Page Interactive Features
document.addEventListener('DOMContentLoaded', function() {
    initializeDiscover();
    const carousel = document.querySelector('.profile-carousel-wrapper');
    if (!carousel) return;
    let scrollAmount = 1.2; // px per frame
    let direction = 1;
    let pause = false;
    let pauseTimeout = null;
    function autoScroll() {
        if (pause) return;
        carousel.scrollLeft += scrollAmount * direction;
        // Pause at ends
        if (carousel.scrollLeft + carousel.clientWidth >= carousel.scrollWidth - 2) {
            direction = -1;
            pause = true;
            pauseTimeout = setTimeout(() => { pause = false; }, 1200);
        } else if (carousel.scrollLeft <= 2) {
            direction = 1;
            pause = true;
            pauseTimeout = setTimeout(() => { pause = false; }, 1200);
        }
        requestAnimationFrame(autoScroll);
    }
    // Pause on user interaction
    carousel.addEventListener('mouseenter', () => { pause = true; });
    carousel.addEventListener('mouseleave', () => { pause = false; autoScroll(); });
    carousel.addEventListener('touchstart', () => { pause = true; });
    carousel.addEventListener('touchend', () => { pause = false; autoScroll(); });
    autoScroll();
});

function initializeDiscover() {
    // Initialize all interactive components
    initializeCategoryTabs();
    initializeFilterButtons();
    initializeViewToggle();
    initializeSearchSuggestions();
    initializeQuickActions();
    initializeLoadMore();
    initializeFAB();
    initializeAnimations();
}

// Category Tabs
function initializeCategoryTabs() {
    const tabItems = document.querySelectorAll('.tab-item');
    const profileCards = document.querySelectorAll('.profile-card-liquid');
    
    tabItems.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            tabItems.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            this.classList.add('active');
            
            const category = this.dataset.category;
            filterProfilesByCategory(category);
        });
    });
}

function filterProfilesByCategory(category) {
    const profileCards = document.querySelectorAll('.profile-card-liquid');
    
    profileCards.forEach(card => {
        const cardCategories = card.dataset.categories || '';
        const cardBio = card.dataset.bio || '';
        const cardTags = card.dataset.tags || '';
        
        if (category === 'all') {
            card.style.display = 'block';
            card.style.animation = 'fadeInUp 0.5s ease forwards';
        } else {
            // Check if category matches tags OR bio description
            const categoryMatches = cardCategories.includes(category) || 
                                   cardBio.includes(category) || 
                                   cardTags.includes(category);
            
            if (categoryMatches) {
                card.style.display = 'block';
                card.style.animation = 'fadeInUp 0.5s ease forwards';
            } else {
                card.style.display = 'none';
            }
        }
    });
    
    // Update empty state
    updateEmptyState();
}

// Filter Buttons
function initializeFilterButtons() {
    const filterBtns = document.querySelectorAll('.filter-btn');
    
    filterBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            filterBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const sortType = this.dataset.sort;
            sortProfiles(sortType);
        });
    });
}

function sortProfiles(sortType) {
    const profilesGrid = document.getElementById('profilesGrid');
    const profileCards = Array.from(profilesGrid.children);
    
    // Remove empty state if present
    const emptyState = profilesGrid.querySelector('.empty-state');
    if (emptyState) {
        emptyState.remove();
    }
    
    // Sort based on type
    switch(sortType) {
        case 'trending':
            profileCards.sort((a, b) => {
                const ratingA = parseFloat(a.querySelector('.rating-text')?.textContent || '4.5');
                const ratingB = parseFloat(b.querySelector('.rating-text')?.textContent || '4.5');
                return ratingB - ratingA;
            });
            break;
        case 'recent':
            // Simulate recent sorting (in real app, use actual timestamps)
            profileCards.sort(() => Math.random() - 0.5);
            break;
        case 'rating':
            profileCards.sort((a, b) => {
                const ratingA = parseFloat(a.querySelector('.rating-text')?.textContent || '4.5');
                const ratingB = parseFloat(b.querySelector('.rating-text')?.textContent || '4.5');
                return ratingB - ratingA;
            });
            break;
    }
    
    // Re-append sorted cards
    profileCards.forEach(card => {
        profilesGrid.appendChild(card);
    });
}

// View Toggle
function initializeViewToggle() {
    const viewBtns = document.querySelectorAll('.view-btn');
    const profilesGrid = document.getElementById('profilesGrid');
    
    viewBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            viewBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            
            const viewType = this.dataset.view;
            changeView(viewType);
        });
    });
}

function changeView(viewType) {
    const profilesGrid = document.getElementById('profilesGrid');
    
    if (viewType === 'list') {
        profilesGrid.style.gridTemplateColumns = '1fr';
        profilesGrid.classList.add('list-view');
    } else {
        profilesGrid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(280px, 1fr))';
        profilesGrid.classList.remove('list-view');
    }
}

// Search Suggestions
function initializeSearchSuggestions() {
    const searchInput = document.getElementById('smartSearch');
    const suggestionsContainer = document.getElementById('searchSuggestions');
    
    if (!searchInput || !suggestionsContainer) return;
    
    const suggestions = [
        'Tech mentors', 'Creative coaches', 'Business advisors',
        'Fitness trainers', 'Life coaches', 'Financial experts',
        'Marketing gurus', 'Design mentors', 'Startup advisors',
        'Programming', 'Design', 'Marketing', 'Finance', 'Health',
        'Education', 'Consulting', 'Coaching', 'Mentoring'
    ];
    
    // Real-time search as user types
    searchInput.addEventListener('input', function() {
        const query = this.value.toLowerCase().trim();
        
        // Show/hide suggestions
        if (query.length < 2) {
            suggestionsContainer.innerHTML = '';
            suggestionsContainer.style.display = 'none';
            // If search is cleared, show all profiles
            if (query.length === 0) {
                showAllProfiles();
            }
            return;
        }
        
        // Filter suggestions
        const filteredSuggestions = suggestions.filter(suggestion => 
            suggestion.toLowerCase().includes(query)
        );
        
        if (filteredSuggestions.length > 0) {
            displaySuggestions(filteredSuggestions, suggestionsContainer);
        } else {
            suggestionsContainer.style.display = 'none';
        }
        
        // Perform real-time search
        performSearch(query);
    });
    
    // Handle Enter key
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = this.value.toLowerCase().trim();
            if (query.length > 0) {
                performSearch(query);
                suggestionsContainer.style.display = 'none';
            }
        }
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
        }
    });
}

function displaySuggestions(suggestions, container) {
    container.innerHTML = '';
    container.style.display = 'block';
    
    suggestions.forEach(suggestion => {
        const div = document.createElement('div');
        div.className = 'suggestion-item';
        div.textContent = suggestion;
        div.addEventListener('click', () => {
            document.getElementById('smartSearch').value = suggestion;
            container.style.display = 'none';
            // Trigger search
            performSearch(suggestion);
        });
        container.appendChild(div);
    });
}

function performSearch(query) {
    console.log('Searching for:', query);
    const profileCards = document.querySelectorAll('.profile-card-liquid');
    const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 0);
    
    profileCards.forEach(card => {
        const searchData = card.dataset.search || '';
        const nameData = card.dataset.name || '';
        const bioData = card.dataset.bio || '';
        const tagsData = card.dataset.tags || '';
        
        // Check if any search term matches any part of the profile data
        const matches = searchTerms.some(term => 
            searchData.includes(term) || 
            nameData.includes(term) || 
            bioData.includes(term) || 
            tagsData.includes(term)
        );
        
        if (matches) {
            card.style.display = 'block';
            card.style.animation = 'fadeInUp 0.5s ease forwards';
        } else {
            card.style.display = 'none';
        }
    });
    
    updateEmptyState();
}

function showAllProfiles() {
    const profileCards = document.querySelectorAll('.profile-card-liquid');
    profileCards.forEach(card => {
        card.style.display = 'block';
        card.style.animation = 'fadeInUp 0.5s ease forwards';
    });
    updateEmptyState();
}

// Quick Actions
function initializeQuickActions() {
    const likeBtns = document.querySelectorAll('.like-btn');
    const messageBtns = document.querySelectorAll('.message-btn');
    
    likeBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const userId = this.dataset.userId;
            toggleLike(this, userId);
        });
    });
    
    messageBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const userId = this.dataset.userId;
            openMessage(userId);
        });
    });
}

function toggleLike(btn, userId) {
    const icon = btn.querySelector('i');
    
    if (btn.classList.contains('liked')) {
        btn.classList.remove('liked');
        icon.style.color = '#333';
        showNotification('Removed from favorites', 'info');
    } else {
        btn.classList.add('liked');
        icon.style.color = '#e91e63';
        btn.style.animation = 'heartBeat 0.5s ease';
        showNotification('Added to favorites!', 'success');
    }
    
    // Remove animation class after animation completes
    setTimeout(() => {
        btn.style.animation = '';
    }, 500);
}

function openMessage(userId) {
    showNotification('Message feature coming soon!', 'info');
}

// Load More
function initializeLoadMore() {
    const loadMoreBtn = document.getElementById('loadMoreBtn');
    
    if (!loadMoreBtn) return;
    
    loadMoreBtn.addEventListener('click', function() {
        const btnText = this.querySelector('.btn-text');
        const spinner = this.querySelector('.loading-spinner');
        
        // Show loading state
        btnText.style.display = 'none';
        spinner.style.display = 'flex';
        
        // Simulate loading
        setTimeout(() => {
            btnText.style.display = 'block';
            spinner.style.display = 'none';
            showNotification('More profiles loaded!', 'success');
        }, 2000);
    });
}

// Floating Action Button
function initializeFAB() {
    const fabMain = document.getElementById('fabMain');
    const fabOptions = document.querySelectorAll('.fab-option');
    
    if (!fabMain) return;
    
    fabMain.addEventListener('click', function() {
        this.classList.toggle('active');
    });
    
    fabOptions.forEach(option => {
        option.addEventListener('click', function() {
            const action = this.dataset.action;
            handleFABAction(action);
        });
    });
}

function handleFABAction(action) {
    switch(action) {
        case 'filter':
            showNotification('Advanced filters coming soon!', 'info');
            break;
        case 'favorites':
            showNotification('View your favorites!', 'info');
            break;
        case 'share':
            if (navigator.share) {
                navigator.share({
                    title: 'Discover Amazing People',
                    text: 'Check out this awesome platform for connecting with creators and mentors!',
                    url: window.location.href
                });
            } else {
                showNotification('Sharing feature not supported', 'warning');
            }
            break;
    }
}

// Animations
function initializeAnimations() {
    // Intersection Observer for fade-in animations
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
    
    // Observe profile cards
    const profileCards = document.querySelectorAll('.profile-card-liquid');
    profileCards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

// Utility Functions
function updateEmptyState() {
    const profilesGrid = document.getElementById('profilesGrid');
    const visibleCards = Array.from(profilesGrid.children).filter(card => 
        card.style.display !== 'none' && !card.classList.contains('empty-state')
    );
    
    if (visibleCards.length === 0) {
        // Remove existing empty state
        const existingEmpty = profilesGrid.querySelector('.empty-state');
        if (existingEmpty) {
            existingEmpty.remove();
        }
        
        // Add new empty state
        const emptyState = document.createElement('div');
        emptyState.className = 'empty-state';
        emptyState.innerHTML = `
            <div class="empty-icon">🔍</div>
            <h3>No creators found</h3>
            <p>Try adjusting your search or explore different categories</p>
            <button class="btn-liquid" onclick="resetFilters()">Show All</button>
        `;
        profilesGrid.appendChild(emptyState);
    }
}

function resetFilters() {
    // Reset category tabs
    const tabItems = document.querySelectorAll('.tab-item');
    tabItems.forEach(tab => tab.classList.remove('active'));
    tabItems[0].classList.add('active'); // "All" tab
    
    // Reset filter buttons
    const filterBtns = document.querySelectorAll('.filter-btn');
    filterBtns.forEach(btn => btn.classList.remove('active'));
    filterBtns[0].classList.add('active'); // "Trending" button
    
    // Show all profiles
    showAllProfiles();
    
    // Clear search
    const searchInput = document.getElementById('smartSearch');
    if (searchInput) {
        searchInput.value = '';
    }
    
    // Hide search suggestions
    const suggestionsContainer = document.getElementById('searchSuggestions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
    
    updateEmptyState();
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `modern-notification modern-notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">
                <i data-feather="${getNotificationIcon(type)}"></i>
            </div>
            <div class="notification-message">${message}</div>
            <button class="notification-close">
                <i data-feather="x"></i>
            </button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    // Auto hide after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
    
    // Close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.classList.remove('show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    });
    
    // Initialize Feather icons
    if (window.feather) {
        feather.replace();
    }
}

function getNotificationIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'warning': return 'alert-triangle';
        case 'error': return 'x-circle';
        default: return 'info';
    }
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes heartBeat {
        0% { transform: scale(1); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
    
    .suggestion-item {
        padding: 0.75rem 1rem;
        color: white;
        cursor: pointer;
        transition: background 0.2s ease;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .suggestion-item:hover {
        background: rgba(255, 255, 255, 0.1);
    }
    
    .suggestion-item:last-child {
        border-bottom: none;
    }
    
    .search-suggestions {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: var(--glass-bg);
        backdrop-filter: var(--glass-blur);
        border: 1px solid var(--glass-border);
        border-radius: 15px;
        margin-top: 0.5rem;
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        display: none;
    }
    
    .list-view .profile-card-liquid {
        display: flex;
        align-items: center;
        padding: 1rem;
    }
    
    .list-view .profile-image-container {
        width: 100px;
        height: 100px;
        flex-shrink: 0;
        margin-right: 1rem;
    }
    
    .list-view .profile-info {
        flex: 1;
        padding: 0;
    }
    
    .list-view .profile-footer {
        margin-top: 0.5rem;
    }
`;
document.head.appendChild(style); 