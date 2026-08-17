from django import template

register = template.Library()


@register.filter
def genre_list(value):
    """Turn "Drama, Mystery, Sci-Fi" into ["Drama", "Mystery", "Sci-Fi"]."""
    if not value:
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]
