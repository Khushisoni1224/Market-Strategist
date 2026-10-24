from .marketing_metrics import calculate_marketing_summary
from .models import MarketingPerformance

from .marketing_import import process_marketing_csv

from django.shortcuts import render, get_object_or_404

from .models import FeedbackImport, CustomerFeedback
from .feedback_import import process_feedback_csv
import re
from .forms import FeedbackForm
from .sentiment import analyze_single_review


from .sentiment import analyze_reviews
from .complaints import analyze_complaints


def home(request):
    # Load reviews and calculate sentiment
    df = analyze_reviews()

    sentiment_counts = df["Sentiment"].value_counts()

    total_reviews = len(df)

    positive_count = int(sentiment_counts.get("Positive", 0))
    negative_count = int(sentiment_counts.get("Negative", 0))
    neutral_count = int(sentiment_counts.get("Neutral", 0))

    # Calculate sentiment percentages
    positive_percentage = (
        round(positive_count / total_reviews * 100, 2)
        if total_reviews else 0
    )

    negative_percentage = (
        round(negative_count / total_reviews * 100, 2)
        if total_reviews else 0
    )

    neutral_percentage = (
        round(neutral_count / total_reviews * 100, 2)
        if total_reviews else 0
    )

    # Pie chart data
    sentiment_chart = {
        "labels": ["Positive", "Negative", "Neutral"],
        "values": [
            positive_count,
            negative_count,
            neutral_count,
        ],
    }

    # Complaint and theme analysis
    complaint_analysis = analyze_complaints(df)
    complaint_themes = complaint_analysis["themes"]

    # Average customer rating
    average_rating = round(df["Rating"].mean(), 2) if total_reviews else 0

    # Generate business recommendations from calculated results
    recommendations = []

    if negative_percentage >= 10:
        recommendations.append(
            "Investigate negative reviews and prioritize improvements "
            "that address recurring customer concerns."
        )
    else:
        recommendations.append(
            "Continue monitoring negative feedback to identify "
            "emerging customer concerns."
        )

    if complaint_themes and complaint_themes[0]["count"] > 0:
        top_theme = complaint_themes[0]["theme"]
        recommendations.append(
            f"Review customer comments about {top_theme.lower()} "
            "and investigate whether product or listing improvements are needed."
        )

    if average_rating < 3:
        recommendations.append(
            "The average rating is below 3 out of 5. Review low-rated "
            "products and investigate the reasons for dissatisfaction."
        )
    elif average_rating >= 4:
        recommendations.append(
            "The average rating is at least 4 out of 5. Maintain product "
            "quality and investigate the feedback behind lower ratings."
        )
    else:
        recommendations.append(
            "Review ratings alongside customer comments to identify "
            "opportunities to improve the shopping experience."
        )

    feedback_summary = {
        "total_reviews": total_reviews,
        "positive_percentage": positive_percentage,
        "negative_percentage": negative_percentage,
        "neutral_percentage": neutral_percentage,
        "average_rating": average_rating,
        "recommendations": recommendations,
    }

    # Read selected filters
    selected_sentiment = request.GET.get("sentiment", "").strip()
    selected_rating = request.GET.get("rating", "").strip()
    selected_department = request.GET.get("department", "").strip()

    # Department options
    departments = sorted(
        df["Department Name"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    # Apply filters to the review table only
    filtered_df = df.copy()

    if selected_sentiment in ["Positive", "Negative", "Neutral"]:
        filtered_df = filtered_df[
            filtered_df["Sentiment"] == selected_sentiment
        ]

    if selected_rating in ["1", "2", "3", "4", "5"]:
        filtered_df = filtered_df[
            filtered_df["Rating"] == int(selected_rating)
        ]

    if selected_department in departments:
        filtered_df = filtered_df[
            filtered_df["Department Name"].astype(str)
            == selected_department
        ]

    # Prepare review table data
    display_df = filtered_df[
        ["Review Text", "Rating", "Sentiment Score", "Sentiment"]
    ].head(100).copy()

    display_df.columns = [
        "review_text",
        "rating",
        "sentiment_score",
        "sentiment",
    ]

    reviews = display_df.to_dict(orient="records")

    context = {
        "total_reviews": total_reviews,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "sentiment_chart": sentiment_chart,
        "reviews": reviews,
        "filtered_count": len(filtered_df),
        "departments": departments,
        "selected_sentiment": selected_sentiment,
        "selected_rating": selected_rating,
        "selected_department": selected_department,
        "complaint_analysis": complaint_analysis,
        "complaint_themes": complaint_themes,
        "feedback_summary": feedback_summary,
    }

    return render(request, "analyzer/home.html", context)

def mask_personal_information(text):
    """
    Mask common email addresses and phone-number patterns.
    This is best-effort masking, not guaranteed anonymization.
    """
    # Mask email addresses
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL MASKED]",
        text,
    )

    # Mask common phone-number patterns
    text = re.sub(
        r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)",
        "[PHONE MASKED]",
        text,
    )

    return text


