(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        const form = document.getElementById("resourceUploadForm");
        if (!form) return;

        const fileInput = form.querySelector('input[type="file"]');
        const progressWrap = document.getElementById("uploadProgressWrap");
        const progressBar = document.getElementById("uploadProgressBar");
        const progressLabel = document.getElementById("uploadProgressLabel");
        const submitBtn = document.getElementById("resourceSubmitBtn");

        form.addEventListener("submit", function (event) {
            // Only hijack the submit for real file uploads — a plain text
            // edit with no new file doesn't need a progress bar.
            if (!fileInput || !fileInput.files.length) return;

            event.preventDefault();
            submitBtn.disabled = true;
            progressWrap.classList.remove("d-none");

            const xhr = new XMLHttpRequest();
            xhr.open(form.method, form.action || window.location.href, true);

            xhr.upload.addEventListener("progress", function (e) {
                if (!e.lengthComputable) return;
                const pct = Math.round((e.loaded / e.total) * 100);
                progressBar.style.width = pct + "%";
                progressLabel.textContent = "Uploading... " + pct + "%";
            });

            xhr.onload = function () {
                // Whether the server redirected (success) or re-rendered the
                // form with errors (validation failure), the response body is
                // a full HTML page — swap it in directly rather than
                // re-implementing redirect/error handling client-side.
                document.open();
                document.write(xhr.responseText);
                document.close();
            };

            xhr.onerror = function () {
                progressLabel.textContent = "Upload failed. Please try again.";
                submitBtn.disabled = false;
            };

            xhr.send(new FormData(form));
        });
    });
})();
