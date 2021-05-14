from django import forms


class WordSearchForm(forms.Form):
    word = forms.CharField(
        label="",
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Search for a word",
                "oninput": "load_results(this.value)",
                "id": "search-input",
            }
        ),
    )
