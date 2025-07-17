/**
 * Search functionality for Droply
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeSearchForm();
    initializeFilters();
    initializeResultsHandling();
    initializeCategoryBubbles();
});

/**
 * Initialize search form functionality
 */
function initializeSearchForm() {
    const searchForm = document.getElementById('searchForm');
    if (!searchForm) return;
    
    // Auto-submit form when filters change
    const filterInputs = searchForm.querySelectorAll('select, input[type="number"]');
    filterInputs.forEach(input => {
        input.addEventListener('change', function() {
            debounce(submitSearchForm, 500)();
        });
    });
    
    // Handle text search with debouncing
    const queryInput = searchForm.querySelector('input[name="query"]');
    if (queryInput) {
        queryInput.addEventListener('input', function() {
            debounce(submitSearchForm, 1000)();
        });
    }
    
    // Handle form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        submitSearchForm();
    });
}

/**
 * Submit search form with AJAX
 */
function submitSearchForm() {
    const form = document.getElementById('searchForm');
    if (!form) return;
    
    // Show loading state
    showLoadingState();
    
    // Get form data
    const formData = new FormData(form);
    const queryParams = new URLSearchParams();
    
    for (let [key, value] of formData.entries()) {
        if (value.trim() !== '') {
            queryParams.append(key, value);
        }
    }
    
    // Update URL without page reload
    const newUrl = `${window.location.pathname}?${queryParams.toString()}`;
    window.history.pushState({}, '', newUrl);
    
    // Make AJAX request
    fetch(newUrl)
        .then(response => response.text())
        .then(html => {
            // Parse the HTML response
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Extract the user cards section
            const newUserCards = doc.querySelector('.row.mt-4.g-4.justify-content-center');
            const currentUserCards = document.querySelector('.row.mt-4.g-4.justify-content-center');
            
            if (newUserCards && currentUserCards) {
                // Replace the content with smooth animation
                currentUserCards.style.opacity = '0';
                setTimeout(() => {
                    currentUserCards.innerHTML = newUserCards.innerHTML;
                    currentUserCards.style.opacity = '1';
                    
                    // Re-initialize feather icons
                    if (window.feather) {
                        feather.replace();
                    }
                    
                    // Hide loading state
                    hideLoadingState();
                }, 150);
            } else {
                // Fallback: reload the page
                window.location.href = newUrl;
            }
        })
        .catch(error => {
            console.error('Search error:', error);
            // Fallback: reload the page
            window.location.href = newUrl;
        });
}

/**
 * Initialize advanced filters
 */
function initializeFilters() {
    // Handle advanced filters toggle
    const advancedToggle = document.querySelector('[data-bs-toggle="collapse"]');
    if (advancedToggle) {
        const advancedFilters = document.getElementById('advancedFilters');
        
        advancedToggle.addEventListener('click', function() {
            const isExpanded = advancedFilters.classList.contains('show');
            
            // Update icon and text
            const icon = this.querySelector('i');
            if (icon && window.feather) {
                icon.setAttribute('data-feather', isExpanded ? 'sliders' : 'x');
                feather.replace();
            }
        });
    }
    
    // Rate range validation
    const minRateInput = document.querySelector('input[name="min_rate"]');
    const maxRateInput = document.querySelector('input[name="max_rate"]');
    
    if (minRateInput && maxRateInput) {
        function validateRateRange() {
            const minRate = parseFloat(minRateInput.value) || 0;
            const maxRate = parseFloat(maxRateInput.value) || Infinity;
            
            if (minRate > maxRate) {
                maxRateInput.setCustomValidity('Maximum rate must be greater than minimum rate');
                maxRateInput.classList.add('is-invalid');
                
                let errorDiv = maxRateInput.parentNode.querySelector('.invalid-feedback');
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.className = 'invalid-feedback';
                    maxRateInput.parentNode.appendChild(errorDiv);
                }
                errorDiv.textContent = 'Maximum rate must be greater than minimum rate';
            } else {
                maxRateInput.setCustomValidity('');
                maxRateInput.classList.remove('is-invalid');
                
                const errorDiv = maxRateInput.parentNode.querySelector('.invalid-feedback');
                if (errorDiv) {
                    errorDiv.remove();
                }
            }
        }
        
        minRateInput.addEventListener('change', validateRateRange);
        maxRateInput.addEventListener('change', validateRateRange);
    }
}

