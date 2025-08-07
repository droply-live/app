/**
 * Modern Tabbed Interface
 * Handles tab switching and content management
 */

class TabbedInterface {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.tabs = [];
    this.activeTab = null;
    this.init();
  }

  init() {
    if (!this.container) return;
    
    // Find all tab buttons
    const tabButtons = this.container.querySelectorAll('.tab-button');
    
    tabButtons.forEach((button, index) => {
      const tabId = button.getAttribute('data-tab');
      const tabContent = this.container.querySelector(`[data-tab-content="${tabId}"]`);
      
      if (tabContent) {
        this.tabs.push({
          id: tabId,
          button: button,
          content: tabContent
        });
        
        // Add click event
        button.addEventListener('click', () => this.switchTab(tabId));
        
        // Set first tab as active by default
        if (index === 0) {
          this.activeTab = tabId;
          button.classList.add('active');
          tabContent.classList.add('active');
        }
      }
    });
    
    // Initialize tab indicator
    this.updateTabIndicator();
  }

  switchTab(tabId) {
    // Remove active class from all tabs
    this.tabs.forEach(tab => {
      tab.button.classList.remove('active');
      tab.content.classList.remove('active');
    });
    
    // Add active class to selected tab
    const selectedTab = this.tabs.find(tab => tab.id === tabId);
    if (selectedTab) {
      selectedTab.button.classList.add('active');
      selectedTab.content.classList.add('active');
      this.activeTab = tabId;
      
      // Update tab indicator
      this.updateTabIndicator();
      
      // Trigger custom event
      this.container.dispatchEvent(new CustomEvent('tabChanged', {
        detail: { tabId: tabId }
      }));
    }
  }

  updateTabIndicator() {
    const activeButton = this.container.querySelector('.tab-button.active');
    if (activeButton) {
      const indicator = this.container.querySelector('.tab-indicator');
      if (indicator) {
        const buttonRect = activeButton.getBoundingClientRect();
        const containerRect = this.container.getBoundingClientRect();
        
        indicator.style.left = (buttonRect.left - containerRect.left) + 'px';
        indicator.style.width = buttonRect.width + 'px';
      }
    }
  }

  getActiveTab() {
    return this.activeTab;
  }

  setActiveTab(tabId) {
    this.switchTab(tabId);
  }
}

// Initialize tabbed interfaces when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
  // Initialize bookings tabs
  const bookingsTabs = new TabbedInterface('bookings-tabs');
  
  // Initialize earnings tabs
  const earningsTabs = new TabbedInterface('earnings-tabs');
  
  // Initialize account tabs
  const accountTabs = new TabbedInterface('account-tabs');
  
  // Handle tab changes
  document.addEventListener('tabChanged', function(e) {
    console.log('Tab changed to:', e.detail.tabId);
    
    // You can add custom logic here for different tab changes
    // For example, loading data via AJAX, updating URL, etc.
  });
});

// Utility functions for tab management
window.TabUtils = {
  // Create a new tab dynamically
  createTab: function(containerId, tabId, title, content, icon = null) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const tabNavigation = container.querySelector('.tab-navigation');
    const tabContent = container.querySelector('.tab-content-container');
    
    if (tabNavigation && tabContent) {
      // Create tab button
      const button = document.createElement('button');
      button.className = 'tab-button';
      button.setAttribute('data-tab', tabId);
      button.innerHTML = `
        ${icon ? `<i class="${icon}"></i>` : ''}
        <span>${title}</span>
      `;
      
      // Create tab content
      const contentDiv = document.createElement('div');
      contentDiv.className = 'tab-content';
      contentDiv.setAttribute('data-tab-content', tabId);
      contentDiv.innerHTML = content;
      
      // Add to DOM
      tabNavigation.appendChild(button);
      tabContent.appendChild(contentDiv);
      
      // Reinitialize tabs
      const tabbedInterface = new TabbedInterface(containerId);
      
      return tabbedInterface;
    }
  },
  
  // Remove a tab
  removeTab: function(containerId, tabId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const button = container.querySelector(`[data-tab="${tabId}"]`);
    const content = container.querySelector(`[data-tab-content="${tabId}"]`);
    
    if (button && content) {
      button.remove();
      content.remove();
      
      // Reinitialize tabs
      new TabbedInterface(containerId);
    }
  },
  
  // Update tab content
  updateTabContent: function(containerId, tabId, newContent) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const content = container.querySelector(`[data-tab-content="${tabId}"]`);
    if (content) {
      content.innerHTML = newContent;
    }
  },
  
  // Add badge to tab
  addTabBadge: function(containerId, tabId, badgeText, badgeClass = '') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const button = container.querySelector(`[data-tab="${tabId}"]`);
    if (button) {
      let badge = button.querySelector('.tab-badge');
      if (!badge) {
        badge = document.createElement('span');
        badge.className = `tab-badge ${badgeClass}`;
        button.appendChild(badge);
      }
      badge.textContent = badgeText;
    }
  },
  
  // Remove badge from tab
  removeTabBadge: function(containerId, tabId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const button = container.querySelector(`[data-tab="${tabId}"]`);
    if (button) {
      const badge = button.querySelector('.tab-badge');
      if (badge) {
        badge.remove();
      }
    }
  }
};
