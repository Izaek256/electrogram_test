// Unified pagination system for the store
document.addEventListener('DOMContentLoaded', function() {
    // Initialize pagination for all sections
    initializePagination();
});

/**
 * Initialize pagination listeners for all sections
 */
function initializePagination() {
    // Make all daily offer items visible
    document.querySelectorAll('.daily-offer-item').forEach(item => {
        if (item.style.display === 'none') {
            item.style.display = 'block';
        }
    });

    // Attach click event listeners to all pagination elements
    document.querySelectorAll('.pagination .page-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            const section = this.closest('[data-section]')?.getAttribute('data-section');
            if (!section) {
                console.error('Section parameter is missing. Make sure data-section attribute is set on the pagination container.');
                return;
            }
            handleSectionPagination(section, page);
        });
    });
}

function handleSectionPagination(section, page) {
    const sectionContainer = document.querySelector(`[data-section-container="${section}"]`);
    if (!sectionContainer) {
        console.error(`Section container not found for section: ${section}`);
        return;
    }
    const productsContainer = sectionContainer.querySelector('.products-container');
    if (!productsContainer) {
        console.error(`Products container not found for section: ${section}`);
        return;
    }
    productsContainer.classList.add('loading');
    fetch(`/api/products/?section=${section}&page=${page}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.html) {
            // If HTML is provided, just use it
            productsContainer.parentElement.innerHTML = data.html;
            initializePagination();
        } else if (data.products && data.pagination) {
            // Otherwise, render products and pagination from data
            renderProductsAndPagination(productsContainer, data.products, data.pagination, section);
            initializePagination();
        } else {
            console.error('No HTML or products data received from server');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(() => {
        productsContainer.classList.remove('loading');
    });
}

// Helper function to render products and pagination
function renderProductsAndPagination(productsContainer, products, pagination, section) {
    // Clear products
    productsContainer.innerHTML = '';
    // Render product cards
    renderProducts(productsContainer, products, section);

    // Find the existing pagination nav for this section
    let paginationNav = productsContainer.parentElement.querySelector('nav[data-section]');
    if (!paginationNav) {
        // If not found, create one
        paginationNav = document.createElement('nav');
        paginationNav.setAttribute('data-section', section);
        paginationNav.className = 'd-flex justify-content-center mt-4';
        productsContainer.parentElement.appendChild(paginationNav);
    }

    // Build pagination HTML
    let html = '<ul class="pagination">';
    if (pagination.has_previous) {
        html += `<li class="page-item"><a class="page-link" href="#" data-page="${pagination.previous_page_number}">&laquo;</a></li>`;
    }
    for (let i = 1; i <= pagination.total_pages; i++) {
        html += `<li class="page-item${i === pagination.current_page ? ' active' : ''}"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
    }
    if (pagination.has_next) {
        html += `<li class="page-item"><a class="page-link" href="#" data-page="${pagination.next_page_number}">&raquo;</a></li>`;
    }
    html += '</ul>';
    paginationNav.innerHTML = html;
}

/**
 * Initialize card layouts
 */
function initializeCardLayouts() {
    const cards = document.querySelectorAll('.product-card');
    cards.forEach(card => {
        // Ensure proper image sizing
        const img = card.querySelector('.product-image img');
        if (img) {
            img.style.width = 'auto';
            img.style.height = 'auto';
            img.style.objectFit = 'contain';
        }
        
        // Ensure proper content layout
        const content = card.querySelector('.product-content');
        if (content) {
            content.style.display = 'flex';
            content.style.flexDirection = 'column';
        }
    });

    // Ensure proper grid layout
    const container = document.querySelector('.products-grid.products-container');
    if (container) {
        container.classList.add('row');
        container.classList.add('is-grid-active');
        
        // Ensure proper column classes
        container.querySelectorAll('.product-card').forEach(card => {
            const columnDiv = card.closest('[class*="col-"]');
            if (columnDiv) {
                columnDiv.classList.add('col-xl-4', 'col-lg-4', 'col-md-6', 'col-sm-12', 'col-12', 'mb-4');
            }
        });
    }
}

