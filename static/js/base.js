// AJAX cart quantity update
document.addEventListener('DOMContentLoaded', function() {
    // Handle cart quantity update buttons
    document.querySelectorAll('a[data-cart-action]').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const action = this.getAttribute('data-cart-action');
            const productId = this.getAttribute('data-product-id');
            const url = this.getAttribute('href');
            
            // Disable all buttons in the same group and save their original HTML FIRST
            const group = this.closest('[data-cart-controls]');
            const buttonOriginals = new Map();
            if (group) {
                group.querySelectorAll('a').forEach(btn => {
                    buttonOriginals.set(btn, btn.innerHTML);
                    btn.style.pointerEvents = 'none';
                });
            }
            
            // Show loading state AFTER saving originals
            const originalHTML = this.innerHTML;
            this.innerHTML = '<i class="bi bi-arrow-repeat spin"></i>';
            this.style.pointerEvents = 'none';
            
            // Make AJAX request
            fetch(url, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update quantity display
                    const quantityElements = document.querySelectorAll(`[data-product-quantity="${productId}"]`);
                    quantityElements.forEach(quantityElement => {
                        if (data.quantity > 0) {
                            quantityElement.textContent = data.quantity;
                        } else {
                            quantityElement.textContent = '0';
                        }
                    });
                    
                    // Handle cart controls visibility
                    const cartControls = document.querySelector(`[data-cart-controls="${productId}"]`);
                    const addButton = document.querySelector(`[data-add-button="${productId}"]`);
                    
                    if (data.quantity > 0) {
                        if (cartControls) cartControls.style.display = '';
                        if (addButton) addButton.style.display = 'none';
                    } else {
                        if (cartControls) {
                            cartControls.style.display = 'none';
                            // Restore all buttons in cartControls
                            cartControls.querySelectorAll('a').forEach(btn => {
                                btn.style.pointerEvents = 'auto';
                            });
                        }
                        if (addButton) {
                            // Remove inline display style to show the button
                            addButton.style.removeProperty('display');
                            addButton.style.pointerEvents = 'auto';
                            addButton.style.cursor = 'pointer';
                            // Ensure addButton has correct content (in case it was modified)
                            if (!addButton.innerHTML.includes('Add to Cart')) {
                                addButton.innerHTML = 'Add to Cart';
                            }
                            // Remove any disabled attribute if present
                            addButton.removeAttribute('disabled');
                        }
                    }
                    
                    // Restore button after visibility changes
                    // First restore the clicked button
                    this.innerHTML = originalHTML;
                    this.style.pointerEvents = 'auto';
                    
                    // Then restore all other buttons in the group (but not the clicked one)
                    if (group) {
                        group.querySelectorAll('a').forEach(btn => {
                            btn.style.pointerEvents = 'auto';
                            // Restore original content for all buttons except the one we clicked
                            if (btn !== this && buttonOriginals.has(btn)) {
                                btn.innerHTML = buttonOriginals.get(btn);
                            }
                        });
                    }
                    
                    // If on cart page, reload to update totals
                    if (window.location.pathname.includes('/cart/')) {
                        setTimeout(() => {
                            window.location.reload();
                        }, 500);
                    }
                    
                    // Show success message
                    showNotification(data.message, 'success');
                } else {
                    // Restore button on error
                    this.innerHTML = originalHTML;
                    this.style.pointerEvents = 'auto';
                    if (group) {
                        group.querySelectorAll('a').forEach(btn => {
                            btn.style.pointerEvents = 'auto';
                            // Restore original content for all buttons except the one we clicked
                            if (btn !== this && buttonOriginals.has(btn)) {
                                btn.innerHTML = buttonOriginals.get(btn);
                            }
                        });
                    }
                    // Show warning message
                    showNotification(data.message, 'warning');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                this.innerHTML = originalHTML;
                this.style.pointerEvents = 'auto';
                if (group) {
                    group.querySelectorAll('a').forEach(btn => {
                        btn.style.pointerEvents = 'auto';
                        // Restore original content for all buttons except the one we clicked
                        if (btn !== this && buttonOriginals.has(btn)) {
                            btn.innerHTML = buttonOriginals.get(btn);
                        }
                    });
                }
                showNotification('An error occurred. Please try again.', 'danger');
            });
        });
    });
    
    // Handle "Add to Cart" buttons
    document.querySelectorAll('a[data-add-button]').forEach(function(link) {
        if (!link.hasAttribute('data-cart-action')) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const productId = this.getAttribute('data-add-button');
                const url = this.getAttribute('href');
                
                // Show loading state
                const originalHTML = this.innerHTML;
                this.innerHTML = '<i class="bi bi-arrow-repeat spin"></i>';
                this.style.pointerEvents = 'none';
                
                // Make AJAX request
                fetch(url, {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Hide "Add to Cart" button and show quantity controls
                        const cartControls = document.querySelector(`[data-cart-controls="${productId}"]`);
                        const addButton = document.querySelector(`[data-add-button="${productId}"]`);
                        
                        if (cartControls) {
                            cartControls.style.display = '';
                            const quantityElement = cartControls.querySelector(`[data-product-quantity="${productId}"]`);
                            if (quantityElement) {
                                quantityElement.textContent = data.quantity;
                            }
                        }
                        if (addButton) addButton.style.display = 'none';
                        
                        showNotification(data.message, 'success');
                    } else {
                        this.innerHTML = originalHTML;
                        this.style.pointerEvents = 'auto';
                        showNotification(data.message, 'warning');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.innerHTML = originalHTML;
                    this.style.pointerEvents = 'auto';
                    showNotification('An error occurred. Please try again.', 'danger');
                });
            });
        }
    });
});

// Show notification function
function showNotification(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3`;
    alertDiv.style.zIndex = '9999';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Add spin animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .spin {
        animation: spin 1s linear infinite;
    }
`;
document.head.appendChild(style);

