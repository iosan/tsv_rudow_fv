(function () {
    "use strict";

    var mobileQuery = window.matchMedia("(max-width: 640px)");

    function isMobileNavigation() {
        return mobileQuery.matches;
    }

    function syncNavigationMenu() {
        var menu = document.querySelector(".nav-menu");
        if (!menu) {
            return;
        }

        menu.open = !isMobileNavigation();
    }

    function closeNavigationMenu(event) {
        var link = event.target.closest(".nav-menu a");
        if (!link) {
            return;
        }

        if (!isMobileNavigation()) {
            return;
        }

        var menu = link.closest(".nav-menu");
        if (menu) {
            window.setTimeout(function () {
                menu.open = false;
            }, 0);
        }
    }

    function registerServiceWorker() {
        if (!("serviceWorker" in window.navigator)) {
            return;
        }

        if (window.location.protocol === "file:") {
            return;
        }

        window.navigator.serviceWorker.register("sw.js").catch(function () {
            // Keep the site functional even if offline caching cannot be installed.
        });
    }

    syncNavigationMenu();
    registerServiceWorker();

    if (mobileQuery.addEventListener) {
        mobileQuery.addEventListener("change", syncNavigationMenu);
    } else if (mobileQuery.addListener) {
        mobileQuery.addListener(syncNavigationMenu);
    }

    document.addEventListener("click", closeNavigationMenu, true);
})();
