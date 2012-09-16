from django import forms
from models import Email

class TryItForm(forms.Form):
    sender = forms.CharField(label="Your email")
    to = forms.CharField(label="Friends' emails")
    subject = forms.CharField(max_length=100)
    message = forms.CharField()

class EmailForm(forms.ModelForm):
    attachments = forms.IntegerField()
    class Meta:
        model = Email
        exclude = 'attachments'

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.Form):
    email = forms.EmailField()
#    profile_picture = forms.URLField()
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
