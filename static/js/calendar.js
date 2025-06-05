/**
 * Calendar functionality for Droply
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
    initializeViewSwitcher();
    initializeFormValidation();
});

/**
 * Initialize calendar functionality
 */
function initializeCalendar() {
    const calendarGrid = document.getElementById('calendarGrid');
    if (!calendarGrid) return;
    
    // Generate calendar for current month
    generateCalendarView();
    
    // Add month navigation if needed
    addMonthNavigation();
}

/**
 * Initialize view switcher between list and calendar views
 */
function initializeViewSwitcher() {
    const listViewBtn = document.getElementById('listView');
    const calendarViewBtn = document.getElementById('calendarView');
    const listContent = document.getElementById('listViewContent');
    const calendarContent = document.getElementById('calendarViewContent');
    
    if (!listViewBtn || !calendarViewBtn) return;
    
    listViewBtn.addEventListener('change', function() {
        if (this.checked) {
            listContent.style.display = 'block';
            calendarContent.style.display = 'none';
        }
    });
    
    calendarViewBtn.addEventListener('change', function() {
        if (this.checked) {
            listContent.style.display = 'none';
            calendarContent.style.display = 'block';
            generateCalendarView();
        }
    });
}

/**
 * Generate calendar view
 */
function generateCalendarView() {
    const calendarGrid = document.getElementById('calendarGrid');
    if (!calendarGrid) return;
    
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    
    // Clear existing content
    calendarGrid.innerHTML = '';
    
    // Add day headers
    const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayHeaders.forEach(day => {
        const header = document.createElement('div');
        header.className = 'calendar-header text-center fw-bold p-2 bg-light';
        header.textContent = day;
        calendarGrid.appendChild(header);
    });
    
    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    // Add empty cells for days before month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day other-month';
        const prevMonthDate = new Date(year, month, -startingDayOfWeek + i + 1);
        emptyDay.innerHTML = `<div class="calendar-date">${prevMonthDate.getDate()}</div>`;
        calendarGrid.appendChild(emptyDay);
    }
    
    // Add days of current month
    for (let day = 1; day <= daysInMonth; day++) {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        
        const currentDate = new Date(year, month, day);
        const isToday = currentDate.toDateString() === now.toDateString();
        
        if (isToday) {
            dayElement.classList.add('today');
        }
        
        dayElement.innerHTML = `
            <div class="calendar-date fw-bold">${day}</div>
            <div class="calendar-events" id="events-${year}-${month}-${day}"></div>
        `;
        
        // Add click handler for adding events
        dayElement.addEventListener('click', function() {
            openAddEventModal(currentDate);
        });
        
        calendarGrid.appendChild(dayElement);
    }
    
    // Load and display time slots
    loadTimeSlots();
}

/**
 * Load time slots from the server (simplified version)
 */
function loadTimeSlots() {
    // In a real implementation, this would fetch time slots from the server
    // For now, we'll use the data already available in the list view
    const timeSlotCards = document.querySelectorAll('.time-slot-card');
    
    timeSlotCards.forEach(card => {
        const dateText = card.querySelector('small:nth-child(1)').textContent;
        const titleText = card.querySelector('h6').textContent;
        const isAvailable = card.querySelector('.badge-success');
        
        // Extract date and add to calendar
        // This is a simplified version - in production, you'd parse the actual date
        addEventToCalendar(dateText, titleText, isAvailable);
    });
}

/**
 * Add event to calendar
 */
function addEventToCalendar(dateStr, title, isAvailable) {
    // Simplified implementation
    // In production, you'd properly parse dates and add events
    console.log('Adding event to calendar:', { dateStr, title, isAvailable });
}

/**
 * Open add event modal with pre-filled date
 */
