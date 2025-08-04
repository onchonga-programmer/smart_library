// ==================== MAIN LIBRARY MANAGEMENT SYSTEM JS ====================

// Global variables
let searchTimeout;
let currentUser = null;
let notificationCount = 0;

// ==================== DOM READY & INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    setupEventListeners();
    initializeNavigation();
    initializeSearch();
    initializeModals();
    loadUserData();
    updateNotificationBadge();
    initializeTooltips();
    setupInfiniteScroll();
    initializeBookActions();
}

// ==================== EVENT LISTENERS ====================
function setupEventListeners() {
    // Mobile navigation toggle
    const mobileToggle = document.getElementById('mobile-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // User menu dropdown
    const userMenuBtn = document.getElementById('user-menu-btn');
    const userDropdownMenu = document.getElementById('user-dropdown-menu');
    
    if (userMenuBtn && userDropdownMenu) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = this.closest('.user-dropdown');
            dropdown.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', function() {
            const dropdown = document.querySelector('.user-dropdown');
            if (dropdown) {
                dropdown.classList.remove('active');
            }
        });
    }

    // Search form submission
    const searchForm = document.querySelector('.search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearchSubmit);
    }

    // Quick action forms
    const quickBorrowForm = document.getElementById('quickBorrowForm');
    const quickReturnForm = document.getElementById('quickReturnForm');
    
    if (quickBorrowForm) {
        quickBorrowForm.addEventListener('submit', handleQuickBorrow);
    }
    
    if (quickReturnForm) {
        quickReturnForm.addEventListener('submit', handleQuickReturn);
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);

    // Close modals on escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAllModals();
        }
    });

    // Handle window resize
    window.addEventListener('resize', handleWindowResize);

    // Handle scroll for navbar
    window.addEventListener('scroll', handleScroll);
}

// ==================== NAVIGATION ====================
function initializeNavigation() {
    // Highlight active navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Setup dropdown menus
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (toggle && menu) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                dropdown.classList.toggle('active');
            });
        }
    });
}

// ==================== SEARCH FUNCTIONALITY ====================
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    const searchSuggestions = document.getElementById('search-suggestions');
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                handleSearchInput(this.value);
            }, 300);
        });

        searchInput.addEventListener('focus', function() {
            if (this.value.length > 0) {
                showSearchSuggestions();
            }
        });

        searchInput.addEventListener('blur', function() {
            // Delay hiding suggestions to allow clicking
            setTimeout(() => {
                hideSearchSuggestions();
            }, 200);
        });
    }
}

function handleSearchInput(query) {
    if (query.length < 2) {
        hideSearchSuggestions();
        return;
    }

    // Show loading state
    showLoadingOverlay();

    // Simulate API call for search suggestions
    fetchSearchSuggestions(query)
        .then(suggestions => {
            displaySearchSuggestions(suggestions);
            hideLoadingOverlay();
        })
        .catch(error => {
            console.error('Search error:', error);
            hideLoadingOverlay();
            showToast('Error fetching search suggestions', 'error');
        });
}

function fetchSearchSuggestions(query) {
    // Simulate API call - replace with actual endpoint
    return new Promise((resolve) => {
        setTimeout(() => {
            const mockSuggestions = [
                { type: 'book', title: `${query} - Book Result 1`, author: 'Author Name' },
                { type: 'author', name: `${query} Author` },
                { type: 'category', name: `${query} Category` }
            ];
            resolve(mockSuggestions);
        }, 500);
    });
}

function displaySearchSuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (!suggestionsContainer) return;

    suggestionsContainer.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        
        if (suggestion.type === 'book') {
            item.innerHTML = `
                <div class="suggestion-book">
                    <i class="fas fa-book"></i>
                    <div>
                        <div class="suggestion-title">${suggestion.title}</div>
                        <div class="suggestion-author">by ${suggestion.author}</div>
                    </div>
                </div>
            `;
        } else if (suggestion.type === 'author') {
            item.innerHTML = `
                <div class="suggestion-author">
                    <i class="fas fa-user"></i>
                    <span>${suggestion.name}</span>
                </div>
            `;
        } else if (suggestion.type === 'category') {
            item.innerHTML = `
                <div class="suggestion-category">
                    <i class="fas fa-tag"></i>
                    <span>${suggestion.name}</span>
                </div>
            `;
        }
        
        item.addEventListener('click', () => {
            selectSuggestion(suggestion);
        });
        
        suggestionsContainer.appendChild(item);
    });

    showSearchSuggestions();
}

function selectSuggestion(suggestion) {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        if (suggestion.type === 'book') {
            searchInput.value = suggestion.title;
        } else {
            searchInput.value = suggestion.name;
        }
    }
    hideSearchSuggestions();
    // Trigger search
    handleSearchSubmit({ preventDefault: () => {} });
}

function showSearchSuggestions() {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'block';
    }
}

