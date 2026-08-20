from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, ReviewReport

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "text")
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} / 5") for i in range(1, 6)]),
            "text": forms.Textarea(attrs={"rows": 5, "placeholder": "Share your experience..."})
        }

class ReportForm(forms.ModelForm):
    class Meta:
        model = ReviewReport
        fields = ("reason",)
        widgets = {"reason": forms.TextInput(attrs={"placeholder": "Why is this review inappropriate?"})}
