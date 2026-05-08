import { browser } from '$app/environment';

// Read initial theme from localStorage or system preference
function getInitialTheme(): 'dark' | 'light' {
    if (browser) {
        const saved = localStorage.getItem('theme');
        if (saved === 'dark' || saved === 'light') return saved;
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'dark';
}

let current = $state<'dark' | 'light'>(getInitialTheme());

export const theme = {
    get value() { return current; },
    get isDark() { return current === 'dark'; },
    toggle() {
        current = current === 'dark' ? 'light' : 'dark';
        if (browser) {
            localStorage.setItem('theme', current);
            document.documentElement.classList.toggle('dark', current === 'dark');
        }
    },
    init() {
        if (browser) {
            document.documentElement.classList.toggle('dark', current === 'dark');
        }
    }
};
