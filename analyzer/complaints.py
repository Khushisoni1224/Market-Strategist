
import re


COMPLAINT_THEMES = {
    "Size and Fit": [
        r"\bsize\b",
        r"\bsizing\b",
        r"\bfit\b",
        r"\btoo small\b",
        r"\btoo large\b",
        r"\btight\b",
        r"\bloose\b",
        r"\bshort\b",
        r"\blong\b",
        r"\bpetite\b",
    ],

    "Fabric and Quality": [
        r"\bfabric\b",
        r"\bquality\b",
        r"\bmaterial\b",
        r"\bcheap\b",
        r"\bthin\b",
        r"\bitchy\b",
        r"\bscratchy\b",
        r"\bstitching\b",
        r"\bseam\b",
        r"\bsee through\b",
        r"\bsee-through\b",
    ],

    "Appearance and Design": [
        r"\bcolor\b",
        r"\bcolour\b",
        r"\bpattern\b",
        r"\bdesign\b",
        r"\blook\b",
        r"\bphoto\b",
        r"\bpicture\b",
        r"\bstyle\b",
        r"\bprint\b",
    ],

    "Price and Value": [
        r"\bprice\b",
        r"\bexpensive\b",
        r"\boverpriced\b",
        r"\bworth\b",
        r"\bvalue\b",
        r"\bcost\b",
        r"\bcheap\b",
    ],

    "Comfort": [
        r"\bcomfortable\b",
        r"\buncomfortable\b",
        r"\bcomfort\b",
        r"\bsoft\b",
        r"\bstiff\b",
        r"\brestrictive\b",
        r"\bitchy\b",
    ],

    "Length and Proportions": [
        r"\blength\b",
        r"\btoo long\b",
        r"\btoo short\b",
        r"\bhem\b",
        r"\bsleeve\b",
        r"\bwaist\b",
        r"\bproportion\b",
    ],
}


def analyze_complaints(df):
    # Analyze negative reviews only
    negative_df = df[
        df["Sentiment"] == "Negative"
    ].copy()

    theme_results = []

    for theme, patterns in COMPLAINT_THEMES.items():
        pattern = re.compile(
            "|".join(f"(?:{p})" for p in patterns),
            flags=re.IGNORECASE,
        )

        # Count each review once per theme
        matches = negative_df[
            negative_df["Review Text"].fillna("").astype(str).str.contains(
                pattern,
                na=False,
            )
        ]

        examples = (
            matches["Review Text"]
            .dropna()
            .astype(str)
            .head(3)
            .tolist()
        )

        theme_results.append({
            "theme": theme,
            "count": len(matches),
            "examples": examples,
        })

    # Display the most frequently mentioned themes first
    theme_results.sort(
        key=lambda item: item["count"],
        reverse=True,
    )

    return {
        "negative_total": len(negative_df),
        "themes": theme_results,
    }