/**
 * Attach pagination handlers
 */
function attachPaginationHandlers() {
    document.querySelectorAll('.pagination .page-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = this.getAttribute('data-page');
            const section = this.closest('[data-section]')?.getAttribute('data-section');
            
            if (!section) {
                console.error('Section parameter is missing');
                return;
            }
            
            loadPageContent(section, page);
        });
    });
}

/**
 * Render categories in the container
 * @param {HTMLElement} container - Container to render categories in
 * @param {Array} categories - Categories data
 */
function renderCategories(container, categories) {
    categories.forEach(category => {
        const categoryElement = document.createElement('div');
        categoryElement.className = 'col-lg-2 col-md-4 col-sm-6 u-s-m-b-30';
        categoryElement.innerHTML = `
            <div class="promotion-o">
                <div class="aspect aspect--bg-grey aspect--square">
                    <img class="aspect__img" src="${category.image_url || category.image}" alt="${category.title}">
                </div>
                <div class="promotion-o__content">
                    <a class="promotion-o__link btn--e-white-brand" 
                       href="/category/${category.cid}/">${category.title}</a>
                </div>
            </div>
        `;
        container.appendChild(categoryElement);
    });
}

/**
 * Render products in the container
 * @param {HTMLElement} container - Container to render products in
 * @param {Array} products - Products data
 * @param {string} section - Section identifier
 */
function renderProducts(container, products, section) {
    // Special handling for daily offer section to ensure 2 rows (4 products) per page
    if (section === 'daily-offer') {
        renderDailyOfferProducts(container, products);
        return;
    }
    
    products.forEach(product => {
        // Format price with commas if it's a number
        const formattedPrice = typeof product.price === 'number' ? 
            product.price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") : 
            product.price;
        
        // Get proper image URL
        const imageUrl = product.image_url || product.get_image_url;
        
        // Create appropriate product element based on section
        const productElement = createProductElement(product, formattedPrice, imageUrl, section);
        container.appendChild(productElement);
    });
}

/**
 * Special handler for rendering daily offer products
 * @param {HTMLElement} container - Container to render products in
 * @param {Array} products - Products data
 */
function renderDailyOfferProducts(container, products) {
    // Clear the container first
    container.innerHTML = '';
    
    // Make sure the container has the daily-offer-grid class
    container.classList.remove('row');
    if (!container.classList.contains('daily-offer-grid')) {
        container.classList.add('daily-offer-grid');
    }
    
    // Reset any inline styles that might be affecting the grid layout
    container.style.display = 'grid';
    container.style.gridTemplateColumns = 'repeat(2, 1fr)';
    container.style.gap = '15px';
    
    // Add products to the container
    products.forEach(product => {
        // Format price with commas if it's a number
        const formattedPrice = typeof product.price === 'number' ? 
            product.price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",") : 
            product.price;
        
        // Get proper image URL
        const imageUrl = product.image_url || product.get_image_url;
        
        // Get category information
        const categoryId = product.category.cid || (typeof product.category === 'object' ? product.category.id : product.category);
        const categoryTitle = product.category.title || (typeof product.category === 'object' ? product.category.name : product.category);
        
        // Create product element
        const productDiv = document.createElement('div');
        productDiv.className = 'daily-offer-item';
        productDiv.style.display = 'block'; // Ensure the item is visible
        productDiv.innerHTML = `
            <div class="product-short u-h-100">
                <div class="product-short__container">
                    <div class="product-short__img-wrap">
                        <a class="aspect aspect--bg-grey-fb aspect--square u-d-block" href="/product/${product.slug}/">
                            <img class="aspect__img product-short__img" src="${imageUrl}" alt="${product.title}">
                        </a>
                    </div>
                    <div class="product-short__info">
                        <span class="product-short__price">Ugshs. ${formattedPrice} /=</span>
                        <span class="product-short__name">
                            <a href="/product/${product.slug}/">${product.title}</a>
                        </span>
                        <span class="product-short__category">
                            <a href="/category/${categoryId}/">${categoryTitle}</a>
                        </span>
                    </div>
                </div>
            </div>
        `;
        container.appendChild(productDiv);
    });
}

