// Live Profile Preview for Profile Setup

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('profileForm');
  const preview = document.getElementById('profilePreview');

  // Auto-save functionality
  let saveTimeout;
  let hasUnsavedChanges = false;
  const SAVE_DELAY = 1000; // Save after 1 second of inactivity

  function autoSave() {
    clearTimeout(saveTimeout);
    hasUnsavedChanges = true;
    saveTimeout = setTimeout(() => {
      saveProfile();
    }, SAVE_DELAY);
  }

  function saveProfile() {
    const formData = new FormData();
    
    // Collect all form data
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
      if (input.type === 'file') {
        if (input.files && input.files[0]) {
          formData.append(input.name, input.files[0]);
        }
      } else {
        formData.append(input.name, input.value);
      }
    });

    // Show saving indicator
    showSavingIndicator();

    fetch('/edit-profile', {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      body: formData
    })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Save failed');
      }
    })
    .then(data => {
      if (data.success) {
        hasUnsavedChanges = false;
        showSavedIndicator();
      } else {
        showErrorIndicator(data.message || 'Save failed');
      }
    })
    .catch(error => {
      console.error('Save error:', error);
      showErrorIndicator('Save failed');
    });
  }

  function showSavingIndicator() {
    // Remove existing indicators
    document.querySelectorAll('.save-indicator').forEach(el => el.remove());
    
    const indicator = document.createElement('div');
    indicator.className = 'save-indicator saving';
    indicator.innerHTML = `
      <div class="indicator-content">
        <div class="indicator-icon">⏳</div>
        <div class="indicator-text">Saving...</div>
      </div>
    `;
    document.body.appendChild(indicator);
    
    setTimeout(() => {
      indicator.style.opacity = '1';
      indicator.style.transform = 'translateY(0)';
    }, 10);
  }

  function showSavedIndicator() {
    const indicator = document.querySelector('.save-indicator');
    if (indicator) {
      indicator.className = 'save-indicator saved';
      indicator.innerHTML = `
        <div class="indicator-content">
          <div class="indicator-icon">✅</div>
          <div class="indicator-text">Saved!</div>
        </div>
      `;
      
      setTimeout(() => {
        indicator.style.opacity = '0';
        indicator.style.transform = 'translateY(-10px)';
        setTimeout(() => indicator.remove(), 300);
      }, 1500);
    }
  }

  function showErrorIndicator(message) {
    const indicator = document.querySelector('.save-indicator');
    if (indicator) {
      indicator.className = 'save-indicator error';
      indicator.innerHTML = `
        <div class="indicator-content">
          <div class="indicator-icon">❌</div>
          <div class="indicator-text">${message}</div>
        </div>
      `;
      
      setTimeout(() => {
        indicator.style.opacity = '0';
        indicator.style.transform = 'translateY(-10px)';
        setTimeout(() => indicator.remove(), 300);
      }, 3000);
    }
  }

  // Helper: get value or fallback
  function val(id) {
    const el = document.getElementById(id);
    return el ? el.value : '';
  }
  function checked(id) {
    const el = document.getElementById(id);
    return el ? el.checked : false;
  }
  function getProfilePic() {
    const input = document.getElementById('profile_picture');
    if (input && input.files && input.files[0]) {
      return URL.createObjectURL(input.files[0]);
    }
    const img = document.getElementById('currentProfilePic');
    return img ? img.src : '/static/img/default-avatar.png';
  }

  // Field mapping for highlighting - ordered to match preview layout
  const fieldMapping = {
    'collapsePic': ['profile_pic'],
    'collapseBasic': ['name', 'profession'],
    'collapseBio': ['bio'],
    'collapseExpertise': ['expertise'],
    'collapseLocation': ['location'],
    'collapseSocial': ['social_links'],
    'collapseIndustry': ['industry'],
    'collapseRate': ['hourly_rate']
  };

  function highlightPreviewFields(collapseId) {
    // Remove all existing highlights
    document.querySelectorAll('.preview-highlight').forEach(el => {
      el.classList.remove('preview-highlight');
    });

    const fieldsToHighlight = fieldMapping[collapseId] || [];
    
    fieldsToHighlight.forEach(fieldType => {
      let elements = [];
      
      switch(fieldType) {
        case 'name':
          elements = preview.querySelectorAll('h1');
          break;
        case 'profession':
          elements = preview.querySelectorAll('p[style*="color: #667eea"]');
          break;
        case 'bio':
          elements = preview.querySelectorAll('p[style*="font-size: 0.92rem; color: #666; line-height: 1.4"]');
          break;
        case 'expertise':
          // Only target the expertise tags, not the location or connect sections
          elements = preview.querySelectorAll('.preview-tag');
          break;
        case 'location':
          // Target the location text specifically, not the icon
          elements = preview.querySelectorAll('p[style*="color: #666; font-size: 0.92rem"]');
          break;
        case 'industry':
          // Only target the industry badge, not the hourly rate
          elements = preview.querySelectorAll('span[style*="background: #f8f9fa; color: #667eea"]');
          break;
        case 'hourly_rate':
          // Target the hourly rate specifically
          elements = preview.querySelectorAll('span[style*="font-size: 1.1rem; font-weight: 700; color: #667eea"]');
          break;
        case 'profile_pic':
          // Target the profile image container
          elements = preview.querySelectorAll('img[alt="Profile picture"]');
          break;
        case 'social_links':
          // Target only the social links section, not expertise or location
          const connectSection = preview.querySelector('div[style*="margin-bottom: 0; min-height: 20px;"]');
          if (connectSection) {
            elements = [connectSection];
          }
          break;
      }
      
      elements.forEach(el => {
        el.classList.add('preview-highlight');
      });
    });
  }

  function renderPreview() {
    // Build tags from three expertise fields
    const expertise1 = val('expertise_1');
    const expertise2 = val('expertise_2');
    const expertise3 = val('expertise_3');
    const tags = [expertise1, expertise2, expertise3].filter(Boolean);
    // Social links
    const socials = [
      {id: 'linkedin', icon: 'linkedin', color: '#0077b5'},
      {id: 'twitter', icon: 'twitter', color: '#1da1f2'},
      {id: 'website', icon: 'globe', color: '#667eea'},
      {id: 'instagram', icon: 'instagram', color: '#e4405f'},
      {id: 'github', icon: 'github', color: '#333'},
      {id: 'facebook', icon: 'facebook', color: '#4267B2'}
    ];
    let socialLinks = '';
    socials.forEach(s => {
      const url = val(s.id);
      if (url) {
        socialLinks += `<a href="${url}" target="_blank" class="preview-social-link" style="color: ${s.color}"><i data-feather="${s.icon}"></i></a>`;
      }
    });
    if (!socialLinks) {
      socialLinks = '<span style="color: #bbb; font-size: 0.9rem;">No social links.</span>';
    }
    // Profile card HTML
    preview.innerHTML = `
      <div class="profile-card d-flex flex-column justify-content-between">
        <div style="text-align: center; margin-bottom: 1rem;">
          <div style="width: 72px; height: 72px; border-radius: 50%; background: white; margin: 0 auto; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 16px rgba(0,0,0,0.08); border: 3px solid white;">
            <img src="${getProfilePic()}" alt="Profile picture" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">
          </div>
        </div>
        <div style="text-align: center; margin-bottom: 0.7rem;">
          <h1 style="font-size: 1.1rem; font-weight: 800; color: #1a1a1a; margin-bottom: 0.2rem;">${val('full_name') || 'Your Name'}</h1>
          <p style="font-size: 0.95rem; color: #667eea; font-weight: 600; margin-bottom: 0.2rem;">${val('profession') || 'Professional'}</p>
          <div style="height: 1.2rem;"></div>
        </div>
        <div style="margin-bottom: 0.6rem; min-height: 36px;">
          <h3 style="font-size: 0.98rem; font-weight: 700; color: #1a1a1a; margin-bottom: 0.2rem;">About me</h3>
          <p style="font-size: 0.92rem; color: #666; line-height: 1.4; margin-bottom: 0;">${val('bio') || 'No bio available yet.'}</p>
        </div>
        <div style="margin-bottom: 0.6rem; min-height: 28px;">
          <h4 style="font-size: 0.93rem; font-weight: 600; color: #1a1a1a; margin-bottom: 0.2rem;">Expertise</h4>
          ${tags.length ? tags.map(tag => `<span class="preview-tag">${tag}</span>`).join('') : '<span style="color: #bbb; font-size: 0.9rem;">No expertise listed.</span>'}
        </div>
        <div style="margin-bottom: 0.6rem; min-height: 20px;">
          <h4 style="font-size: 0.93rem; font-weight: 600; color: #1a1a1a; margin-bottom: 0.1rem;">Location</h4>
          <p style="color: #666; font-size: 0.92rem; margin-bottom: 0;">
            <i data-feather="map-pin" style="width: 13px; height: 13px; margin-right: 0.3rem;"></i>
            ${val('location') || '<span style=\'color: #bbb; font-size: 0.9rem;\'>No location set.</span>'}
          </p>
        </div>
        <div style="margin-bottom: 0; min-height: 20px;">
          <h4 style="font-size: 0.93rem; font-weight: 600; color: #1a1a1a; margin-bottom: 0.1rem;">Connect</h4>
          <div>${socialLinks}</div>
        </div>
        <div style="margin-top: 1rem; text-align: center;">
          <span style="background: #f8f9fa; color: #667eea; padding: 0.2rem 0.7rem; border-radius: 12px; font-size: 0.95rem; font-weight: 600;">${val('industry') || 'Industry'}</span>
          <span style="background: #f8f9fa; color: #28a745; padding: 0.2rem 0.7rem; border-radius: 12px; font-size: 0.95rem; font-weight: 600; margin-left: 0.5rem;">${checked('is_available') ? 'Available' : 'Unavailable'}</span>
        </div>
        <div style="margin-top: 0.5rem; text-align: center;">
          <span style="font-size: 1.1rem; font-weight: 700; color: #667eea;">${val('hourly_rate') ? '$' + val('hourly_rate') + '/hr' : 'Rate not set'}</span>
        </div>
      </div>
    `;
    if (window.feather) feather.replace();
  }

  // Listen to all relevant inputs
  [
    'full_name', 'profession', 'industry', 'hourly_rate', 'location', 'expertise_1', 'expertise_2', 'expertise_3',
    'bio', 'linkedin', 'twitter', 'github', 'website', 'instagram', 'facebook'
  ].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', () => {
        renderPreview();
        autoSave();
      });
      el.addEventListener('change', () => {
        renderPreview();
        autoSave();
      });
    }
  });
  // Profile picture
  const picInput = document.getElementById('profile_picture');
  if (picInput) {
    picInput.addEventListener('change', () => {
      renderPreview();
      autoSave();
    });
  }

  // Initial render
  renderPreview();
  
  // Highlight Profile Picture by default since it's open
  setTimeout(() => {
    highlightPreviewFields('collapsePic');
  }, 100);

  // Custom accordion behavior: only one section open at a time, and clicking an open section closes it
  document.querySelectorAll('.accordion-button').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      const target = btn.getAttribute('data-bs-target');
      if (!target) return;
      
      const currentCollapse = document.querySelector(target);
      if (!currentCollapse) return;
      
      const isCurrentlyOpen = currentCollapse.classList.contains('show');
      
      // If the clicked section is already open, just close it
      if (isCurrentlyOpen) {
        const bsCollapse = bootstrap.Collapse.getOrCreateInstance(currentCollapse);
        bsCollapse.hide();
        // Remove highlights when closing
        setTimeout(() => {
          document.querySelectorAll('.preview-highlight').forEach(el => {
            el.classList.remove('preview-highlight');
          });
          document.querySelectorAll('.field-indicator').forEach(el => {
            el.remove();
          });
        }, 300);
        return;
      }
      
      // Otherwise, close all other sections first, then open the clicked one
      document.querySelectorAll('.accordion-collapse').forEach(function(collapse) {
        if (collapse !== currentCollapse && collapse.classList.contains('show')) {
          const bsCollapse = bootstrap.Collapse.getOrCreateInstance(collapse);
          bsCollapse.hide();
        }
      });
      
      // Open the current section
      const bsCollapse = bootstrap.Collapse.getOrCreateInstance(currentCollapse);
      bsCollapse.show();
      
      // Highlight fields after a short delay to allow animation to start
      setTimeout(() => {
        highlightPreviewFields(currentCollapse.id);
      }, 150);
    });
  });

  // Remove the data-bs-parent attribute to prevent Bootstrap's default accordion behavior
  // since we're implementing our own
  document.querySelectorAll('.accordion-collapse').forEach(function(el) {
    el.removeAttribute('data-bs-parent');
  });

  // Beforeunload event listener to warn users
  window.addEventListener('beforeunload', function(event) {
    if (hasUnsavedChanges) {
      event.preventDefault();
      event.returnValue = ''; // Required for Chrome
      return 'You have unsaved changes. Are you sure you want to leave?';
    }
  });
}); 