function hideSearchSuggestions() {
    const suggestionsContainer = document.getElementById('search-suggestions');
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }
}

function handleSearchSubmit(e) {
    e.preventDefault();
    const form = e.target || document.querySelector('.search-form');
    const formData = new FormData(form);
    const query = formData.get('q');
    
    if (!query || query.trim().length === 0) {
        showToast('Please enter a search term', 'warning');
        return;
    }

    // Show loading state
    showLoadingOverlay();
    
    // Redirect to search results or handle AJAX search
    const searchUrl = form.action + '?' + new URLSearchParams(formData).toString();
    window.location.href = searchUrl;
}

// ==================== MODAL FUNCTIONALITY ====================
function initializeModals() {
    // Setup modal close buttons
    const modalCloses = document.querySelectorAll('.modal-close');
    modalCloses.forEach(close => {
        close.addEventListener('click', function() {
            const modal = this.closest('.modal');
            closeModal(modal.id);
        });
    });

    // Close modal when clicking outside
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal(this.id);
            }
        });
    });
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
        
        // Focus first input
        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
        
        // Reset form if exists
        const form = modal.querySelector('form');
        if (form) {
            form.reset();
        }
    }
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal.active');
    modals.forEach(modal => {
        closeModal(modal.id);
    });
}

// ==================== QUICK ACTIONS ====================
function openQuickBorrowModal() {
    openModal('quickBorrowModal');
}

function openQuickReturnModal() {
    openModal('quickReturnModal');
}

function handleQuickBorrow(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const bookId = formData.get('bookId');
    const duration = formData.get('borrowDuration');

    if (!bookId) {
        showToast('Please enter a book ID', 'warning');
        return;
    }

    showLoadingOverlay();

    // Simulate API call
    simulateBorrowBook(bookId, duration)
        .then(response => {
            hideLoadingOverlay();
            closeModal('quickBorrowModal');
            showToast(`Book ${bookId} borrowed successfully for ${duration} days!`, 'success');
            updateUserStats();
        })
        .catch(error => {
            hideLoadingOverlay();
            showToast(error.message || 'Failed to borrow book', 'error');
        });
}

function handleQuickReturn(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);
    const bookId = formData.get('returnBookId');
    const condition = formData.get('condition');
    const notes = formData.get('notes');

    if (!bookId) {
        showToast('Please enter a book ID', 'warning');
        return;
    }

    showLoadingOverlay();

    // Simulate API call
    simulateReturnBook(bookId, condition, notes)
        .then(response => {
            hideLoadingOverlay();
            closeModal('quickReturnModal');
            showToast(`Book ${bookId} returned successfully!`, 'success');
            updateUserStats();
        })
        .catch(error => {
            hideLoadingOverlay();
            showToast(error.message || 'Failed to return book', 'error');
        });
}

// ==================== BOOK ACTIONS ====================
function initializeBookActions() {
    // Setup book card interactions
    const bookCards = document.querySelectorAll('.book-card');
    bookCards.forEach(card => {
        // Add click analytics
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.btn-overlay')) {
                trackBookView(this.dataset.bookId);
            }
        });
    });
}

function viewBook(bookId) {
    // Track book view
    trackBookView(bookId);
    
    // Navigate to book detail page
    window.location.href = `/books/${bookId}/`;
}

function addToWishlist(bookId) {
    showLoadingOverlay();
    
    // Simulate API call
    simulateAddToWishlist(bookId)
        .then(response => {
            hideLoadingOverlay();
            showToast('Book added to wishlist!', 'success');
            updateWishlistIcon(bookId, true);
        })
        .catch(error => {
            hideLoadingOverlay();
            showToast(error.message || 'Failed to add to wishlist', 'error');
        });
}

function removeFromWishlist(bookId) {
    showLoadingOverlay();
    
    // Simulate API call
    simulateRemoveFromWishlist(bookId)
        .then(response => {
            hideLoadingOverlay();
            showToast('Book removed from wishlist!', 'info');
            updateWishlistIcon(bookId, false);
        })
        .catch(error => {
            hideLoadingOverlay();
            showToast(error.message || 'Failed to remove from wishlist', 'error');
        });
}

function updateWishlistIcon(bookId, isInWishlist) {
    const bookCard = document.querySelector(`[data-book-id="${bookId}"]`);
    if (bookCard) {
        const wishlistBtn = bookCard.querySelector('.btn-overlay i.fa-heart');
        if (wishlistBtn) {
            if (isInWishlist) {
                wishlistBtn.classList.remove('far');
                wishlistBtn.classList.add('fas');
            } else {
                wishlistBtn.classList.remove('fas');
                wishlistBtn.classList.add('far');
            }
        }
    }
}

// ==================== USER DATA & NOTIFICATIONS ====================
function loadUserData() {
    // Simulate loading user data
    currentUser = {
        id: 1,
        name: 'John Doe',
        borrowedBooks: 3,
        reservations: 1,
        wishlistCount: 12
    };
    
    updateUserStats();
}

