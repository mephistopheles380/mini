document.addEventListener('DOMContentLoaded', function() {
    // Quote rotation
    const quotes = document.querySelectorAll('.quote');
    let currentQuote = 0;

    function rotateQuotes() {
        quotes.forEach(quote => quote.classList.remove('active'));
        quotes[currentQuote].classList.add('active');
        currentQuote = (currentQuote + 1) % quotes.length;
    }

    setInterval(rotateQuotes, 5000);
    rotateQuotes(); // Initial call

    // Form validation
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});