/**
 * Initialize results handling
 */
function initializeResultsHandling() {
    // Add smooth scroll to results
    const searchBtn = document.querySelector('button[type="submit"]');
    if (searchBtn) {
        searchBtn.addEventListener('click', function() {
            setTimeout(() => {
                const resultsSection = document.querySelector('.row .col-12 h5');
                if (resultsSection) {
                    resultsSection.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'start' 
                    });
                }
            }, 100);
        });
    }
    
    // Handle expert card interactions
    const expertCards = document.querySelectorAll('.expert-card');
    expertCards.forEach(card => {
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.classList.add('shadow-lg');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('shadow-lg');
        });
        
        // Track card clicks for analytics
        const viewButton = card.querySelector('.btn');
        if (viewButton) {
            viewButton.addEventListener('click', function() {
                const expertName = card.querySelector('.card-title').textContent;
                trackExpertView(expertName);
            });
        }
    });
}

/**
 * Show loading state
 */
function showLoadingState() {
    const searchBtn = document.querySelector('button[type="submit"]');
    if (searchBtn) {
        searchBtn.disabled = true;
        searchBtn.innerHTML = '<i data-feather="loader" class="me-2"></i>Searching...';
        
        // Add spinning animation
        const loader = searchBtn.querySelector('i');
        if (loader) {
            loader.style.animation = 'spin 1s linear infinite';
        }
        
        // Re-initialize feather icons
        if (window.feather) {
            feather.replace();
        }
    }
    
    // Add loading overlay to results area
    const resultsArea = document.querySelector('.row.mt-4.g-4.justify-content-center');
    if (resultsArea) {
        resultsArea.classList.add('search-loading');
    }
}

/**
 * Hide loading state
 */
function hideLoadingState() {
    const searchBtn = document.querySelector('button[type="submit"]');
    if (searchBtn) {
        searchBtn.disabled = false;
        searchBtn.innerHTML = '<i data-feather="search" class="me-2"></i>Search';
        
        // Remove spinning animation
        const loader = searchBtn.querySelector('i');
        if (loader) {
            loader.style.animation = '';
        }
        
        // Re-initialize feather icons
        if (window.feather) {
            feather.replace();
        }
    }
    
    // Remove loading overlay from results area
    const resultsArea = document.querySelector('.row.mt-4.g-4.justify-content-center');
    if (resultsArea) {
        resultsArea.classList.remove('search-loading');
    }
}

/**
 * Debounce function to limit API calls
 */
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

/**
 * Track expert profile views
 */
function trackExpertView(expertName) {
    // In a real implementation, this would send analytics data
    console.log('Expert profile viewed:', expertName);
    
    // Could send to Google Analytics, Mixpanel, etc.
    if (window.gtag) {
        gtag('event', 'expert_profile_view', {
            'expert_name': expertName,
            'page_title': document.title,
            'page_location': window.location.href
        });
    }
}

/**
 * Handle URL parameters on page load
 */
function handleUrlParameters() {
    const urlParams = new URLSearchParams(window.location.search);
    const form = document.getElementById('searchForm');
    
    if (!form) return;
    
    // Populate form with URL parameters
    urlParams.forEach((value, key) => {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            input.value = value;
        }
    });
    
    // Show advanced filters if advanced parameters are present
    const advancedParams = ['min_rate', 'max_rate'];
    const hasAdvancedParams = advancedParams.some(param => urlParams.has(param));
    
    if (hasAdvancedParams) {
        const advancedFilters = document.getElementById('advancedFilters');
        if (advancedFilters) {
            advancedFilters.classList.add('show');
        }
    }
}

/**
 * Save search preferences
 */
