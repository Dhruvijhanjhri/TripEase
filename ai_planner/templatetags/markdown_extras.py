from django import template
import markdown

register = template.Library()


@register.filter
def markdownify(text):
    if not text:
        return ""

    return markdown.markdown(
        text,
        extensions=[
            "extra",
            "nl2br",
            "sane_lists",
        ],
    )
