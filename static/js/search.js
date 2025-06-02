/**
 * Search suggestions functionality
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get search input elements
    const searchInputs = document.querySelectorAll('.main-form input[type="text"]');
    
    // Remove any existing suggestion containers
    const existingSuggestions = document.querySelectorAll('.search-suggestions');
    existingSuggestions.forEach(container => container.remove());
    
    searchInputs.forEach(function(searchInput) {
        // Remove any existing suggestions associated with this input
        const parentElement = searchInput.parentNode;
        const oldSuggestions = parentElement.querySelectorAll('.search-suggestions');
        oldSuggestions.forEach(el => el.remove());
        
        // Create suggestion container
        const suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'search-suggestions';
        suggestionsContainer.id = 'search-suggestions-' + Math.random().toString(36).substr(2, 9); // Unique ID
        searchInput.parentNode.style.position = 'relative';
        searchInput.parentNode.appendChild(suggestionsContainer);
        
        // Style the suggestions container - always full width
        suggestionsContainer.style.display = 'none';
        suggestionsContainer.style.position = 'absolute';
        suggestionsContainer.style.top = '100%';
        suggestionsContainer.style.left = '0';
        suggestionsContainer.style.right = '0';
        suggestionsContainer.style.backgroundColor = '#fff';
        suggestionsContainer.style.border = '1px solid #ccc';
        suggestionsContainer.style.borderTop = 'none';
        suggestionsContainer.style.maxHeight = '70vh';
        suggestionsContainer.style.overflowY = 'auto';
        suggestionsContainer.style.zIndex = '9999';
        suggestionsContainer.style.borderRadius = '0 0 8px 8px';
        suggestionsContainer.style.boxShadow = '0 5px 15px rgba(0, 0, 0, 0.2)';
        
        // Set up full-width styling
        function setupFullWidthSuggestions() {
            // Get the viewport width
            const viewportWidth = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
            
            // Position absolute but full width
            suggestionsContainer.style.width = viewportWidth + 'px';
            suggestionsContainer.style.maxWidth = viewportWidth + 'px';
            
            // Calculate offset to adjust position for full width
            const searchBarRect = searchInput.getBoundingClientRect();
            const leftOffset = searchBarRect.left;
            
            // Shift the container left to align with screen edge
            suggestionsContainer.style.marginLeft = `-${leftOffset}px`;
            
            // Ensure the container has a high z-index to appear above other elements
            suggestionsContainer.style.zIndex = '9999';
        }
        
        // Apply full-width styling when displaying suggestions
        window.addEventListener('resize', setupFullWidthSuggestions);
        
        // Debounce function for search input
        let timeoutId;
        const debounce = (callback, time = 300) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(callback, time);
        };
        
        // Hide all other suggestion containers when showing this one
        function hideOtherSuggestions() {
            document.querySelectorAll('.search-suggestions').forEach(container => {
                if (container.id !== suggestionsContainer.id) {
                    container.style.display = 'none';
                }
            });
        }
        
        // Handle input event
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            if (query.length < 2) {
                suggestionsContainer.style.display = 'none';
                return;
            }
            
            debounce(() => {
                fetchSuggestions(query, suggestionsContainer);
                setupFullWidthSuggestions();
                hideOtherSuggestions();
            });
        });
        
        // Hide suggestions on blur
        searchInput.addEventListener('blur', function() {
            // Delay to allow clicking on suggestions
            setTimeout(() => {
                suggestionsContainer.style.display = 'none';
            }, 200);
        });
        
        // Show suggestions on focus if there's a query
        searchInput.addEventListener('focus', function() {
            const query = this.value.trim();
            if (query.length >= 2) {
                fetchSuggestions(query, suggestionsContainer);
                setupFullWidthSuggestions();
                hideOtherSuggestions();
            }
        });
    });
    
    /**
     * Fetch search suggestions from the server
     */
    function fetchSuggestions(query, suggestionsContainer) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        
        fetch(`/api/search-suggestions/?q=${encodeURIComponent(query)}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            renderSuggestions(data, suggestionsContainer);
        })
        .catch(error => {
            console.error('Error fetching suggestions:', error);
        });
    }
    
    /**
     * Render suggestions in the suggestions container
     */
    function renderSuggestions(data, suggestionsContainer) {
        suggestionsContainer.innerHTML = '';
        
        if (data.count === 0) {
            const noResultsItem = document.createElement('div');
            noResultsItem.className = 'suggestion-item no-results';
            noResultsItem.textContent = 'No products found';
            noResultsItem.style.padding = '12px 15px';
            noResultsItem.style.color = '#666';
            noResultsItem.style.textAlign = 'center';
            noResultsItem.style.fontSize = '15px';
            suggestionsContainer.appendChild(noResultsItem);
        } else {
            data.suggestions.forEach(product => {
                const item = document.createElement('a');
                item.className = 'suggestion-item';
                item.href = `/product/${product.slug}`;
                
                // Style the item
                item.style.display = 'flex';
                item.style.alignItems = 'center';
                item.style.padding = '12px 15px';
                item.style.borderBottom = '1px solid #eee';
                item.style.textDecoration = 'none';
                item.style.color = '#333';
                
                // Add hover effect
                item.onmouseover = function() {
                    this.style.backgroundColor = '#f5f5f5';
                };
                item.onmouseout = function() {
                    this.style.backgroundColor = 'transparent';
                };
                
                // Product image
                const imageDiv = document.createElement('div');
                imageDiv.style.width = '40px';
                imageDiv.style.height = '40px';
                imageDiv.style.marginRight = '10px';
                imageDiv.style.flexShrink = '0';
                imageDiv.style.display = 'flex';
                imageDiv.style.alignItems = 'center';
                imageDiv.style.justifyContent = 'center';
                
                const image = document.createElement('img');
                image.src = product.image_url;
                image.alt = product.title;
                image.style.width = '100%';
                image.style.height = '100%';
                image.style.objectFit = 'contain';
                
                imageDiv.appendChild(image);
                
                // Product info
                const infoDiv = document.createElement('div');
                infoDiv.style.flex = '1';
                infoDiv.style.minWidth = '0'; // Important for text truncation
                
                const title = document.createElement('div');
                title.textContent = product.title;
                title.style.fontWeight = 'bold';
                title.style.fontSize = '14px';
                title.style.overflow = 'hidden';
                title.style.textOverflow = 'ellipsis';
                title.style.whiteSpace = 'nowrap';
                title.style.lineHeight = '1.3';
                
                infoDiv.appendChild(title);
                
                item.appendChild(imageDiv);
                item.appendChild(infoDiv);
                
                suggestionsContainer.appendChild(item);
            });
        }
        
        suggestionsContainer.style.display = 'block';
    }
}); 