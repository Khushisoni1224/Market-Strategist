"""Complaint theme detection for negative customer feedback."""

import re


COMPLAINT_THEMES: dict[str, list[str]] = {
    "Size and Fit": [
        r"\btoo tight\b",
        r"\btoo loose\b",
        r"\bdoesn't fit\b",
        r"\bdoes not fit\b",
        r"\bdidn't fit\b",
        r"\bdid not fit\b",
        r"\bpoor fit\b",
        r"\bwrong size\b",
        r"\bsize\s+(?:too small|too large|too big)\b",
        r"\bsize chart\b",
        r"\bsmall for\b",
        r"\blarge for\b",
        r"\btight around\b",
        r"\bloose around\b",
    ],
        "Fabric and Quality": [
        r"\bpoor quality\b",
        r"\blow quality\b",
        r"\bquality is (?:very |extremely )?poor\b",
        r"\bpoor (?:fabric|material)\b",
        r"\bfabric is (?:very |extremely )?terrible\b",
        r"\bmaterial is (?:very |extremely )?terrible\b",
        r"\bterrible quality\b",
        r"\bfabric.{0,30}\bterrible\b",
        r"\bterrible.{0,30}\bfabric\b",
        r"\brough fabric\b",
        r"\bthin fabric\b",
        r"\bcheap material\b",
        r"\bstiff fabric\b",
        r"\bscratchy fabric\b",
        r"\bitchy material\b",
        r"\bfabric is itchy\b",
        r"\bfabric feels itchy\b",
        r"\bsee[- ]through\b",
        r"\btransparent fabric\b",
        r"\bfabric is rough\b",
        r"\bmaterial is rough\b",
    ],
    "Appearance and Design": [
        r"\bwrong color\b",
        r"\bcolour is different\b",
        r"\bcolor is different\b",
        r"\blooks different\b",
        r"\bnot as pictured\b",
        r"\bnot like the picture\b",
        r"\bnot like the photo\b",
        r"\bpoor design\b",
        r"\bpattern is different\b",
        r"\bcolor faded\b",
        r"\bcolour faded\b",
        r"\bdoesn't look like\b",
        r"\bdoes not look like\b",
    ],
    "Durability": [
        r"\bfell apart\b",
        r"\bfell off\b",
        r"\bbroke after\b",
        r"\bbroken after\b",
        r"\bstarted tearing\b",
        r"\bcoming apart\b",
        r"\bthreads came out\b",
        r"\bseams came apart\b",
        r"\bzipper broke\b",
        r"\bbutton fell off\b",
        r"\bpoor stitching\b",
        r"\bnot durable\b",
    ],
    "Delivery and Service": [
        r"\blate delivery\b",
        r"\bdelivery was delayed\b",
        r"\bdelayed delivery\b",
        r"\barrived late\b",
        r"\bnever arrived\b",
        r"\bnot delivered\b",
        r"\bwrong item\b",
        r"\bmissing item\b",
        r"\bpoor customer service\b",
        r"\bno response\b",
        r"\brefund was denied\b",
        r"\brefund not received\b",
    ],
}


# Compile patterns once so they do not need to be recompiled for every review.
COMPILED_COMPLAINT_THEMES: dict[str, list[re.Pattern[str]]] = {
    theme: [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
    for theme, patterns in COMPLAINT_THEMES.items()
}


def detect_complaint_themes(
    review_text: str,
    sentiment: str,
) -> list[str]:
    """
    Return complaint themes found in a negative customer review.

    Each theme appears at most once per review.

    Positive and neutral reviews return an empty list.
    """
    if not isinstance(review_text, str):
        raise TypeError("Review text must be a string.")

    if sentiment not in {"Positive", "Neutral", "Negative"}:
        raise ValueError(
            "Sentiment must be Positive, Neutral, or Negative."
        )

    if sentiment != "Negative" or not review_text.strip():
        return []

    detected_themes: list[str] = []

    for theme, patterns in COMPILED_COMPLAINT_THEMES.items():
        if any(pattern.search(review_text) for pattern in patterns):
            detected_themes.append(theme)

    return detected_themes


def count_complaint_themes(
    reviews: list[dict[str, str]],
) -> dict[str, int]:
    """
    Count how many negative reviews mention each complaint theme.

    Each review contributes at most one count to each theme.

    Each review dictionary must contain:
        - review_text
        - sentiment
    """
    theme_counts = {
        theme: 0 for theme in COMPLAINT_THEMES
    }

    for review in reviews:
        review_text = review.get("review_text", "")
        sentiment = review.get("sentiment", "")

        detected_themes = detect_complaint_themes(
            review_text,
            sentiment,
        )

        for theme in detected_themes:
            theme_counts[theme] += 1

    return theme_counts