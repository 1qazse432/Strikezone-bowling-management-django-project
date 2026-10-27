"""Reusable bowling-specific template filters and tags."""
from django import template
register = template.Library()

@register.filter(name="score_band")
def score_band(value):
    """Return a concise label for a valid ten-pin bowling score."""
    try:
        score = int(value)
    except (TypeError, ValueError):
        return "Unrated"
    if score >= 220: return "Elite"
    if score >= 180: return "Competitive"
    if score >= 120: return "Developing"
    return "Beginner"

@register.simple_tag
def score_percentage(value):
    """Calculate a bounded percentage against a perfect 300 game."""
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0
    return min(100, max(0, round(score / 300 * 100)))

@register.filter(name="initials")
def initials(value):
    """Return up to two initials for compact profile marks."""
    parts = str(value or "").split()
    return "".join(part[0].upper() for part in parts[:2] if part)
