/**
 * Search functionality for Droply
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeSearchForm();
    initializeFilters();
    initializeResultsHandling();
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
    
    // In a real implementation, this would make an AJAX request
    // For now, we'll just reload the page
    window.location.href = newUrl;
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
    const resultsArea = document.querySelector('.row .col-12');
    if (resultsArea) {
        resultsArea.style.opacity = '0.6';
        resultsArea.style.pointerEvents = 'none';
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
        
        if (window.feather) {
            feather.replace();
        }
    }
    
    // Remove loading overlay
    const resultsArea = document.querySelector('.row .col-12');
    if (resultsArea) {
        resultsArea.style.opacity = '1';
        resultsArea.style.pointerEvents = 'auto';
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
 * Handle filter presets
 */
function initializeFilterPresets() {
    const presets = {
        'coaches': {
            profession: 'coach',
            industry: '',
            location_type: ''
        },
        'mentors': {
            profession: 'mentor',
            industry: '',
            location_type: ''
        },
        'remote': {
            profession: '',
            industry: '',
            location_type: 'remote'
        },
        'local': {
            profession: '',
            industry: '',
            location_type: 'in_person'
        }
    };
    
    // Add preset buttons
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        const presetContainer = document.createElement('div');
        presetContainer.className = 'preset-filters mb-3';
        presetContainer.innerHTML = `
            <small class="text-muted d-block mb-2">Quick Filters:</small>
            <div class="btn-group" role="group">
                <button type="button" class="btn btn-outline-secondary btn-sm" data-preset="coaches">Coaches</button>
                <button type="button" class="btn btn-outline-secondary btn-sm" data-preset="mentors">Mentors</button>
                <button type="button" class="btn btn-outline-secondary btn-sm" data-preset="remote">Remote Only</button>
                <button type="button" class="btn btn-outline-secondary btn-sm" data-preset="local">Local Only</button>
            </div>
        `;
        
        searchForm.insertBefore(presetContainer, searchForm.firstChild);
        
        // Add click handlers for presets
        presetContainer.addEventListener('click', function(e) {
            if (e.target.hasAttribute('data-preset')) {
                const preset = e.target.getAttribute('data-preset');
                applyFilterPreset(presets[preset]);
                
                // Update active button
                presetContainer.querySelectorAll('.btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                e.target.classList.add('active');
            }
        });
    }
}

/**
 * Apply filter preset
 */
function applyFilterPreset(preset) {
    const form = document.getElementById('searchForm');
    if (!form) return;
    
    // Apply preset values
    Object.keys(preset).forEach(key => {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            input.value = preset[key];
        }
    });
    
    // Trigger search
    submitSearchForm();
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

// Initialize all functionality
document.addEventListener('DOMContentLoaded', function() {
    handleUrlParameters();
    loadSearchPreferences();
    initializeFilterPresets();
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
