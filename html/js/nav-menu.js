(function () {
    "use strict";

    function closeNavigationMenu(event) {
        var link = event.target.closest(".nav-menu a");
        if (!link) {
            return;
        }

        var menu = link.closest(".nav-menu");
        if (menu) {
            menu.open = false;
        }
    }

    document.addEventListener("click", closeNavigationMenu);
})();
