/**
 * Modern Calendar functionality for Droply
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeCalendar();
    initializeViewSwitcher();
    initializeFormValidation();
    // Add listeners for auto-update
    document.getElementById('defaultDuration').addEventListener('change', function() {
        updateTimeSlotRules();
        generateCalendarView();
    });
    document.getElementById('workingHoursStart').addEventListener('change', function() {
        updateTimeSlotRules();
        generateCalendarView();
    });
    document.getElementById('workingHoursEnd').addEventListener('change', function() {
        updateTimeSlotRules();
        generateCalendarView();
    });
    document.getElementById('lockWeekends').addEventListener('change', function() {
        timeSlotRules.lockWeekends = this.checked;
        generateCalendarView();
    });
});

// Global state for time slot rules
const timeSlotRules = {
    defaultDuration: 30, // minutes
    workingHours: {
        start: 9, // 9 AM
        end: 17,  // 5 PM
    },
    daysOff: [], // Array of dates that are blocked
    customRules: {}, // Specific rules for certain dates
    lockWeekends: false, // Whether weekends should be locked
    lockedDays: {} // Track locked days by date key
};

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
    
    // Create date at noon to avoid timezone issues
    const now = new Date();
    now.setHours(12, 0, 0, 0);
    const year = now.getFullYear();
    const month = now.getMonth();
    
    calendarGrid.innerHTML = '';
    calendarGrid.className = 'calendar-grid';
    
    // Add day headers - starting with Monday (1) to Sunday (0)
    const dayHeaders = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    dayHeaders.forEach(day => {
        const header = document.createElement('div');
        header.className = 'calendar-header';
        header.textContent = day;
        calendarGrid.appendChild(header);
    });
    
    const firstDay = new Date(year, month, 1, 12, 0, 0, 0);
    const lastDay = new Date(year, month + 1, 0, 12, 0, 0, 0);
    const daysInMonth = lastDay.getDate();
    // Adjust starting day to match our new header order (Monday = 0, Sunday = 6)
    let startingDayOfWeek = (firstDay.getDay() + 6) % 7;
    
    // Add empty cells for days before month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
        const emptyDay = document.createElement('div');
        emptyDay.className = 'calendar-day other-month';
        calendarGrid.appendChild(emptyDay);
    }
    
    // Add days of current month
    for (let day = 1; day <= daysInMonth; day++) {
        const currentDate = new Date(year, month, day, 12, 0, 0, 0);
        
        // Skip past days completely
        if (currentDate < new Date(now.getFullYear(), now.getMonth(), now.getDate(), 12, 0, 0, 0)) {
            continue;
        }
        
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day';
        
        const isToday = currentDate.toDateString() === now.toDateString();
        
        if (isToday) {
            dayElement.classList.add('today');
        }
        
        // Check if day has custom rules
        const dateKey = currentDate.toISOString().split('T')[0];
        const hasCustomRules = timeSlotRules.customRules[dateKey];
        
        dayElement.innerHTML = `
            <div class="calendar-date">${day}</div>
            <div class="calendar-time-slots" id="slots-${dateKey}"></div>
        `;
        
        // Add click handler for day customization
        dayElement.addEventListener('click', function() {
            openDayCustomizationModal(currentDate);
        });
        
        calendarGrid.appendChild(dayElement);
        
        // Generate time slots for this day
        generateTimeSlotsForDay(currentDate, hasCustomRules);
    }
}

function generateTimeSlotsForDay(date, customRules) {
    const dateKey = date.toISOString().split('T')[0];
    const slotsContainer = document.getElementById(`slots-${dateKey}`);
    if (!slotsContainer) return;
    
    // Check if it's a weekend (0 = Sunday, 6 = Saturday)
    const isWeekend = date.getDay() === 0 || date.getDay() === 6;
    
    // If day is explicitly locked or it's a weekend with weekend locking enabled (and not in custom rules), don't generate slots
    if (timeSlotRules.lockedDays[dateKey] || (isWeekend && timeSlotRules.lockWeekends && !timeSlotRules.customRules[dateKey])) {
        return;
    }
    
    const rules = customRules || timeSlotRules;
    const startHour = rules.workingHours.start;
    const endHour = rules.workingHours.end;
    const duration = rules.defaultDuration;
    
    for (let hour = startHour; hour < endHour; hour += duration / 60) {
        const slot = document.createElement('div');
        slot.className = 'time-slot';
        slot.innerHTML = `
            <div class="time-slot-time">
                ${formatTime(hour)} - ${formatTime(hour + duration / 60)}
            </div>
        `;
        slotsContainer.appendChild(slot);
    }
}

function formatTime(hour) {
    const h = Math.floor(hour);
    const m = Math.round((hour - h) * 60);
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}`;
}

function openDayCustomizationModal(date) {
    // Ensure date is at noon to avoid timezone issues
    date.setHours(12, 0, 0, 0);
    const dateKey = date.toISOString().split('T')[0];
    const modal = new bootstrap.Modal(document.getElementById('dayCustomizationModal'));
    
    // Check if it's a weekend (0 = Sunday, 6 = Saturday)
    const isWeekend = date.getDay() === 0 || date.getDay() === 6;
    
    // Populate modal with current rules
    const currentRules = timeSlotRules.customRules[dateKey] || timeSlotRules;
    document.getElementById('customStartTime').value = `${currentRules.workingHours.start.toString().padStart(2, '0')}:00`;
    document.getElementById('customEndTime').value = `${currentRules.workingHours.end.toString().padStart(2, '0')}:00`;
    document.getElementById('customDuration').value = currentRules.defaultDuration;
    
    // Set lock checkbox state
    const lockCheckbox = document.getElementById('customLockDay');
    // For weekends, check if either explicitly locked or weekend locking is enabled
    const isLocked = timeSlotRules.lockedDays[dateKey] || (isWeekend && timeSlotRules.lockWeekends);
    lockCheckbox.checked = isLocked;
    
    // Disable time inputs if day is locked
    const timeInputs = document.querySelectorAll('#customStartTime, #customEndTime, #customDuration');
    timeInputs.forEach(input => {
        input.disabled = isLocked;
    });
    
    // Add change handler for lock checkbox
    lockCheckbox.onchange = function() {
        timeInputs.forEach(input => {
            input.disabled = this.checked;
        });
    };
    
    // Save button handler
    document.getElementById('saveCustomRules').onclick = function() {
        const isLocked = document.getElementById('customLockDay').checked;
        
        if (isLocked) {
            // If day is locked, remove any custom rules and mark as locked
            delete timeSlotRules.customRules[dateKey];
            timeSlotRules.lockedDays[dateKey] = true;
        } else {
            // If day is unlocked, save custom rules and remove from locked days
            const newRules = {
                workingHours: {
                    start: parseInt(document.getElementById('customStartTime').value.split(':')[0]),
                    end: parseInt(document.getElementById('customEndTime').value.split(':')[0])
                },
                defaultDuration: parseInt(document.getElementById('customDuration').value)
            };
            
            timeSlotRules.customRules[dateKey] = newRules;
            delete timeSlotRules.lockedDays[dateKey];
            
            // If it's a weekend and weekend locking is enabled, we need to remove it from the weekend lock
            if (isWeekend && timeSlotRules.lockWeekends) {
                // Add to custom rules to prevent it from being re-locked
                timeSlotRules.customRules[dateKey] = newRules;
            }
        }
        
        generateCalendarView();
        modal.hide();
    };
    
    modal.show();
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

function updateTimeSlotRules() {
    timeSlotRules.defaultDuration = parseInt(document.getElementById('defaultDuration').value);
    timeSlotRules.workingHours.start = parseInt(document.getElementById('workingHoursStart').value.split(':')[0]);
    timeSlotRules.workingHours.end = parseInt(document.getElementById('workingHoursEnd').value.split(':')[0]);
    timeSlotRules.lockWeekends = document.getElementById('lockWeekends').checked;
    
    // Update locked days when weekend locking changes
    if (timeSlotRules.lockWeekends) {
        const now = new Date();
        const year = now.getFullYear();
        const month = now.getMonth();
        const daysInMonth = new Date(year, month + 1, 0).getDate();
        
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const isWeekend = date.getDay() === 0 || date.getDay() === 6;
            const dateKey = date.toISOString().split('T')[0];
            
            // Only lock weekends that aren't in custom rules
            if (isWeekend && !timeSlotRules.customRules[dateKey]) {
                timeSlotRules.lockedDays[dateKey] = true;
            }
        }
    } else {
        // Remove weekend locks when weekend locking is disabled
        Object.keys(timeSlotRules.lockedDays).forEach(dateKey => {
            const date = new Date(dateKey);
            const isWeekend = date.getDay() === 0 || date.getDay() === 6;
            if (isWeekend) {
                delete timeSlotRules.lockedDays[dateKey];
            }
        });
    }
}

// Stepper/tab logic for homepage hero section 2 with timer bar

document.addEventListener('DOMContentLoaded', function() {
    function setupStepperTabs() {
        const stepTabs = document.querySelectorAll('.stepper-tab');
        const stepImage = document.getElementById('step-image');
        const stepImages = [
            '/static/img/mockup-hero.png',
            '/static/img/mockup-hero-2.png',
            '/static/img/generated-icon.png',
            '/static/img/default-avatar.png',
            '/static/img/mockup-hero.png'
        ];
        let timer = null;
        let currentIdx = 0;
        const TIMER_DURATION = 5000;

        function activateStep(idx, userClick=false) {
            stepTabs.forEach((t, i) => {
                t.classList.toggle('active', i === idx);
                // Reset timer bar animation
                const bar = t.querySelector('.step-timer-bar');
                if (bar) {
                    bar.style.animation = 'none';
                    bar.offsetHeight; // force reflow
                    if (i === idx) {
                        bar.style.animation = `timerBarGrow ${TIMER_DURATION}ms linear forwards`;
                    } else {
                        bar.style.animation = '';
                    }
                }
            });
            // Instantly switch image, no animation
            stepImage.src = stepImages[idx];
            currentIdx = idx;
            if (timer) clearTimeout(timer);
            timer = setTimeout(() => {
                let nextIdx = (currentIdx + 1) % stepTabs.length;
                activateStep(nextIdx);
            }, TIMER_DURATION);
        }

        if (stepTabs.length && stepImage) {
            stepTabs.forEach((tab, idx) => {
                tab.onclick = function() {
                    activateStep(idx, true);
                };
            });
            activateStep(0);
        }
    }
    setupStepperTabs();
});
