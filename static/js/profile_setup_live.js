// Live Profile Preview for Profile Setup

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('profileForm');
  const preview = document.getElementById('profilePreview');

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

  function renderPreview() {
    // Build tags from expertise (comma separated)
    const tags = val('expertise').split(',').map(t => t.trim()).filter(Boolean);
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
    'full_name', 'profession', 'industry', 'hourly_rate', 'location', 'expertise',
    'bio', 'linkedin', 'twitter', 'github', 'website', 'instagram', 'facebook', 'is_available'
  ].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener('input', renderPreview);
      el.addEventListener('change', renderPreview);
    }
  });
  // Profile picture
  const picInput = document.getElementById('profile_picture');
  if (picInput) {
    picInput.addEventListener('change', renderPreview);
  }

  // Initial render
  renderPreview();

  // Accordion: allow toggling open/close on header click, even if already open
  // This ensures clicking an open section header will close it

  document.querySelectorAll('.accordion-button').forEach(function(btn) {
    btn.addEventListener('click', function(e) {
      var target = btn.getAttribute('data-bs-target');
      if (!target) return;
      var collapse = document.querySelector(target);
      if (!collapse) return;
      if (collapse.classList.contains('show')) {
        // If already open, close it manually
        var bsCollapse = bootstrap.Collapse.getOrCreateInstance(collapse);
        bsCollapse.hide();
        e.preventDefault();
        e.stopPropagation();
      }
      // Otherwise, let Bootstrap handle opening
    });
  });

  // Accordion: allow multiple sections open/closed independently
  // Remove data-bs-parent from HTML, but also ensure toggling works
  // (If data-bs-parent is present, Bootstrap will only allow one open at a time)
  document.querySelectorAll('.accordion-collapse').forEach(function(el) {
    el.removeAttribute('data-bs-parent');
  });
}); 