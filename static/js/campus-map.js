(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        var locations = window.NC_CAMPUS_LOCATIONS || {};
        var detailCard = document.getElementById("locationDetailCard");
        var detailName = document.getElementById("detailName");
        var detailCategory = document.getElementById("detailCategory");
        var detailDescription = document.getElementById("detailDescription");
        var detailIcon = document.getElementById("detailIcon");

        function selectLocation(id) {
            var data = locations[id];
            if (!data) return;

            document.querySelectorAll(".nc-campus-marker.active, .nc-campus-list-item.active").forEach(function (el) {
                el.classList.remove("active");
            });
            document.querySelectorAll('[data-location-id="' + id + '"]').forEach(function (el) {
                el.classList.add("active");
            });

            detailName.textContent = data.name;
            detailCategory.textContent = data.category;
            detailDescription.textContent = data.description || "No additional details provided.";
            detailIcon.innerHTML = '<i class="bi ' + data.icon + '"></i>';
            detailCard.style.display = "block";
        }

        document.querySelectorAll(".nc-campus-marker, .nc-campus-list-item").forEach(function (el) {
            el.addEventListener("click", function () {
                selectLocation(el.dataset.locationId);
                if (el.classList.contains("nc-campus-marker")) {
                    detailCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
                }
            });
        });
    });
})();