/**
 * Create a product element based on section type
 * @param {Object} product - Product data
 * @param {string} formattedPrice - Price with formatting
 * @param {string} imageUrl - URL of the product image
 * @param {string} section - Section identifier
 * @returns {HTMLElement} - Product element
 */
function createProductElement(product, formattedPrice, imageUrl, section) {
    const productDiv = document.createElement('div');
    
    // Handle category data formatting
    const categoryId = product.category.cid || (typeof product.category === 'object' ? product.category.id : product.category);
    const categoryTitle = product.category.title || (typeof product.category === 'object' ? product.category.name : product.category);
    
    // Different HTML structure based on section
    if (section === 'recent-products') {
        productDiv.className = 'col-lg-3 col-md-4 col-sm-6 u-s-m-b-30';
        productDiv.innerHTML = `
            <div class="product-r u-h-100">
                <div class="product-r__container">
                    <a class="aspect aspect--bg-grey aspect--square u-d-block"
                        href="/product/${product.slug}/">
                        <img class="aspect__img" src="${imageUrl}" alt="${product.title}">
                    </a>
                </div>
                <div class="product-r__info-wrap">
                    <span class="product-r__category">
                        <a href="/category/${categoryId}/">${categoryTitle}</a>
                    </span>
                    <div class="product-r__n-p-wrap">
                        <span class="product-r__name">
                            <a href="/product/${product.slug}/">${product.title}</a>
                        </span>
                    </div>
                    <div class="product-r__price-container" style="display: flex; align-items: center;">
                        <span class="product-r__price">Ugshs.</span>
                        <span class="product-r__price" id="current_price${product.id}">${formattedPrice}</span>
                        <span class="product-r__price">/=</span>
                    </div>
                </div>
            </div>
        `;
    } else if (section === 'best-selling') {
        productDiv.className = 'col-xl-3 col-lg-4 col-md-6 col-sm-6 u-s-m-b-30 filter__item';
        productDiv.innerHTML = `
            <div class="product-bs h-100 shadow-sm rounded">
                <div class="product-bs__container p-3">
                    <div class="product-bs__wrap">
                        <a class="aspect aspect--bg-grey aspect--square u-d-block"
                            href="/product/${product.slug}/">
                            <img class="aspect__img rounded" src="${imageUrl}"
                                alt="${product.title}">
                        </a>
                    </div>
                    <div class="product-bs__info mt-3">
                        <span class="product-bs__category d-block text-muted mb-2">
                            <a href="/category/${categoryId}/">${categoryTitle}</a>
                        </span>
                        <h3 class="product-bs__name h6 mb-2">
                            <a href="/product/${product.slug}/">${product.title}</a>
                        </h3>
                        <span class="product-r__price fw-bold">Ugshs. ${formattedPrice} /=</span>
                    </div>
                </div>
            </div>
        `;
    } else if (section === 'monthly-products') {
        productDiv.className = 'col-lg-3 col-md-4 col-sm-6 u-s-m-b-30';
        productDiv.innerHTML = `
            <div class="product-short h-100">
                <div class="product-short__container">
                    <div class="product-short__img-wrap">
                        <a class="aspect aspect--bg-grey-fb aspect--square u-d-block" href="/product/${product.slug}/">
                            <img class="aspect__img product-short__img" src="${imageUrl}" alt="${product.title}">
                        </a>
                    </div>
                    <div class="product-short__info">
                        <span class="product-short__price">Ugshs. ${formattedPrice} /=</span>
                        <span class="product-short__name">
                            <a href="/product/${product.slug}/">${product.title}</a>
                        </span>
                        <span class="product-short__category">
                            <a href="/category/${categoryId}/">${categoryTitle}</a>
                        </span>
                    </div>
                </div>
            </div>
        `;
    } else {
        // Default case for any other section
        productDiv.className = 'col-lg-3 col-md-4 col-sm-6 u-s-m-b-30';
        productDiv.innerHTML = `
            <div class="product-short h-100">
                <div class="product-short__container">
                    <div class="product-short__img-wrap">
                        <a class="aspect aspect--bg-grey-fb aspect--square u-d-block" href="/product/${product.slug}/">
                            <img class="aspect__img product-short__img" src="${imageUrl}" alt="${product.title}">
                        </a>
                    </div>
                    <div class="product-short__info">
                        <span class="product-short__price">Ugshs. ${formattedPrice} /=</span>
                        <span class="product-short__name">
                            <a href="/product/${product.slug}/">${product.title}</a>
                        </span>
                        <span class="product-short__category">
                            <a href="/category/${categoryId}/">${categoryTitle}</a>
                        </span>
                    </div>
                </div>
            </div>
        `;
    }
    
    return productDiv;
}

