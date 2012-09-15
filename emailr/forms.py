from django import forms

class TryItForm(forms.Form):
    sender = forms.CharField(label="Your email")
    to = forms.CharField(label="Friends' emails")
    subject = forms.CharField(max_length=100)
    message = forms.CharField()