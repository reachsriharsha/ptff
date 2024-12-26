const toggleButton = document.getElementById('darkModeToggle');

toggleButton.addEventListener('click', () => {
    document.body.classList.toggle('dark-mode');
    // Optionally, store user preference in local storage
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
});

// Check if dark mode was previously enabled
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}