function saveSearchPreferences() {
    const form = document.getElementById('searchForm');
    if (!form) return;
    
    const formData = new FormData(form);
    const preferences = {};
    
    for (let [key, value] of formData.entries()) {
        if (value.trim() !== '') {
            preferences[key] = value;
        }
    }
    
    // Save to localStorage
    localStorage.setItem('droply_search_preferences', JSON.stringify(preferences));
}

/**
 * Load search preferences
 */
function loadSearchPreferences() {
    const saved = localStorage.getItem('droply_search_preferences');
    if (!saved) return;
    
    try {
        const preferences = JSON.parse(saved);
        const form = document.getElementById('searchForm');
        
        if (form && !window.location.search) {
            // Only load if there are no URL parameters
            Object.keys(preferences).forEach(key => {
                const input = form.querySelector(`[name="${key}"]`);
                if (input) {
                    input.value = preferences[key];
                }
            });
        }
    } catch (e) {
        console.error('Error loading search preferences:', e);
    }
}

/**
 * Initialize search suggestions
 */
function initializeSearchSuggestions() {
    const queryInput = document.querySelector('input[name="query"]');
    if (!queryInput) return;
    
    // Popular search terms
    const suggestions = [
        'Career coaching',
        'Leadership development',
        'Business mentoring',
        'Life coaching',
        'Financial planning',
        'Marketing strategy',
        'Tech consulting',
        'Fitness coaching',
        'Wellness mentoring'
    ];
    
    // Create suggestions dropdown
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions position-absolute bg-white border rounded shadow-sm';
    suggestionsContainer.style.display = 'none';
    suggestionsContainer.style.zIndex = '1000';
    suggestionsContainer.style.width = '100%';
    suggestionsContainer.style.maxHeight = '200px';
    suggestionsContainer.style.overflowY = 'auto';
    
    queryInput.parentNode.style.position = 'relative';
    queryInput.parentNode.appendChild(suggestionsContainer);
    
    // Show suggestions on focus
    queryInput.addEventListener('focus', function() {
        if (this.value.length < 2) {
            showPopularSuggestions();
        }
    });
    
    // Filter suggestions on input
    queryInput.addEventListener('input', function() {
        const query = this.value.toLowerCase();
        
        if (query.length < 2) {
            suggestionsContainer.style.display = 'none';
            return;
        }
        
        const filtered = suggestions.filter(s => 
            s.toLowerCase().includes(query)
        );
        
        if (filtered.length > 0) {
            showSuggestions(filtered);
        } else {
            suggestionsContainer.style.display = 'none';
        }
    });
    
    // Hide suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!queryInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
            suggestionsContainer.style.display = 'none';
        }
    });
    
    function showPopularSuggestions() {
        const popularSuggestions = suggestions.slice(0, 5);
        showSuggestions(popularSuggestions, 'Popular searches:');
    }
    
    function showSuggestions(items, title = null) {
        let html = '';
        
        if (title) {
            html += `<div class="suggestion-header p-2 bg-light small text-muted">${title}</div>`;
        }
        
        items.forEach(item => {
            html += `
                <div class="suggestion-item p-2 cursor-pointer hover:bg-light" data-suggestion="${item}">
                    <i data-feather="search" class="me-2" style="width: 14px; height: 14px;"></i>
                    ${item}
                </div>
            `;
        });
        
        suggestionsContainer.innerHTML = html;
        suggestionsContainer.style.display = 'block';
        
        // Re-initialize feather icons
        if (window.feather) {
            feather.replace();
        }
        
        // Add click handlers
        suggestionsContainer.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', function() {
                queryInput.value = this.getAttribute('data-suggestion');
                suggestionsContainer.style.display = 'none';
                submitSearchForm();
            });
            
            // Add hover effect
            item.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f8f9fa';
            });
            
            item.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });
    }
}

/**
 * Initialize category bubbles functionality
 */
