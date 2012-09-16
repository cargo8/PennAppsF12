from django import forms
from models import Email

class TryItForm(forms.Form):
    sender = forms.CharField(label="Your email")
    to = forms.CharField(label="Friends' emails")
    subject = forms.CharField(max_length=100)
    message = forms.CharField()

class LoginForm(forms.Form):
    email = models.EmailField()
    password = models.PasswordField()

class UserForm(forms.Form):
	email = models.EmailField()
	profile_picture = models.URLField()
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
    password = models.PasswordField()

class EmailForm(forms.ModelForm):
    attachments = forms.IntegerField()
    class Meta:
        model = Email
        exclude = 'attachments'
