from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
	owner = models.ForeignKey(User)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)

class Group(models.Model):
	owner = models.ForeignKey(User)
	members = models.ManyToManyField(Contact)

class EmailPreferences(models.Model):
	private_posts = models.BooleanField(default=True)
	private_commments = models.BooleanField(default=True)

	public_posts = models.BooleanField(default=True)
	public_commments = models.BooleanField(default=False)

	digest = models.BooleanField(default=True)
	digest_timeframe_days = models.IntegerField(default=1)

class User(models.Model):
	friends = models.ManyToManyField(Contact)
	email = models.EmailField()
	profile_picture = models.URLField()
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email_preferences = models.OneToOneField(EmailPreferences)
	activated = models.BooleanField(default=False)


class Content(models.Model):
	link = models.URLField()
	picture = models.URLField()

class Post(models.Model):
	author = models.ForeignKey(User)
	recipients = models.ManyToManyField(User)
	subject = models.CharField(max_length=50)
	text = models.TextField()
	content = models.ManyToManyField(Content)
	likes = models.IntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)
	is_public = models.BooleanField(default=False)

class Comment(models.Model):
	post = models.ForeignKey(Post)
	author = models.ForeignKey(User)
	text = models.TextField()
	content = models.ManyToManyField(Content)
	likes = models.IntegerField()
	timestamp = models.DateTimeField(auto_now_add=True)

class Digest(models.Model):
	user = models.ForeignKey(User)
	posts = models.ManyToManyField(Post)
	comments = models.ManyToManyField(Comment)
	timestamp = models.DateTimeField(auto_now_add=True)

class Attachment(models.Model):
	link = models.URLField()

#These are for logging. We do not currently expect to access them
class Email(models.Model):
    headers = models.TextField()
    text = models.TextField()
    html = models.TextField()
    sender = models.TextField()
    to = models.TextField()
    cc = models.TextField()
    subject = models.TextField()
    dkim = models.TextField()
    SPF = models.TextField()
    envelope = models.TextField()
    charsets = models.CharField(max_length=255)
    spam_score = models.FloatField()
    spam_report = models.TextField()
    attachments = models.ManyToManyField(Attachment)
    timestamp = models.DateTimeField(auto_now_add=True)



