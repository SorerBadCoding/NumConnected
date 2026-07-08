(function () {
    "use strict";

    function getCookie(name) {
        const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
        return match ? decodeURIComponent(match[2]) : null;
    }

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".nc-favorite-btn").forEach(function (btn) {
            btn.addEventListener("click", function () {
                const url = btn.dataset.favoriteUrl;
                btn.disabled = true;

                fetch(url, {
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
                        if (data.favorited) {
                            btn.classList.add("active");
                            icon.classList.remove("bi-heart");
                            icon.classList.add("bi-heart-fill");
                        } else {
                            btn.classList.remove("active");
                            icon.classList.remove("bi-heart-fill");
                            icon.classList.add("bi-heart");
                        }
                    })
                    .finally(function () {
                        btn.disabled = false;
                    });
            });
        });
    });
})();
