(function () {
    "use strict";

    function getCookie(name) {
        const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
        return match ? decodeURIComponent(match[2]) : null;
    }

    document.addEventListener("DOMContentLoaded", function () {
        const btn = document.querySelector(".nc-rsvp-btn");
        if (!btn) return;

        btn.addEventListener("click", function () {
            btn.disabled = true;

            fetch(btn.dataset.rsvpUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then(function (response) {
                    return response.json();
                })
                .then(function (data) {
                    const icon = btn.querySelector("i");
                    const label = btn.querySelector(".nc-rsvp-label");
                    document.querySelector(".nc-attendee-count").textContent = data.attendee_count;

                    if (data.joined) {
                        btn.classList.add("btn-primary", "active");
                        btn.classList.remove("btn-light");
                        icon.classList.remove("bi-calendar-plus");
                        icon.classList.add("bi-check-circle-fill");
                        label.textContent = "Going";
                    } else {
                        btn.classList.remove("btn-primary", "active");
                        btn.classList.add("btn-light");
                        icon.classList.remove("bi-check-circle-fill");
                        icon.classList.add("bi-calendar-plus");
                        label.textContent = "RSVP";
                    }
                })
                .finally(function () {
                    btn.disabled = false;
                });
        });
    });
})();
