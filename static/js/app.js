/**
 * ComPaye Tarjetas — Main JavaScript
 *
 * Handles:
 *  - Delete confirmation dialog
 *  - Photo file preview
 *  - Inline container editing toggle
 *  - Auto-dismiss flash messages
 */

(function () {
    'use strict';

    // =================================================================
    // CONFIRMATION DIALOG
    // =================================================================

    const overlay  = document.getElementById('confirm-dialog');
    const msgEl    = document.getElementById('confirm-message');
    const okBtn    = document.getElementById('confirm-ok');
    const cancelBtn = document.getElementById('confirm-cancel');
    let pendingForm = null;

    function showConfirm(message, form) {
        msgEl.textContent = message;
        pendingForm = form;
        overlay.style.display = 'flex';
        cancelBtn.focus();
    }

    function hideConfirm() {
        overlay.style.display = 'none';
        pendingForm = null;
    }

    if (okBtn) {
        okBtn.addEventListener('click', function () {
            if (pendingForm) {
                pendingForm.submit();
            }
            hideConfirm();
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', hideConfirm);
    }

    if (overlay) {
        overlay.addEventListener('click', function (e) {
            if (e.target === overlay) hideConfirm();
        });
    }

    // Attach to any button with data-confirm
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('[data-confirm]');
        if (!btn) return;

        e.preventDefault();
        e.stopPropagation();

        const form = btn.closest('form');
        const message = btn.getAttribute('data-confirm');

        if (form && message) {
            showConfirm(message, form);
        }
    });

    // ESC to close
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && overlay && overlay.style.display === 'flex') {
            hideConfirm();
        }
    });


    // =================================================================
    // PHOTO PREVIEW
    // =================================================================

    window.previewPhoto = function (input) {
        if (!input.files || !input.files[0]) return;

        const file = input.files[0];
        const reader = new FileReader();

        reader.onload = function (e) {
            let previewImg = document.getElementById('photo-preview');
            const container = document.getElementById('photo-preview-container');

            if (container) {
                container.style.display = 'block';
            }

            if (previewImg) {
                previewImg.src = e.target.result;
            }
        };

        reader.readAsDataURL(file);

        // Update the label text
        const label = input.nextElementSibling;
        if (label && label.classList.contains('btn-file-label')) {
            label.textContent = '📁 ' + file.name;
        }
    };


    // =================================================================
    // CONTAINER INLINE EDIT TOGGLE
    // =================================================================

    window.toggleEditRow = function (btn, containerId) {
        const editRow = document.getElementById('edit-row-' + containerId);
        if (!editRow) return;

        const isVisible = editRow.style.display !== 'none';
        editRow.style.display = isVisible ? 'none' : 'table-row';

        if (!isVisible) {
            const firstInput = editRow.querySelector('input');
            if (firstInput) firstInput.focus();
        }
    };


    // =================================================================
    // AUTO-DISMISS FLASH MESSAGES (after 6 seconds)
    // =================================================================

    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(function (flash) {
        setTimeout(function () {
            flash.style.transition = 'opacity 0.5s, transform 0.5s';
            flash.style.opacity = '0';
            flash.style.transform = 'translateY(-10px)';
            setTimeout(function () {
                flash.remove();
            }, 500);
        }, 6000);
    });

})();
