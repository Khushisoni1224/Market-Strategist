
from django import forms


class FeedbackForm(forms.Form):
    review_text = forms.CharField(
        label="Customer feedback",
        min_length=3,
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "class": "feedback-textarea",
                "rows": 6,
                "placeholder": (
                    "Example: The dress is comfortable, "
                    "but the size is too small."
                ),
            }
        ),
        error_messages={
            "required": "Please enter customer feedback.",
            "min_length": "Feedback must contain at least 3 characters.",
            "max_length": "Feedback cannot exceed 5000 characters.",
        },
    )
