(function () {
    'use strict';

    function getDesiredPerPage() {
        var w = window.innerWidth;
        if (w < 768) return 5;
        if (w < 992) return 10;
        if (w < 1400) return 15;
        if (w < 1921) return 20;
        return 25;
    }

    function getCookie(name) {
        var value = '; ' + document.cookie;
        var parts = value.split('; ' + name + '=');
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    function navigate(callback) {
        var url = new URL(window.location.href);
        callback(url.searchParams);
        url.searchParams.delete('page');
        window.location.search = url.searchParams.toString();
    }

    function applyDesiredPerPage() {
        var desired = getDesiredPerPage();
        var current = parseInt(getCookie('posts_per_page'), 10) || 15;
        if (String(current) === String(desired)) return;

        var expiry = new Date();
        expiry.setFullYear(expiry.getFullYear() + 1);
        document.cookie = 'posts_per_page=' + desired + '; path=/; expires=' + expiry.toUTCString() + '; SameSite=Lax';

        var url = new URL(window.location.href);
        url.searchParams.delete('page');
        window.location.replace(url.toString());
    }

    document.addEventListener('DOMContentLoaded', applyDesiredPerPage);

    var resizeTimer;
    window.addEventListener('resize', function () {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(applyDesiredPerPage, 300);
    });

    var searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('keydown', function (event) {
            if (event.key !== 'Enter') return;
            var value = this.value.trim();
            navigate(function (p) {
                if (value) {
                    p.set('q', value);
                } else {
                    p.delete('q');
                }
            });
        });
    }

    function setupSelect(name, paramName) {
        var select = document.getElementById(name);
        if (!select) return;
        select.addEventListener('change', function () {
            navigate(function (p) {
                if (select.value) {
                    p.set(paramName, select.value);
                } else {
                    p.delete(paramName);
                }
                if (paramName === 'year') {
                    p.delete('month');
                }
            });
        });
    }

    setupSelect('tagFilter', 'tag');
    setupSelect('yearFilter', 'year');
    setupSelect('monthFilter', 'month');
    setupSelect('orderFilter', 'order');

    var resetButtons = document.querySelectorAll('[data-reset]');
    resetButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var param = this.getAttribute('data-reset');
            navigate(function (p) {
                if (param === 'year') {
                    p.delete('year');
                    p.delete('month');
                } else {
                    p.delete(param);
                }
            });
        });
    });
})();
