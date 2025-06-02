/**
 * Enhanced Pagination Loader Script
 * Handles pagination loaders with HTMX integration
 */
document.addEventListener('DOMContentLoaded', function() {
    // Log that the script has loaded
    console.log('Enhanced pagination loader script initialized');
    
    // Get all pagination links with HTMX attributes
    const paginationLinks = document.querySelectorAll('.pagination a[hx-get]');
    const paginationLoader = document.getElementById('pagination-loader');
    const filterForm = document.getElementById('filter-form');
    const filterIndicator = document.getElementById('filter-indicator');
    
    // Force show loader - use this when other methods fail
    function forceShowLoader(loaderId = '#pagination-loader') {
        const loader = document.querySelector(loaderId);
        if (loader) {
            // Force display style to ensure visibility
            loader.style.display = 'block';
            loader.classList.add('htmx-request');
            console.log(`Forced loader visibility for ${loaderId}`);
            
            // Scroll to products container for better UX
            const productsContainer = document.getElementById('products-container');
            if (productsContainer) {
                productsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }
    
    // Hide all loaders
    function hideAllLoaders() {
        document.querySelectorAll('#pagination-loader, #filter-indicator, .htmx-indicator').forEach(function(loader) {
            loader.classList.remove('htmx-request');
            loader.style.display = 'none';
        });
        console.log('All loaders hidden');
    }
    
    // Add click event listeners to all pagination links
    paginationLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            console.log('Pagination link clicked');
            forceShowLoader('#pagination-loader');
        });
    });
    
    // Handle filter form inputs
    if (filterForm) {
        // Handle checkbox changes
        const checkboxes = filterForm.querySelectorAll('input[type=checkbox]');
        checkboxes.forEach(function(checkbox) {
            checkbox.addEventListener('change', function() {
                console.log('Filter checkbox changed');
                forceShowLoader('#pagination-loader');
            });
        });
        
        // Handle price inputs
        const priceInputs = filterForm.querySelectorAll('input[type=number]');
        priceInputs.forEach(function(input) {
            input.addEventListener('change', function() {
                console.log('Price input changed');
                forceShowLoader('#pagination-loader');
            });
        });
    }
    
    // Handle filter reset button
    const resetButton = document.getElementById('reset-filters');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            console.log('Reset filters clicked');
            forceShowLoader('#pagination-loader');
        });
    }
    
    // HTMX event listeners for request lifecycle
    
    // Before any HTMX request
    document.body.addEventListener('htmx:beforeRequest', function(event) {
        console.log('HTMX request starting');
        const target = event.detail.target;
        if (target && target.id === 'products-container') {
            forceShowLoader('#pagination-loader');
        }
    });
    
    // After HTMX content swap
    document.body.addEventListener('htmx:afterSwap', function(event) {
        console.log('Content swapped');
        
        // Re-attach event listeners to new pagination links
        const newPaginationLinks = document.querySelectorAll('.pagination a[hx-get]');
        newPaginationLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                console.log('New pagination link clicked');
                forceShowLoader('#pagination-loader');
            });
        });
        
        // Hide loaders after content is swapped
        hideAllLoaders();
    });
    
    // After any HTMX request completes
    document.body.addEventListener('htmx:afterRequest', function() {
        console.log('HTMX request completed');
        // Hide loaders after request completes
        hideAllLoaders();
    });
    
    // Handle HTMX errors
    document.body.addEventListener('htmx:responseError', function(event) {
        console.error('HTMX request failed:', event.detail.xhr.status);
        hideAllLoaders(); // Using the existing hideAllLoaders function
        
        // Show error notification
        if (typeof alertify !== 'undefined') {
            alertify.error('Error loading content. Please try again.');
        } else {
            console.error('Error loading content. Please try again.');
        }
    });
});