function updateUserStats() {
    // Update dashboard stats if on dashboard page
    const borrowedCount = document.getElementById('borrowed-count');
    const reservationCount = document.getElementById('reservation-count');
    const wishlistCount = document.getElementById('wishlist-count');
    
    if (borrowedCount && currentUser) {
        borrowedCount.textContent = currentUser.borrowedBooks;
    }
    if (reservationCount && currentUser) {
        reservationCount.textContent = currentUser.reservations;
    }
    if (wishlistCount && currentUser) {
        wishlistCount.textContent = currentUser.wishlistCount;
    }
}

function updateNotificationBadge() {
    const badge = document.getElementById('notification-count');
    if (badge) {
        // Simulate fetching notification count
        setTimeout(() => {
            notificationCount = 3; // Mock data
            badge.textContent = notificationCount;
            badge.style.display = notificationCount > 0 ? 'block' : 'none';
        }, 1000);
    }
}

// ==================== TOAST NOTIFICATIONS ====================
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = getToastIcon(type);
    toast.innerHTML = `
        <i class="${icon}"></i>
        <span>${message}</span>
        <button class="toast-close" onclick="closeToast(this)">
            <i class="fas fa-times"></i>
        </button>
    `;

    toastContainer.appendChild(toast);

    // Trigger animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);

    // Auto remove
    setTimeout(() => {
        closeToast(toast.querySelector('.toast-close'));
    }, duration);
}

function getToastIcon(type) {
    const icons = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    };
    return icons[type] || icons.info;
}

function closeToast(closeBtn) {
    const toast = closeBtn.closest('.toast');
    if (toast) {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }
}

// ==================== LOADING OVERLAY ====================
function showLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// ==================== UTILITY FUNCTIONS ====================
function handleKeyboardShortcuts(e) {
    // Ctrl/Cmd + K for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Ctrl/Cmd + B for quick borrow
    if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault();
        openQuickBorrowModal();
    }
    
    // Ctrl/Cmd + R for quick return
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        openQuickReturnModal();
    }
}

function handleWindowResize() {
    // Close mobile menu on resize to desktop
    if (window.innerWidth > 768) {
        const navMenu = document.getElementById('nav-menu');
        const mobileToggle = document.getElementById('mobile-toggle');
        
        if (navMenu && mobileToggle) {
            navMenu.classList.remove('active');
            mobileToggle.classList.remove('active');
        }
    }
}

function handleScroll() {
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.backdropFilter = 'blur(10px)';
        } else {
            navbar.style.background = '#ffffff';
            navbar.style.backdropFilter = 'none';
        }
    }
}

function initializeTooltips() {
    // Simple tooltip implementation
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const text = e.target.getAttribute('data-tooltip');
    if (!text) return;

    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    document.body.appendChild(tooltip);

    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

function setupInfiniteScroll() {
    // Infinite scroll for book lists
    if (document.querySelector('.books-grid')) {
        window.addEventListener('scroll', function() {
            if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 1000) {
                loadMoreBooks();
            }
        });
    }
}

function loadMoreBooks() {
    // Prevent multiple simultaneous requests
    if (window.loadingMoreBooks) return;
    window.loadingMoreBooks = true;

    // Simulate loading more books
    setTimeout(() => {
        showToast('More books loaded!', 'info');
        window.loadingMoreBooks = false;
    }, 1000);
}

function trackBookView(bookId) {
    // Analytics tracking
    if (typeof gtag !== 'undefined') {
        gtag('event', 'book_view', {
            book_id: bookId,
            timestamp: new Date().toISOString()
        });
    }
    console.log(`Book viewed: ${bookId}`);
}

// ==================== API SIMULATION FUNCTIONS ====================
function simulateBorrowBook(bookId, duration) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.1) { // 90% success rate
                resolve({ success: true, bookId, duration });
            } else {
                reject(new Error('Book is currently unavailable'));
            }
        }, 1000);
    });
}

function simulateReturnBook(bookId, condition, notes) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.05) { // 95% success rate
                resolve({ success: true, bookId, condition, notes });
            } else {
                reject(new Error('Book ID not found in your borrowed books'));
            }
        }, 1000);
    });
}

function simulateAddToWishlist(bookId) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.1) { // 90% success rate
                resolve({ success: true, bookId });
            } else {
                reject(new Error('Book already in wishlist'));
            }
        }, 500);
    });
}

function simulateRemoveFromWishlist(bookId) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            if (Math.random() > 0.05) { // 95% success rate
                resolve({ success: true, bookId });
            } else {
                reject(new Error('Book not found in wishlist'));
            }
        }, 500);
    });
}

// ==================== EXPORT FOR TESTING ====================
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showToast,
        openModal,
        closeModal,
        addToWishlist,
        removeFromWishlist,
        viewBook,
        handleSearchInput
    };
}