function openAddEventModal(date) {
    const modal = document.getElementById('addSlotModal');
    if (!modal) return;
    
    // Pre-fill date fields if they exist
    const startDateInput = document.querySelector('input[name="start_datetime"]');
    const endDateInput = document.querySelector('input[name="end_datetime"]');
    
    if (startDateInput && endDateInput) {
        const dateStr = date.toISOString().slice(0, 16);
        startDateInput.value = dateStr;
        
        // Set end time to 1 hour later
        const endDate = new Date(date);
        endDate.setHours(endDate.getHours() + 1);
        endDateInput.value = endDate.toISOString().slice(0, 16);
    }
    
    // Show modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

/**
 * Add month navigation
 */
function addMonthNavigation() {
    const calendarGrid = document.getElementById('calendarGrid');
    if (!calendarGrid) return;
    
    // Create navigation controls
    const nav = document.createElement('div');
    nav.className = 'calendar-nav d-flex justify-content-between align-items-center mb-3';
    nav.innerHTML = `
        <button class="btn btn-outline-secondary" id="prevMonth">
            <i data-feather="chevron-left"></i> Previous
        </button>
        <h5 class="mb-0" id="currentMonth"></h5>
        <button class="btn btn-outline-secondary" id="nextMonth">
            Next <i data-feather="chevron-right"></i>
        </button>
    `;
    
    // Insert before calendar grid
    calendarGrid.parentNode.insertBefore(nav, calendarGrid);
    
    // Update month display
    updateMonthDisplay();
    
    // Add event listeners
    document.getElementById('prevMonth').addEventListener('click', function() {
        changeMonth(-1);
    });
    
    document.getElementById('nextMonth').addEventListener('click', function() {
        changeMonth(1);
    });
    
    // Re-initialize feather icons
    if (window.feather) {
        feather.replace();
    }
}

let currentDate = new Date();

/**
 * Change month
 */
function changeMonth(delta) {
    currentDate.setMonth(currentDate.getMonth() + delta);
    generateCalendarView();
    updateMonthDisplay();
}

/**
 * Update month display
 */
function updateMonthDisplay() {
    const monthElement = document.getElementById('currentMonth');
    if (monthElement) {
        const options = { year: 'numeric', month: 'long' };
        monthElement.textContent = currentDate.toLocaleDateString('en-US', options);
    }
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    const form = document.querySelector('#addSlotModal form');
    if (!form) return;
    
    const startDateInput = form.querySelector('input[name="start_datetime"]');
    const endDateInput = form.querySelector('input[name="end_datetime"]');
    
    if (startDateInput && endDateInput) {
        // Validate that end time is after start time
        function validateTimes() {
            const startTime = new Date(startDateInput.value);
            const endTime = new Date(endDateInput.value);
            
            if (startTime && endTime && endTime <= startTime) {
                endDateInput.setCustomValidity('End time must be after start time');
                endDateInput.classList.add('is-invalid');
                
                // Show error message
                let errorDiv = endDateInput.parentNode.querySelector('.invalid-feedback');
                if (!errorDiv) {
                    errorDiv = document.createElement('div');
                    errorDiv.className = 'invalid-feedback';
                    endDateInput.parentNode.appendChild(errorDiv);
                }
                errorDiv.textContent = 'End time must be after start time';
            } else {
                endDateInput.setCustomValidity('');
                endDateInput.classList.remove('is-invalid');
                
                const errorDiv = endDateInput.parentNode.querySelector('.invalid-feedback');
                if (errorDiv) {
                    errorDiv.remove();
                }
            }
        }
        
        startDateInput.addEventListener('change', validateTimes);
        endDateInput.addEventListener('change', validateTimes);
        
        // Auto-set end time when start time changes
        startDateInput.addEventListener('change', function() {
            if (this.value && !endDateInput.value) {
                const startTime = new Date(this.value);
                startTime.setHours(startTime.getHours() + 1);
                endDateInput.value = startTime.toISOString().slice(0, 16);
            }
        });
    }
    
    // Form submission handling
    form.addEventListener('submit', function(e) {
        // Add loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i data-feather="loader" class="me-2"></i>Adding...';
            
            // Re-initialize feather icons
            if (window.feather) {
                feather.replace();
            }
        }
    });
}

/**
 * Utility function to format date for display
 */
function formatDate(date) {
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return date.toLocaleDateString('en-US', options);
}

/**
 * Utility function to format time range
 */
function formatTimeRange(startDate, endDate) {
    const options = { hour: '2-digit', minute: '2-digit' };
    const start = startDate.toLocaleTimeString('en-US', options);
    const end = endDate.toLocaleTimeString('en-US', options);
    return `${start} - ${end}`;
}

/**
 * Handle time slot card interactions
 */
document.addEventListener('click', function(e) {
    // Handle dropdown menu actions
    if (e.target.closest('.dropdown-menu .dropdown-item')) {
        const item = e.target.closest('.dropdown-item');
        const action = item.textContent.trim().toLowerCase();
        
        if (action.includes('edit')) {
            handleEditTimeSlot(e);
        } else if (action.includes('delete')) {
            handleDeleteTimeSlot(e);
        }
    }
});

/**
 * Handle edit time slot
 */
function handleEditTimeSlot(e) {
    e.preventDefault();
    
    // In a real implementation, this would populate the modal with existing data
    const modal = document.getElementById('addSlotModal');
    if (modal) {
        const bootstrapModal = new bootstrap.Modal(modal);
        bootstrapModal.show();
    }
}

/**
 * Handle delete time slot
 */
function handleDeleteTimeSlot(e) {
    e.preventDefault();
    
    if (confirm('Are you sure you want to delete this time slot?')) {
        // In a real implementation, this would make an AJAX request to delete
        console.log('Deleting time slot...');
        
        // Remove the card from the UI
        const card = e.target.closest('.time-slot-card');
        if (card) {
            card.style.transition = 'all 0.3s ease';
            card.style.opacity = '0';
            card.style.transform = 'translateX(-100%)';
            
            setTimeout(() => {
                card.remove();
            }, 300);
        }
    }
}

/**
 * Auto-refresh functionality
 */
function initializeAutoRefresh() {
    // Refresh calendar data every 5 minutes
    setInterval(function() {
        if (document.getElementById('calendarViewContent').style.display !== 'none') {
            loadTimeSlots();
        }
    }, 5 * 60 * 1000);
}

// Initialize auto-refresh
initializeAutoRefresh();
