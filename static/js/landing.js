(function () {
    "use strict";

    function animateCounter(el) {
        var target = parseInt(el.dataset.target, 10) || 0;
        var duration = 1200;
        var start = null;

        function step(timestamp) {
            if (!start) start = timestamp;
            var progress = Math.min((timestamp - start) / duration, 1);
            var eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.floor(eased * target).toLocaleString();
            if (progress < 1) {
                window.requestAnimationFrame(step);
            } else {
                el.textContent = target.toLocaleString();
            }
        }
        window.requestAnimationFrame(step);
    }

    document.addEventListener("DOMContentLoaded", function () {
        var counters = document.querySelectorAll(".nc-counter");
        if (!counters.length) return;

        if (!("IntersectionObserver" in window)) {
            counters.forEach(animateCounter);
            return;
        }

        var observer = new IntersectionObserver(
            function (entries, obs) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        animateCounter(entry.target);
                        obs.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.4 }
        );

        counters.forEach(function (counter) {
            observer.observe(counter);
        });

        // Smooth-scroll for on-page anchor nav links
        document.querySelectorAll('.nc-mkt-links a[href^="#"]').forEach(function (link) {
            link.addEventListener("click", function (event) {
                var target = document.querySelector(link.getAttribute("href"));
                if (target) {
                    event.preventDefault();
                    target.scrollIntoView({ behavior: "smooth", block: "start" });
                }
            });
        });
    });
})();
