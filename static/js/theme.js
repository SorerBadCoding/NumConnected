(function () {
    "use strict";

    var STORAGE_KEY = "numconnect-theme";
    var COOKIE_NAME = "numconnect_theme";
    var root = document.documentElement;

    function setCookie(name, value, days) {
        var expires = new Date(Date.now() + days * 864e5).toUTCString();
        document.cookie = name + "=" + value + "; expires=" + expires + "; path=/; SameSite=Lax";
    }

    function applyTheme(theme) {
        root.setAttribute("data-bs-theme", theme);
        localStorage.setItem(STORAGE_KEY, theme);
        setCookie(COOKIE_NAME, theme, 365);
    }

    function currentTheme() {
        return root.getAttribute("data-bs-theme") === "dark" ? "dark" : "light";
    }

    document.addEventListener("DOMContentLoaded", function () {
        var toggles = document.querySelectorAll(".nc-theme-toggle");
        toggles.forEach(function (btn) {
            btn.addEventListener("click", function () {
                applyTheme(currentTheme() === "dark" ? "light" : "dark");
            });
        });
    });
})();
