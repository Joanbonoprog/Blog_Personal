(function () {
    'use strict';
    const html = document.documentElement;
    const btn = document.getElementById('themeToggle');
    const iconSun = document.getElementById('iconSun');
    const iconMoon = document.getElementById('iconMoon');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    function resolveTheme(theme) {
        if (theme === 'auto' || !theme) {
            return prefersDark ? 'dark' : 'light';
        }
        return theme;
    }

    function applyTheme(theme) {
        const resolved = resolveTheme(theme);
        html.setAttribute('data-theme', resolved);
        if (resolved === 'dark') {
            iconSun.style.display = 'block';
            iconMoon.style.display = 'none';
        } else {
            iconSun.style.display = 'none';
            iconMoon.style.display = 'block';
        }
    }

    const saved = localStorage.getItem('theme');
    applyTheme(saved || (prefersDark ? 'dark' : 'light'));

    if (btn) {
        btn.addEventListener('click', function () {
            const current = resolveTheme(html.getAttribute('data-theme'));
            const next = current === 'dark' ? 'light' : 'dark';
            applyTheme(next);
            localStorage.setItem('theme', next);
        });
    }

    const langForm = document.getElementById('langForm');
    const langSelect = langForm ? langForm.querySelector('select[name="language"]') : null;
    if (langSelect) {
        langSelect.addEventListener('change', function () {
            langForm.submit();
        });
    }
})();