function initializeCategoryBubbles() {
    const bubbles = document.querySelectorAll('.category-bubble');
    const searchInput = document.querySelector('input[name="query"]');
    
    if (!bubbles.length || !searchInput) return;
    
    // Initialize bubble states based on current search
    updateBubbleStates();
    
    // Handle bubble clicks
    bubbles.forEach(bubble => {
        bubble.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            const isActive = this.classList.contains('active');
            
            // If trying to activate and already have 3 active bubbles, show modern notification
            if (!isActive && getActiveBubbleCount() >= 3) {
                showModernNotification('You can select up to 3 categories at a time. Please deselect one first.', 'info');
                return;
            }
            
            // Toggle bubble state
            if (isActive) {
                this.classList.remove('active');
            } else {
                this.classList.add('active');
            }
            
            // Update search input based on active bubbles
            updateSearchFromBubbles();
            
            // Submit search
            submitSearchForm();
        });
    });
    
    // Handle search input changes to sync with bubbles
    searchInput.addEventListener('input', function() {
        updateBubbleStates();
    });
}

/**
 * Get the count of active bubbles
 */
function getActiveBubbleCount() {
    return document.querySelectorAll('.category-bubble.active').length;
}

/**
 * Update search input based on active bubbles
 */
function updateSearchFromBubbles() {
    const searchInput = document.querySelector('input[name="query"]');
    const activeBubbles = document.querySelectorAll('.category-bubble.active');
    
    if (!searchInput) return;
    
    // Get categories from active bubbles
    const categories = Array.from(activeBubbles).map(bubble => 
        bubble.getAttribute('data-category')
    );
    
    // Combine with existing search terms
    const existingQuery = searchInput.value.trim();
    const existingTerms = existingQuery ? existingQuery.split(',').map(t => t.trim()) : [];
    
    // Remove any existing category terms
    const categoryTerms = ['finance', 'technology', 'business', 'marketing', 'healthcare', 'education', 'consulting', 'creative', 'fitness'];
    const filteredTerms = existingTerms.filter(term => !categoryTerms.includes(term.toLowerCase()));
    
    // Add new category terms
    const allTerms = [...filteredTerms, ...categories];
    
    // Update search input
    searchInput.value = allTerms.join(', ');
}

/**
 * Update bubble states based on current search
 */
function updateBubbleStates() {
    const searchInput = document.querySelector('input[name="query"]');
    const bubbles = document.querySelectorAll('.category-bubble');
    
    if (!searchInput || !bubbles.length) return;
    
    const query = searchInput.value.toLowerCase();
    const categoryTerms = ['finance', 'technology', 'business', 'marketing', 'healthcare', 'education', 'consulting', 'creative', 'fitness'];
    
    bubbles.forEach(bubble => {
        const category = bubble.getAttribute('data-category');
        const isInQuery = categoryTerms.includes(category) && query.includes(category);
        
        if (isInQuery) {
            bubble.classList.add('active');
        } else {
            bubble.classList.remove('active');
        }
    });
}

/**
 * Show modern notification
 */
function showModernNotification(message, type = 'info') {
    // Remove any existing notifications
    const existingNotifications = document.querySelectorAll('.modern-notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `modern-notification modern-notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <path d="m9 12 2 2 4-4"></path>
                </svg>
            </div>
            <div class="notification-message">${message}</div>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        </div>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Auto remove after 4 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }
    }, 4000);
}

// Initialize all functionality
document.addEventListener('DOMContentLoaded', function() {
    handleUrlParameters();
    loadSearchPreferences();
    initializeSearchSuggestions();
    
    // Save preferences when form changes
    const form = document.getElementById('searchForm');
    if (form) {
        form.addEventListener('change', debounce(saveSearchPreferences, 1000));
    }
});

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
        // Refresh results if page has been hidden for more than 5 minutes
        const lastRefresh = sessionStorage.getItem('last_search_refresh');
        const now = Date.now();
        
        if (!lastRefresh || (now - parseInt(lastRefresh)) > 5 * 60 * 1000) {
            sessionStorage.setItem('last_search_refresh', now.toString());
            // Could refresh search results here
        }
    }
});
