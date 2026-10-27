"""Utilities for masking personally identifiable information."""

import re


# Match common email address formats.
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

# Find possible phone-number sequences containing digits and separators.
# The callback below checks the number of digits before masking.
PHONE_PATTERN = re.compile(
    r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)"
)


def _mask_phone_match(match: re.Match[str]) -> str:
    """Mask a phone-like sequence only when it contains 10–15 digits."""
    candidate = match.group(0)
    digit_count = sum(character.isdigit() for character in candidate)

    if 10 <= digit_count <= 15:
        return "[PHONE]"

    return candidate


def mask_personal_information(text: str) -> str:
    """
    Mask email addresses and likely phone numbers in text.

    Args:
        text: Review text that may contain personal information.

    Returns:
        Text with email addresses replaced by [EMAIL] and phone numbers
        replaced by [PHONE].

    Raises:
        TypeError: If text is not a string.
    """
    if not isinstance(text, str):
        raise TypeError("Review text must be a string.")

    # Mask email addresses first.
    masked_text = EMAIL_PATTERN.sub("[EMAIL]", text)

    # Mask likely phone numbers.
    masked_text = PHONE_PATTERN.sub(_mask_phone_match, masked_text)

    return masked_text