/**
 * Update pagination UI
 * @param {HTMLElement} container - Pagination container
 * @param {Object} data - Pagination data
 */
function updatePaginationUI(container, data) {
    // Find the pagination list
    let paginationList = container.querySelector('.pagination');
    if (!paginationList) {
        console.error('Pagination list not found in container');
        return;
    }
    
    // Clear existing pagination items
    paginationList.innerHTML = '';
    
    // Previous page button
    if (data.has_previous) {
        const prevItem = document.createElement('li');
        prevItem.className = 'page-item';
        prevItem.innerHTML = `<a class="page-link" href="#" data-page="${data.previous_page_number}">&laquo;</a>`;
        paginationList.appendChild(prevItem);
    }
    
    // Page number buttons
    const pageRange = data.paginator?.page_range || [];
    const totalPages = data.total_pages || pageRange.length;
    const currentPage = data.current_page || data.number;
    
    // Generate page numbers
    for (let i = 1; i <= totalPages; i++) {
        const isActive = i === currentPage;
        const pageItem = document.createElement('li');
        pageItem.className = `page-item${isActive ? ' active' : ''}`;
        pageItem.innerHTML = `<a class="page-link" href="#" data-page="${i}">${i}</a>`;
        paginationList.appendChild(pageItem);
    }
    
    // Next page button
    if (data.has_next) {
        const nextItem = document.createElement('li');
        nextItem.className = 'page-item';
        nextItem.innerHTML = `<a class="page-link" href="#" data-page="${data.next_page_number}">&raquo;</a>`;
        paginationList.appendChild(nextItem);
    }
}

/**
 * Handle category section updates
 * @param {string} section - Section identifier
 * @param {number} page - Page number
 */
function handleCategorySection(section, page) {
    const container = document.querySelector(`[data-section-container="${section}"]`);
    if (!container) return;

    // Show loading state
    container.classList.add('loading');

    // Make AJAX request
    fetch(`/api/products/?section=${section}&page=${page}`, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Update container with new content
        container.innerHTML = data.html;
        
        // Initialize Swiper for mobile carousel if it exists
        const swiperContainer = container.querySelector('.swiper-container');
        if (swiperContainer) {
            new Swiper(swiperContainer, {
                slidesPerView: 'auto',
                spaceBetween: 20,
                navigation: {
                    nextEl: '.swiper-button-next',
                    prevEl: '.swiper-button-prev',
                },
                pagination: {
                    el: '.swiper-pagination',
                    clickable: true,
                },
                breakpoints: {
                    768: {
                        enabled: false
                    }
                }
            });
        }
        
        // Remove loading state
        container.classList.remove('loading');
    })
    .catch(error => {
        console.error('Error:', error);
        container.classList.remove('loading');
    });
}
