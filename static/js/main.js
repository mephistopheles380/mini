// Add smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Filter functionality
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[type="text"]');
    const selectFilters = document.querySelectorAll('select');

    if (searchInput) {
        searchInput.addEventListener('input', filterBooks);
    }

    selectFilters.forEach(filter => {
        filter.addEventListener('change', filterBooks);
    });

    function filterBooks() {
        // Add filtering logic here
        console.log('Filtering books...');
    }
});

// Handle mobile menu overlay click
document.addEventListener('DOMContentLoaded', function() {
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarCollapse) {
        navbarCollapse.addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('show');
            }
        });
    }
});