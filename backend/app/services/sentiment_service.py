"""Sentiment analysis utilities using VADER."""

from functools import lru_cache

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


@lru_cache(maxsize=1)
def get_sentiment_analyzer() -> SentimentIntensityAnalyzer:
    """Create and cache one VADER analyzer per application process."""
    return SentimentIntensityAnalyzer()


def classify_sentiment(score: float) -> str:
    """
    Convert a VADER compound score into a sentiment label.

    Positive: score >= 0.05
    Negative: score <= -0.05
    Neutral: otherwise
    """
    if score >= 0.05:
        return "Positive"

    if score <= -0.05:
        return "Negative"

    return "Neutral"


def analyze_sentiment(text: str) -> dict[str, float | str]:
    """
    Analyze a review and return its sentiment label and scores.

    Args:
        text: The customer review to analyze.

    Returns:
        A dictionary containing the sentiment label, compound score,
        and positive, neutral, and negative proportions.

    Raises:
        TypeError: If text is not a string.
        ValueError: If text is empty or contains only whitespace.
    """
    if not isinstance(text, str):
        raise TypeError("Review text must be a string.")

    if not text.strip():
        raise ValueError("Review text cannot be empty.")

    analyzer = get_sentiment_analyzer()
    scores = analyzer.polarity_scores(text)

    compound_score = scores["compound"]

    return {
        "sentiment": classify_sentiment(compound_score),
        "sentiment_score": compound_score,
        "positive_score": scores["pos"],
        "neutral_score": scores["neu"],
        "negative_score": scores["neg"],
    }