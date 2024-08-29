const dayButton = document.getElementById('dayMode');
const autoButton = document.getElementById('autoMode');
const nightButton = document.getElementById('nightMode');
const storedTheme = localStorage.getItem('theme');
const storedMode = localStorage.getItem('mode');

if (storedMode === 'auto') {
    setTheme(getSystemTheme());
} else {
    setTheme(storedTheme || 'light');
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-bs-theme', theme);

    const body = document.body;
    if (theme === 'light') {
        body.classList.add('bg-body-tertiary');
    } else if (theme === 'dark') {
        body.classList.remove('bg-body-tertiary');
    }

    dayButton.classList.toggle('active', theme === 'light' && localStorage.getItem('mode') === 'manual');
    autoButton.classList.toggle('active', localStorage.getItem('mode') === 'auto');
    nightButton.classList.toggle('active', theme === 'dark' && localStorage.getItem('mode') === 'manual');
}

function getSystemTheme() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', event => {
    if (localStorage.getItem('mode') === 'auto') {
        setTheme(getSystemTheme());
    }
});

dayButton.addEventListener('click', () => {
    localStorage.setItem('theme', 'light');
    localStorage.setItem('mode', 'manual');
    setTheme('light');
});

nightButton.addEventListener('click', () => {
    localStorage.setItem('theme', 'dark');
    localStorage.setItem('mode', 'manual');
    setTheme('dark');
});

autoButton.addEventListener('click', () => {
    localStorage.setItem('mode', 'auto');
    setTheme(getSystemTheme());
});