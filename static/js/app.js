/**
 * ComPaye Tarjetas — Client Interaction Script
 *
 * Handles:
 *  - Accessible <dialog> delete confirmation
 *  - Seamless AJAX stock +/- updates (preserves scroll, updates badges & ARIA live region)
 *  - Photo file preview
 *  - Inline container edit toggle
 *  - Smart flash auto-dismiss (pauses on hover/focus)
 */

(function () {
    'use strict';

    const announcer = document.getElementById('live-announcer');

    function announce(text) {
        if (!announcer) return;
        announcer.textContent = '';
        window.setTimeout(function () {
            announcer.textContent = text;
        }, 30);
    }


    // =================================================================
    // ACCESSIBLE CONFIRMATION DIALOG
    // =================================================================

    const dialog    = document.getElementById('confirm-dialog');
    const titleEl   = document.getElementById('confirm-title');
    const msgEl     = document.getElementById('confirm-message');
    const okBtn     = document.getElementById('confirm-ok');
    const cancelBtn = document.getElementById('confirm-cancel');
    let pendingForm = null;

    function openConfirm(btn, form) {
        if (!dialog || typeof dialog.showModal !== 'function') {
            if (window.confirm(btn.getAttribute('data-confirm'))) {
                form.submit();
            }
            return;
        }

        titleEl.textContent = btn.getAttribute('data-confirm-title') || 'Confirmar acción';
        msgEl.textContent   = btn.getAttribute('data-confirm') || '¿Está seguro de continuar?';
        okBtn.textContent   = btn.getAttribute('data-confirm-action') || 'Eliminar';
        pendingForm = form;
        dialog.showModal();
        cancelBtn.focus();
    }

    if (okBtn && dialog) {
        okBtn.addEventListener('click', function () {
            const formToSubmit = pendingForm;
            pendingForm = null;
            dialog.close();
            if (formToSubmit) formToSubmit.submit();
        });
    }

    if (cancelBtn && dialog) {
        cancelBtn.addEventListener('click', function () {
            pendingForm = null;
            dialog.close();
        });
    }

    if (dialog) {
        dialog.addEventListener('click', function (e) {
            if (e.target === dialog) {
                pendingForm = null;
                dialog.close();
            }
        });
    }

    document.addEventListener('click', function (e) {
        const btn = e.target.closest('[data-confirm]');
        if (!btn || btn.disabled) return;

        e.preventDefault();
        const form = btn.closest('form');
        if (form) openConfirm(btn, form);
    });


    // =================================================================
    // AJAX STOCK +/- CONTROLS (no page jump)
    // =================================================================

    function updateBadgeClass(badge, estado, label) {
        if (!badge) return;
        badge.classList.remove('badge-danger', 'badge-warning', 'badge-success');
        if (estado === 'agotado') {
            badge.classList.add('badge-danger');
        } else if (estado === 'bajo') {
            badge.classList.add('badge-warning');
        } else {
            badge.classList.add('badge-success');
        }
        badge.textContent = label;
    }

    document.addEventListener('submit', function (e) {
        const form = e.target.closest('.js-stock-form');
        if (!form || !window.fetch) return;

        const submitter = e.submitter;
        if (!submitter || !submitter.name) return;

        e.preventDefault();

        const formData = new FormData(form);
        formData.set(submitter.name, submitter.value);

        const buttons = form.querySelectorAll('button[type="submit"]');
        buttons.forEach(function (b) { b.disabled = true; });

        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
            },
            body: formData,
        })
            .then(function (resp) {
                if (!resp.ok) throw new Error('HTTP ' + resp.status);
                return resp.json();
            })
            .then(function (data) {
                if (!data.ok) throw new Error('Update failed');

                const scope = form.closest('[data-card-item], [data-card-row]') || document;
                const countEl = form.querySelector('.js-stock-count');
                if (countEl) countEl.textContent = data.stock;

                const inlineEl = scope.querySelector('.js-stock-inline');
                if (inlineEl) inlineEl.textContent = data.stock;

                const badgeEl = scope.querySelector('.js-stock-badge');
                updateBadgeClass(badgeEl, data.estado, data.estado_label);

                if (scope.matches && scope.matches('[data-card-item]')) {
                    scope.classList.toggle('card-out-of-stock', data.stock === 0);
                }
                if (scope.matches && scope.matches('[data-card-row]')) {
                    scope.classList.toggle('row-out-of-stock', data.stock === 0);
                }

                const decBtn = form.querySelector('button[value="decrement"]');
                const incBtn = form.querySelector('button[value="increment"]');
                if (decBtn) decBtn.disabled = data.stock <= 0;
                if (incBtn) incBtn.disabled = false;

                announce('Stock actualizado a ' + data.stock + ' piezas. Estado: ' + data.estado_label + '.');
            })
            .catch(function () {
                // Graceful fallback to standard POST
                buttons.forEach(function (b) { b.disabled = false; });
                form.classList.remove('js-stock-form');
                const hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = submitter.name;
                hidden.value = submitter.value;
                form.appendChild(hidden);
                form.submit();
            });
    });


    // =================================================================
    // PHOTO FILE PREVIEW
    // =================================================================

    window.previewPhoto = function (input) {
        if (!input.files || !input.files[0]) return;

        const file = input.files[0];
        const reader = new FileReader();

        reader.onload = function (e) {
            let previewImg = document.getElementById('photo-preview');
            const container = document.getElementById('photo-preview-container');

            if (!previewImg && container) {
                previewImg = document.createElement('img');
                previewImg.id = 'photo-preview';
                previewImg.alt = 'Vista previa de la tarjeta';
                previewImg.className = 'photo-preview';
                container.appendChild(previewImg);
            }

            if (container) container.hidden = false;
            if (previewImg) previewImg.src = e.target.result;
        };

        reader.readAsDataURL(file);

        const label = input.nextElementSibling;
        if (label && label.classList.contains('btn-file-label')) {
            const span = label.querySelector('span');
            if (span) span.textContent = file.name;
        }
    };


    // =================================================================
    // CONTAINER INLINE EDIT TOGGLE
    // =================================================================

    document.addEventListener('click', function (e) {
        const toggleBtn = e.target.closest('.js-edit-toggle');
        if (!toggleBtn) return;

        const id = toggleBtn.getAttribute('data-edit-id');
        const editRow = document.getElementById('edit-row-' + id);
        if (!editRow) return;

        const isHidden = editRow.hidden;
        editRow.hidden = !isHidden;

        const triggers = document.querySelectorAll('.js-edit-toggle[data-edit-id="' + id + '"]');
        triggers.forEach(function (t) {
            if (t.hasAttribute('aria-expanded')) {
                t.setAttribute('aria-expanded', isHidden ? 'true' : 'false');
            }
        });

        if (isHidden) {
            const firstInput = editRow.querySelector('input[name="nombre"]');
            if (firstInput) firstInput.focus();
        }
    });

    document.addEventListener('keydown', function (e) {
        if (e.key !== 'Escape') return;
        const openRow = e.target.closest('.edit-row');
        if (!openRow) return;
        openRow.hidden = true;
        const id = openRow.id.replace('edit-row-', '');
        const btn = document.querySelector('.js-edit-toggle[aria-expanded][data-edit-id="' + id + '"]');
        if (btn) {
            btn.setAttribute('aria-expanded', 'false');
            btn.focus();
        }
    });


    // =================================================================
    // AUTO-DISMISS FLASH MESSAGES (pauses while hovered/focused)
    // =================================================================

    document.querySelectorAll('.flash').forEach(function (flash) {
        let timer = null;

        function scheduleDismiss() {
            timer = window.setTimeout(function () {
                flash.style.opacity = '0';
                window.setTimeout(function () {
                    flash.remove();
                }, 250);
            }, 7000);
        }

        flash.addEventListener('mouseenter', function () {
            if (timer) window.clearTimeout(timer);
        });
        flash.addEventListener('focusin', function () {
            if (timer) window.clearTimeout(timer);
        });
        flash.addEventListener('mouseleave', scheduleDismiss);

        scheduleDismiss();
    });

})();