def submit_feedback(request):
    result = None

    if request.method == "POST":
        form = FeedbackForm(request.POST)

        if form.is_valid():
            original_text = form.cleaned_data["review_text"].strip()

            if not original_text:
                form.add_error(
                    "review_text",
                    "Please enter meaningful customer feedback.",
                )
            else:
                sanitized_text = mask_personal_information(
                    original_text
                )

                result = analyze_single_review(sanitized_text)

                # Display the masked text, not the original text.
                result["review_text"] = sanitized_text
    else:
        form = FeedbackForm()

    return render(
        request,
        "analyzer/feedback.html",
        {
            "form": form,
            "result": result,
        },
    )


def import_feedback(request):
    result = None
    error = None

    if request.method == "POST":
        uploaded_file = request.FILES.get("feedback_file")

        try:
            result = process_feedback_csv(uploaded_file)

        except ValueError as exc:
            error = str(exc)

            # Record failed attempts only when a file was actually selected.
            if uploaded_file is not None:
                FeedbackImport.objects.create(
                    filename=uploaded_file.name[:255],
                    status="failed",
                    error_message=error,
                    total_rows=0,
                    valid_count=0,
                    invalid_count=0,
                    analyzed_count=0,
                )

    return render(
        request,
        "analyzer/import_feedback.html",
        {
            "result": result,
            "error": error,
        },
    )

def import_history(request):
    imports = FeedbackImport.objects.all()

    context = {
        "imports": imports,
        "total_imports": imports.count(),
        "completed_imports": imports.filter(status="completed").count(),
        "failed_imports": imports.filter(status="failed").count(),
        "processing_imports": imports.filter(status="processing").count(),
    }

    return render(
        request,
        "analyzer/import_history.html",
        context,
    )

def import_detail(request, import_id):
    import_record = get_object_or_404(
        FeedbackImport,
        pk=import_id,
    )

    feedback_records = import_record.feedback_records.all()

    sentiment_counts = {
        "Positive": feedback_records.filter(
            sentiment="Positive"
        ).count(),
        "Negative": feedback_records.filter(
            sentiment="Negative"
        ).count(),
        "Neutral": feedback_records.filter(
            sentiment="Neutral"
        ).count(),
    }

    context = {
        "import_record": import_record,
        "feedback_records": feedback_records,
        "sentiment_counts": sentiment_counts,
        "error_message": import_record.error_message,
    }

    return render(
        request,
        "analyzer/import_detail.html",
        context,
    )

def import_marketing(request):
    result = None
    error = None

    if request.method == "POST":
        uploaded_file = request.FILES.get("marketing_file")

        try:
            result = process_marketing_csv(uploaded_file)
        except ValueError as exc:
            error = str(exc)

    return render(
        request,
        "analyzer/import_marketing.html",
        {
            "result": result,
            "error": error,
        },
    )




def marketing_dashboard(request):
    from datetime import date

    all_records = MarketingPerformance.objects.all()
    records = all_records

    start_date = request.GET.get("start_date", "").strip()
    end_date = request.GET.get("end_date", "").strip()
    selected_product = request.GET.get("product", "").strip()
    selected_content_type = request.GET.get("content_type", "").strip()

    filter_error = ""

    # Validate the date filters.
    parsed_start = None
    parsed_end = None

    if start_date:
        try:
            parsed_start = date.fromisoformat(start_date)
        except ValueError:
            filter_error = "Please select a valid start date."

    if end_date:
        try:
            parsed_end = date.fromisoformat(end_date)
        except ValueError:
            filter_error = "Please select a valid end date."

    if (
        parsed_start
        and parsed_end
        and parsed_start > parsed_end
    ):
        filter_error = "Start date cannot be later than end date."
    else:
        if parsed_start:
            records = records.filter(content_date__gte=parsed_start)

        if parsed_end:
            records = records.filter(content_date__lte=parsed_end)

    # Apply product and content-type filters.
    if selected_product:
        records = records.filter(product_name=selected_product)

    if selected_content_type:
        records = records.filter(content_type=selected_content_type)

    # Keep the selected records consistent across the dashboard.
    ordered_records = records.order_by("content_date", "content_id")

    summary = calculate_marketing_summary(ordered_records)

    chart_labels = []
    chart_reach = []
    chart_clicks = []
    chart_conversions = []

    for record in ordered_records:
        chart_labels.append(
            f"{record.content_date} - {record.content_id}"
        )
        chart_reach.append(record.reach)
        chart_clicks.append(record.clicks)
        chart_conversions.append(record.conversions)

    products = (
        MarketingPerformance.objects
        .order_by("product_name")
        .values_list("product_name", flat=True)
        .distinct()
    )

    content_types = (
        MarketingPerformance.objects
        .order_by("content_type")
        .values_list("content_type", flat=True)
        .distinct()
    )

    return render(
        request,
        "analyzer/marketing_dashboard.html",
        {
            "summary": summary,
            "records": ordered_records,
            "chart_labels": chart_labels,
            "chart_reach": chart_reach,
            "chart_clicks": chart_clicks,
            "chart_conversions": chart_conversions,
            "products": products,
            "content_types": content_types,
            "selected_product": selected_product,
            "selected_content_type": selected_content_type,
            "start_date": start_date,
            "end_date": end_date,
            "filter_error": filter_error,
        },
    )
