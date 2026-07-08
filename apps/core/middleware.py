class ThemeMiddleware:
    """Read the visitor's light/dark preference from a cookie.

    Reading it server-side (rather than only in JS) lets the base template
    render the correct `data-bs-theme` attribute on first paint, avoiding a
    flash of the wrong theme.
    """

    COOKIE_NAME = "numconnect_theme"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        theme = request.COOKIES.get(self.COOKIE_NAME, "light")
        request.theme = theme if theme in ("light", "dark") else "light"
        return self.get_response(request)
