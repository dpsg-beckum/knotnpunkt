document.addEventListener('DOMContentLoaded', function () {
    // helper to build a unique key for each panel
    function keyFor(panelId) {
        return 'accordionState:' + panelId;
    }

    // restore state on load
    document.querySelectorAll('.accordion .accordion-button.persist')
        .forEach(function (btn) {
            var target = document.querySelector(btn.getAttribute('data-bs-target'));
            var isOpen = localStorage.getItem(keyFor(target.id)) === 'open';
            if (isOpen) {
                // Bootstrap 5: use the Collapse API to show
                var collapse = new bootstrap.Collapse(target, { toggle: false });
                collapse.show();
            }
        });

    // listen for show/hide and save state
    document.querySelectorAll('.accordion .accordion-button.persist')
        .forEach(function (btn) {
            var target = document.querySelector(btn.getAttribute('data-bs-target'));

            target.addEventListener('show.bs.collapse', function () {
                localStorage.setItem(keyFor(target.id), 'open');
            });
            target.addEventListener('hide.bs.collapse', function () {
                localStorage.setItem(keyFor(target.id), 'closed');
            });
        });
});
