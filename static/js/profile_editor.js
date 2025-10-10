// Profile Editor JavaScript - Enhanced Live Preview and Form Handling

document.addEventListener('DOMContentLoaded', function() {
    let currentTab = 'basic';
    let currentPreview = 'desktop';
    let profileData = {};
    let autoSaveTimeout;
    let hasUnsavedChanges = false;

    // Initialize profile data
    function initializeProfileData() {
        profileData = {
            primaryColor: document.getElementById('primaryColor')?.value || '#667eea',
            secondaryColor: document.getElementById('secondaryColor')?.value || '#764ba2',
            backgroundColor: document.getElementById('backgroundColor')?.value || '#f7faff',
            fontFamily: document.getElementById('fontFamily')?.value || 'Inter',
            fontSize: document.getElementById('fontSize')?.value || 16,
            fullName: document.getElementById('fullName')?.value || '{{ current_user.full_name or "Your Name" }}',
            profession: document.getElementById('profession')?.value || '{{ current_user.profession or "Professional" }}',
            bio: document.getElementById('bio')?.value || '{{ current_user.bio or "Tell us about yourself..." }}',
            location: document.getElementById('location')?.value || '{{ current_user.location or "Your Location" }}',
            industry: document.getElementById('industry')?.value || '{{ current_user.industry or "" }}',
            hourlyRate: '{{ current_user.hourly_rate or 0 }}',
            expertiseTags: document.getElementById('expertiseTags')?.value || '{{ current_user.specialty_tags or "" }}',
            linkedinUrl: document.getElementById('linkedinUrl')?.value || '{{ current_user.linkedin_url or "" }}',
            twitterUrl: document.getElementById('twitterUrl')?.value || '{{ current_user.twitter_url or "" }}',
            githubUrl: document.getElementById('githubUrl')?.value || '{{ current_user.github_url or "" }}',
            instagramUrl: document.getElementById('instagramUrl')?.value || '{{ current_user.instagram_url or "" }}',
            youtubeUrl: document.getElementById('youtubeUrl')?.value || '{{ current_user.youtube_url or "" }}',
            websiteUrl: document.getElementById('websiteUrl')?.value || '{{ current_user.website_url or "" }}',
            isAvailable: document.getElementById('isAvailable')?.checked || true,
            emailNotifications: document.getElementById('emailNotifications')?.checked || true,
            showServices: document.getElementById('showServices')?.checked || true,
            showContent: document.getElementById('showContent')?.checked || true,
            serviceDescription: document.getElementById('serviceDescription')?.value || '{{ current_user.service_description or "" }}',
            sessionDuration: document.getElementById('sessionDuration')?.value || '{{ current_user.session_duration or 30 }}',
            contentDescription: document.getElementById('contentDescription')?.value || '{{ current_user.content_description or "" }}',
            contentCategories: document.getElementById('contentCategories')?.value || '{{ current_user.content_categories or "" }}'
        };
    }

    // Tab switching
    function switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        const clickedBtn = event.target.closest('.tab-btn');
        if (clickedBtn) {
            clickedBtn.classList.add('active');
        }
        
        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
        const targetPanel = document.getElementById(tabName + '-tab');
        if (targetPanel) {
            targetPanel.classList.add('active');
        }
        
        currentTab = tabName;
        
        // Update preview after tab switch
        setTimeout(() => {
            updatePreview();
        }, 50);
    }

    // Preview switching
    function switchPreview(previewType) {
        document.querySelectorAll('.preview-btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');
        
        document.getElementById('desktop-preview').style.display = previewType === 'desktop' ? 'block' : 'none';
        document.getElementById('mobile-preview').style.display = previewType === 'mobile' ? 'block' : 'none';
        
        currentPreview = previewType;
        updatePreview();
    }

    // Auto-save functionality
    function autoSave() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(() => {
            saveProfile(true); // Silent save
        }, 2000); // Save 2 seconds after last change
    }

    // Update preview
    function updatePreview() {
        // Re-initialize profile data to get current form values
        initializeProfileData();
        
        const previewElement = currentPreview === 'mobile' ? 
            document.getElementById('profilePreviewMobile') : 
            document.getElementById('profilePreview');
        
        if (!previewElement) {
            console.error('Preview element not found:', currentPreview === 'mobile' ? 'profilePreviewMobile' : 'profilePreview');
            return;
        }
        
        // Generate and set the preview HTML
        const previewHTML = generatePreviewHTML();
        previewElement.innerHTML = previewHTML;
        previewElement.style.fontFamily = profileData.fontFamily;
        previewElement.style.fontSize = profileData.fontSize + 'px';
        
        // Trigger auto-save
        autoSave();
        
        // Re-render feather icons if they exist
        if (window.feather) {
            feather.replace();
        }
    }

    // Generate preview HTML - matches real profile exactly
    function generatePreviewHTML() {
        const socialLinks = [];
        if (profileData.linkedinUrl) socialLinks.push({name: 'LinkedIn', url: profileData.linkedinUrl, icon: 'fab fa-linkedin'});
        if (profileData.twitterUrl) socialLinks.push({name: 'Twitter', url: profileData.twitterUrl, icon: 'fab fa-twitter'});
        if (profileData.githubUrl) socialLinks.push({name: 'GitHub', url: profileData.githubUrl, icon: 'fab fa-github'});
        if (profileData.instagramUrl) socialLinks.push({name: 'Instagram', url: profileData.instagramUrl, icon: 'fab fa-instagram'});
        if (profileData.youtubeUrl) socialLinks.push({name: 'YouTube', url: profileData.youtubeUrl, icon: 'fab fa-youtube'});
        if (profileData.websiteUrl) socialLinks.push({name: 'Website', url: profileData.websiteUrl, icon: 'fas fa-globe'});
        
        return `
            <div class="container-fluid" style="background: ${profileData.backgroundColor || '#f7faff'}; min-height: 100vh;">
                <div class="row">
                    <div class="col-12">
                        <!-- Profile Header -->
                        <div class="profile-header" style="background: linear-gradient(135deg, ${profileData.primaryColor || '#667eea'} 0%, ${profileData.secondaryColor || '#764ba2'} 100%); color: white; padding: 1.5rem 1rem; margin-bottom: 1.5rem; border-radius: 0.5rem;">
                            <div class="row align-items-center">
                                <div class="col-md-3">
                                    <div class="profile-avatar text-center">
                                        <img src="${document.getElementById('profileImagePreview')?.src || '/static/img/default-avatar.svg'}" 
                                             alt="Profile Picture" 
                                             class="rounded-circle mb-3 profile-avatar-img" 
                                             style="width: 150px; height: 150px; object-fit: cover;">
                                    </div>
                                </div>
                                <div class="col-md-9">
                                    <div class="profile-info">
                                        <h1 class="profile-name" style="font-size: 1.75rem; font-weight: 700; margin-bottom: 0.5rem; line-height: 1.3;">${profileData.fullName || 'Your Name'}</h1>
                                        <p class="profile-title" style="font-size: 1rem; opacity: 0.9; margin-bottom: 0.5rem;">${profileData.profession || 'Professional'}</p>
                                        <p class="profile-location" style="font-size: 0.9rem; opacity: 0.8; margin-bottom: 1rem;">
                                            <i class="fas fa-map-marker-alt me-2"></i>${profileData.location || 'Location not specified'}
                                        </p>
                                        
                                        ${profileData.bio ? `
                                        <div class="profile-bio" style="margin-bottom: 1rem; font-size: 0.95rem; line-height: 1.5;">
                                            <p>${profileData.bio}</p>
                                        </div>
                                        ` : ''}
                                        
                                        <div class="profile-stats" style="margin-top: 1rem;">
                                            <div class="row">
                                                <div class="col-md-3">
                                                    <div class="stat-item" style="text-align: center; padding: 0.75rem; background: rgba(255, 255, 255, 0.1); border-radius: 0.5rem; margin-bottom: 0.75rem;">
                                                        <h5 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem;">4.8</h5>
                                                        <small style="opacity: 0.8;">Rating</small>
                                                    </div>
                                                </div>
                                                <div class="col-md-3">
                                                    <div class="stat-item" style="text-align: center; padding: 0.75rem; background: rgba(255, 255, 255, 0.1); border-radius: 0.5rem; margin-bottom: 0.75rem;">
                                                        <h5 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem;">24</h5>
                                                        <small style="opacity: 0.8;">Reviews</small>
                                                    </div>
                                                </div>
                                                <div class="col-md-3">
                                                    <div class="stat-item" style="text-align: center; padding: 0.75rem; background: rgba(255, 255, 255, 0.1); border-radius: 0.5rem; margin-bottom: 0.75rem;">
                                                        <h5 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem;">$${profileData.hourlyRate || 0}</h5>
                                                        <small style="opacity: 0.8;">Per Session</small>
                                                    </div>
                                                </div>
                                                <div class="col-md-3">
                                                    <div class="stat-item" style="text-align: center; padding: 0.75rem; background: rgba(255, 255, 255, 0.1); border-radius: 0.5rem; margin-bottom: 0.75rem;">
                                                        <h5 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.25rem;">12</h5>
                                                        <small style="opacity: 0.8;">Content Items</small>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Navigation Tabs -->
                        <div class="profile-nav" style="margin-bottom: 1.5rem;">
                            <ul class="nav nav-tabs" id="profileTabs" role="tablist" style="border-bottom: 2px solid #e5e7eb;">
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link active" style="border: none; color: ${profileData.primaryColor || '#667eea'}; font-weight: 500; padding: 0.75rem 1rem; border-radius: 0.5rem 0.5rem 0 0; margin-right: 0.5rem; background: #f8fafc; border-bottom: 2px solid ${profileData.primaryColor || '#667eea'};">
                                        <i class="fas fa-video me-2"></i>Services
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" style="border: none; color: #6b7280; font-weight: 500; padding: 0.75rem 1rem; border-radius: 0.5rem 0.5rem 0 0; margin-right: 0.5rem;">
                                        <i class="fas fa-lock me-2"></i>Premium Content
                                    </button>
                                </li>
                                <li class="nav-item" role="presentation">
                                    <button class="nav-link" style="border: none; color: #6b7280; font-weight: 500; padding: 0.75rem 1rem; border-radius: 0.5rem 0.5rem 0 0; margin-right: 0.5rem;">
                                        <i class="fas fa-user me-2"></i>About
                                    </button>
                                </li>
                            </ul>
                        </div>

                        <!-- Tab Content -->
                        <div class="tab-content" id="profileTabContent">
                            <!-- Services Tab -->
                            <div class="tab-pane fade show active" id="services" role="tabpanel">
                                <div class="card" style="background: #fff; border: 1px solid #dee2e6; border-radius: 0.5rem; padding: 1rem; transition: transform 0.2s ease, box-shadow 0.2s ease; height: 100%; margin-bottom: 1rem;">
                                    <div class="card-body">
                                        <h5 class="card-title">1-on-1 Sessions</h5>
                                        <p class="card-text">Book a personal session with ${profileData.fullName || 'Your Name'}</p>
                                        
                                        <div class="service-details">
                                            <div class="row">
                                                <div class="col-md-6">
                                                    <h6>Session Details</h6>
                                                    <ul class="list-unstyled">
                                                        <li><i class="fas fa-clock me-2"></i>Duration: ${profileData.sessionDuration || 30} minutes</li>
                                                        <li><i class="fas fa-dollar-sign me-2"></i>Price: $${profileData.hourlyRate || 0}</li>
                                                        <li><i class="fas fa-video me-2"></i>Video call via platform</li>
                                                    </ul>
                                                </div>
                                                <div class="col-md-6">
                                                    <h6>What You'll Get</h6>
                                                    <ul class="list-unstyled">
                                                        <li><i class="fas fa-check me-2 text-success"></i>Personalized advice</li>
                                                        <li><i class="fas fa-check me-2 text-success"></i>Direct interaction</li>
                                                        <li><i class="fas fa-check me-2 text-success"></i>Follow-up resources</li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div class="text-center mt-4">
                                            ${profileData.isAvailable ? `
                                                <button class="btn btn-primary btn-lg" style="background: ${profileData.primaryColor || '#667eea'}; border-color: ${profileData.primaryColor || '#667eea'};">
                                                    <i class="fas fa-calendar-plus me-2"></i>Book a Session
                                                </button>
                                            ` : `
                                                <button class="btn btn-secondary btn-lg" disabled>
                                                    <i class="fas fa-pause me-2"></i>Currently Unavailable
                                                </button>
                                            `}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Color input synchronization
    function updateColorFromText(colorType) {
        const textInput = document.getElementById(colorType + 'ColorText');
        const colorInput = document.getElementById(colorType + 'Color');
        colorInput.value = textInput.value;
        // Update preview after color change
        updatePreview();
    }

    // Image upload handling
    function handleImageUpload(input) {
        const file = input.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.getElementById('profileImagePreview');
                if (preview) {
                    preview.src = e.target.result;
                } else {
                    const placeholder = document.querySelector('.upload-placeholder');
                    placeholder.innerHTML = `<img src="${e.target.result}" alt="Profile" style="max-width: 100%; max-height: 200px; border-radius: 8px;">`;
                }
                // Update preview after image is loaded
                updatePreview();
            };
            reader.readAsDataURL(file);
        }
    }

    // Save profile
    function saveProfile(silent = false) {
        initializeProfileData();
        
        const formData = new FormData();
        
        // Add all form fields
        const formFields = [
            'fullName', 'profession', 'bio', 'location', 'industry', 
            'expertiseTags', 'linkedinUrl', 'twitterUrl', 'githubUrl', 'instagramUrl', 
            'youtubeUrl', 'websiteUrl', 'phone', 'language', 'timezone',
            'primaryColor', 'secondaryColor', 'backgroundColor', 'fontFamily', 'fontSize',
            'isAvailable', 'emailNotifications', 'showServices', 'showContent', 
            'showAbout', 'showSocial', 'serviceDescription', 'sessionDuration',
            'contentDescription', 'contentCategories'
        ];
        
        formFields.forEach(field => {
            const element = document.getElementById(field);
            if (element) {
                if (element.type === 'checkbox') {
                    formData.append(field, element.checked);
                } else {
                    formData.append(field, element.value);
                }
            }
        });
        
        // Add image files if uploaded
        const profileImage = document.getElementById('profileImageUpload');
        
        if (profileImage && profileImage.files[0]) {
            formData.append('profile_image', profileImage.files[0]);
        }
        
        // Show loading state only if not silent
        let saveBtn, originalText;
        if (!silent) {
            saveBtn = document.querySelector('.btn-primary');
            if (saveBtn) {
                originalText = saveBtn.innerHTML;
                saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Saving...</span>';
                saveBtn.disabled = true;
            }
        }
        
        fetch('/api/profile/update', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                hasUnsavedChanges = false;
                if (!silent && saveBtn) {
                    // Show success message
                    saveBtn.innerHTML = '<i class="fas fa-check"></i><span>Saved!</span>';
                    saveBtn.style.background = '#10b981';
                    setTimeout(() => {
                        saveBtn.innerHTML = originalText;
                        saveBtn.style.background = '';
                        saveBtn.disabled = false;
                    }, 2000);
                }
            } else {
                if (!silent) {
                    alert('Failed to update profile: ' + (data.message || data.error || 'Unknown error'));
                    if (saveBtn) {
                        saveBtn.innerHTML = originalText;
                        saveBtn.disabled = false;
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            if (!silent) {
                alert('Failed to update profile: ' + error.message);
                if (saveBtn) {
                    saveBtn.innerHTML = originalText;
                    saveBtn.disabled = false;
                }
            }
        });
    }

    // Preview profile
    function previewProfile() {
        const url = `/profile/{{ current_user.username }}`;
        window.open(url, '_blank');
    }

    // Copy profile link
    function copyProfileLink() {
        const profileUrl = `${window.location.origin}/profile/{{ current_user.username }}`;
        navigator.clipboard.writeText(profileUrl).then(function() {
            // Show success message
            const button = event.target.closest('.preview-action');
            const originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-check"></i><span>Copied!</span>';
            button.style.background = '#10b981';
            button.style.borderColor = '#10b981';
            
            setTimeout(() => {
                button.innerHTML = originalText;
                button.style.background = '';
                button.style.borderColor = '';
            }, 2000);
        }).catch(function(err) {
            console.error('Could not copy text: ', err);
            alert('Could not copy link. Please copy manually: ' + profileUrl);
        });
    }

    // Initialize on page load
    function initialize() {
        // Initialize profile data
        initializeProfileData();
        
        // Set up font size display
        const fontSizeSlider = document.getElementById('fontSize');
        const fontSizeValue = document.getElementById('fontSizeValue');
        if (fontSizeSlider && fontSizeValue) {
            fontSizeSlider.addEventListener('input', function() {
                fontSizeValue.textContent = this.value + 'px';
            });
        }
        
        // Initial preview update
        setTimeout(() => {
            updatePreview();
        }, 100);
        
        // Add event listeners to all form fields to update preview in real-time
        const formFields = [
            'fullName', 'profession', 'bio', 'location', 'industry', 
            'expertiseTags', 'linkedinUrl', 'twitterUrl', 'githubUrl', 'instagramUrl', 
            'youtubeUrl', 'websiteUrl', 'phone', 'language', 'timezone',
            'fontFamily', 'fontSize', 'primaryColor', 'secondaryColor', 'backgroundColor',
            'serviceDescription', 'sessionDuration', 'contentDescription', 'contentCategories'
        ];
        
        formFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                element.addEventListener('input', function() {
                    updatePreview();
                });
                element.addEventListener('change', function() {
                    updatePreview();
                });
            }
        });
        
        // Add event listeners for checkboxes
        const checkboxFields = [
            'isAvailable', 'emailNotifications', 'showServices', 'showContent', 
            'showAbout', 'showSocial'
        ];
        
        checkboxFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                element.addEventListener('change', function() {
                    updatePreview();
                });
            }
        });
        
        // Add event listeners for color inputs
        const colorFields = ['primaryColor', 'secondaryColor', 'backgroundColor'];
        colorFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                element.addEventListener('input', function() {
                    updatePreview();
                });
                element.addEventListener('change', function() {
                    updatePreview();
                });
            }
        });
        
        // Add event listeners for color text inputs
        const colorTextFields = ['primaryColorText', 'secondaryColorText', 'backgroundColorText'];
        colorTextFields.forEach(fieldId => {
            const element = document.getElementById(fieldId);
            if (element) {
                element.addEventListener('input', function() {
                    updatePreview();
                });
                element.addEventListener('change', function() {
                    updatePreview();
                });
            }
        });
        
        // Add event listeners for image uploads
        const profileImageUpload = document.getElementById('profileImageUpload');
        if (profileImageUpload) {
            profileImageUpload.addEventListener('change', function() {
                handleImageUpload(this);
            });
        }
    }

    // Make functions globally available
    window.switchTab = switchTab;
    window.switchPreview = switchPreview;
    window.updatePreview = updatePreview;
    window.handleImageUpload = handleImageUpload;
    window.updateColorFromText = updateColorFromText;
    window.saveProfile = saveProfile;
    window.previewProfile = previewProfile;
    window.copyProfileLink = copyProfileLink;

    // Initialize
    initialize();
});
