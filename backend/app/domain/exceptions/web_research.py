"""Web Research domain exceptions."""


class WebResearchError(Exception):
    """Raised when web research (Gemini Grounding) fails.

    NOT silently caught — chapters are marked as grounding_status='failed'.
    Admin Dashboard shows red badge for failed chapters.
    """
    pass
