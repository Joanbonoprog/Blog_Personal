(function () {
    'use strict';

    const btn = document.getElementById('copyLinkBtn');
    if (!btn) return;

    const labelEl = document.getElementById('copyLabel');
    const iconEl = document.getElementById('copyIcon');
    const originalLabel = labelEl.textContent;
    const originalIcon = iconEl.innerHTML;
    const copiedLabel = btn.dataset.copiedLabel;
    const copiedIcon = '<polyline points="20 6 9 17 4 12"></polyline>';

    btn.addEventListener('click', function () {
        navigator.clipboard.writeText(window.location.href).then(function () {
            labelEl.textContent = copiedLabel;
            iconEl.innerHTML = copiedIcon;
            setTimeout(function () {
                labelEl.textContent = originalLabel;
                iconEl.innerHTML = originalIcon;
            }, 2000);
        });
    });
})();
