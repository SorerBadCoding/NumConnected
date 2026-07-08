from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def nav_active(context, *namespaces):
    """Return 'active' if the current view's app namespace matches one of
    the given namespaces. Used to highlight the current section in the
    sidebar without repeating request-inspection logic in every template."""
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    if match and match.app_name in namespaces:
        return "active"
    return ""
