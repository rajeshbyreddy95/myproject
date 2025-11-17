from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def nav_active(context, url_name):
    try:
        current = context['request'].resolver_match.url_name
        return 'active bg-primary text-white' if current == url_name else ''
    except:
        return ''
