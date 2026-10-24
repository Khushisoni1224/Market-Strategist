
from pathlib import Path

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "datasets" / "clothing_reviews.csv"

def classify_sentiment(score):
    """Classify a VADER compound score using the existing thresholds."""
    if score >= 0.05:
        return "Positive"
    elif score <= -0.05:
        return "Negative"
    return "Neutral"


def analyze_single_review(review_text):
    """Analyze one customer review using VADER."""
    analyzer = SentimentIntensityAnalyzer()

    scores = analyzer.polarity_scores(review_text)
    compound_score = scores["compound"]

    return {
        "sentiment_score": compound_score,
        "sentiment": classify_sentiment(compound_score),
        "positive_score": scores["pos"],
        "neutral_score": scores["neu"],
        "negative_score": scores["neg"],
    }


def analyze_reviews():
    """Load and analyze the existing clothing reviews dataset."""
    df = pd.read_csv(DATASET_PATH)

    df = df.dropna(subset=["Review Text"]).copy()

    analyzer = SentimentIntensityAnalyzer()

    df["Sentiment Score"] = df["Review Text"].apply(
        lambda review: analyzer.polarity_scores(str(review))["compound"]
    )

    df["Sentiment"] = df["Sentiment Score"].apply(
        classify_sentiment
    )

    return df
