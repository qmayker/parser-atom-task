"""
Choices for Product model fields.
Defines dropdown options for display in Django admin and forms.
"""

from django.db.models import TextChoices


class Parsers(TextChoices):
    """Available parser types"""
    REQUESTS = "requests", "Requests"
    SELENIUM = "selenium", "Selenium"
    PLAYWRIGHT = "playwright", "Playwright"

