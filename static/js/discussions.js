(function () {
    "use strict";

    function getCookie(name) {
        const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
        return match ? decodeURIComponent(match[2]) : null;
    }

    function setupLikeButtons(root) {
        root.querySelectorAll(".nc-like-btn").forEach(function (btn) {
            if (btn.dataset.bound) return;
            btn.dataset.bound = "true";

            btn.addEventListener("click", function () {
                const url = btn.dataset.likeUrl;
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
                        const count = btn.querySelector(".nc-like-count");
                        count.textContent = data.like_count;
                        if (data.liked) {
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
    }

    document.addEventListener("DOMContentLoaded", function () {
        setupLikeButtons(document);

        const feed = document.getElementById("postFeed");
        const loadMoreWrap = document.getElementById("loadMoreWrap");
        if (!feed || !loadMoreWrap) return;

        const loadMoreBtn = document.getElementById("loadMoreBtn");
        const skeleton = document.getElementById("loadMoreSkeleton");

        loadMoreBtn.addEventListener("click", function (event) {
            event.preventDefault();
            const url = loadMoreBtn.getAttribute("href");
            loadMoreBtn.classList.add("d-none");
            skeleton.classList.remove("d-none");

            fetch(url, { headers: { "X-Requested-With": "XMLHttpRequest" } })
                .then(function (response) {
                    return response.text();
                })
                .then(function (html) {
                    const temp = document.createElement("div");
                    temp.innerHTML = html;

                    const meta = temp.querySelector("#paginationMeta");
                    temp.querySelectorAll(".card").forEach(function (card) {
                        feed.appendChild(card);
                    });
                    setupLikeButtons(feed);

                    skeleton.classList.add("d-none");
                    if (meta && meta.dataset.hasNext === "true") {
                        loadMoreBtn.setAttribute(
                            "href",
                            url.replace(/page=\d+/, "page=" + meta.dataset.nextPage)
                        );
                        loadMoreBtn.classList.remove("d-none");
                    } else {
                        loadMoreWrap.remove();
                    }
                })
                .catch(function () {
                    skeleton.classList.add("d-none");
                    loadMoreBtn.classList.remove("d-none");
                });
        });
    });
})();
