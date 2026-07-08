(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        // Mobile sidebar toggle
        var sidebar = document.getElementById("ncSidebar");
        var backdrop = document.getElementById("ncSidebarBackdrop");
        var toggleBtn = document.getElementById("ncSidebarToggle");

        function closeSidebar() {
            if (sidebar) sidebar.classList.remove("show");
            if (backdrop) backdrop.classList.remove("show");
        }

        if (toggleBtn && sidebar) {
            toggleBtn.addEventListener("click", function () {
                sidebar.classList.toggle("show");
                if (backdrop) backdrop.classList.toggle("show");
            });
        }
        if (backdrop) {
            backdrop.addEventListener("click", closeSidebar);
        }

        // Auto-dismiss success/info alerts after a few seconds
        document.querySelectorAll(".nc-alert.alert-success, .nc-alert.alert-info").forEach(function (alertEl) {
            setTimeout(function () {
                var bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
                bsAlert.close();
            }, 5000);
        });

        // Enable Bootstrap tooltips where present
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
            new bootstrap.Tooltip(el);
        });
    });
})();
