document.addEventListener('DOMContentLoaded', () => {
    const authorizeButton = document.getElementById('authorize');
    authorizeButton.addEventListener('click', () => {
        window.location.href = '/login';
    });
});