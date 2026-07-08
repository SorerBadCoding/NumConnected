(function () {
    "use strict";

    document.addEventListener("DOMContentLoaded", function () {
        var form = document.getElementById("chatForm");
        if (!form) return;

        var messagesEl = document.getElementById("chatMessages");
        var input = document.getElementById("chatInput");
        var conversationIdInput = document.getElementById("chatConversationId");
        var sendBtn = document.getElementById("chatSendBtn");
        var welcomeEl = document.getElementById("chatWelcome");
        var sendUrl = form.dataset.sendUrl || "/ai-assistant/send/";

        function csrfToken() {
            var input = form.querySelector('[name="csrfmiddlewaretoken"]');
            return input ? input.value : "";
        }

        function scrollToBottom() {
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }

        function escapeHtml(text) {
            var div = document.createElement("div");
            div.textContent = text;
            return div.innerHTML;
        }

        function appendBubble(role, content, time) {
            var row = document.createElement("div");
            row.className = "nc-chat-bubble-row " + (role === "user" ? "is-user" : "is-assistant");

            var avatarHtml = role === "assistant"
                ? '<span class="nc-avatar nc-avatar-sm nc-avatar-initials"><i class="bi bi-stars"></i></span>'
                : "";

            row.innerHTML =
                avatarHtml +
                '<div class="nc-chat-bubble"><p class="mb-0">' + escapeHtml(content).replace(/\n/g, "<br>") + '</p>' +
                '<span class="nc-chat-time">' + time + "</span></div>";

            messagesEl.appendChild(row);
            scrollToBottom();
            return row;
        }

        function showTypingIndicator() {
            var row = document.createElement("div");
            row.className = "nc-chat-bubble-row is-assistant";
            row.id = "ncTypingRow";
            row.innerHTML =
                '<span class="nc-avatar nc-avatar-sm nc-avatar-initials"><i class="bi bi-stars"></i></span>' +
                '<div class="nc-chat-bubble"><div class="nc-typing-indicator"><span></span><span></span><span></span></div></div>';
            messagesEl.appendChild(row);
            scrollToBottom();
        }

        function removeTypingIndicator() {
            var row = document.getElementById("ncTypingRow");
            if (row) row.remove();
        }

        function autoResize() {
            input.style.height = "auto";
            input.style.height = Math.min(input.scrollHeight, 140) + "px";
        }

        input.addEventListener("input", autoResize);

        input.addEventListener("keydown", function (event) {
            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                form.requestSubmit();
            }
        });

        function sendMessage(text) {
            if (welcomeEl) {
                welcomeEl.remove();
                welcomeEl = null;
            }

            appendBubble("user", text, "Just now");
            showTypingIndicator();
            sendBtn.disabled = true;

            var body = new URLSearchParams();
            body.set("message", text);
            body.set("conversation_id", conversationIdInput.value || "");

            fetch(sendUrl, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrfToken(),
                    "X-Requested-With": "XMLHttpRequest",
                },
                body: body.toString(),
            })
                .then(function (response) {
                    return response.json().then(function (data) {
                        return { ok: response.ok, data: data };
                    });
                })
                .then(function (result) {
                    removeTypingIndicator();
                    if (!result.ok) {
                        appendBubble("assistant", result.data.error || "Something went wrong. Please try again.", "Just now");
                        return;
                    }
                    conversationIdInput.value = result.data.conversation_id;
                    appendBubble("assistant", result.data.assistant_message.content, result.data.assistant_message.time);
                })
                .catch(function () {
                    removeTypingIndicator();
                    appendBubble("assistant", "Sorry, I couldn't reach the server. Please check your connection and try again.", "Just now");
                })
                .finally(function () {
                    sendBtn.disabled = false;
                });
        }

        form.addEventListener("submit", function (event) {
            event.preventDefault();
            var text = input.value.trim();
            if (!text) return;
            input.value = "";
            autoResize();
            sendMessage(text);
        });

        document.querySelectorAll(".nc-suggestion-chip").forEach(function (chip) {
            chip.addEventListener("click", function () {
                sendMessage(chip.textContent.trim());
            });
        });

        scrollToBottom();
    });
})();
