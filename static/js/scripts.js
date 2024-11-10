document.addEventListener('DOMContentLoaded', function() {
    // Flash message auto-hide
    setTimeout(function() {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(function(message) {
            message.style.display = 'none';
        });
    }, 3000);
});