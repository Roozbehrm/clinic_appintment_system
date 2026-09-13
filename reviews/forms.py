from django import forms
from .models import Review

from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} ستاره") for i in range(1, 6)],
                                    attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3,
                                              "placeholder": "نظر خود را بنویسید..."}),
        }
