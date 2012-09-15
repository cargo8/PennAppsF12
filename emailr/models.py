from django.db import models
from django.contrib.auth.models import User

class Contact(models.Model):
	user = models.ForeignKey(User)
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)

class Group(models.Model):
	owner = models.ForeignKey(User)
	members = models.ManyToManyField(Contact)

class User(models.Model):
	contacts = models.ManyToManyField(Contact)
	email = models.EmailField()
	profile_picture = Models.URLField()
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	email_preferences = models.OneToOneField(EmailPreferences)
	activated = models.BooleanField(default=False)

class Content(models.Model):
	link = Models.URLField()
	picture = Models.URLField()

class Post(models.Model):
	author = models.ForeignKey(User)
	recipients = models.ManyToManyField(User)
	subject = models.CharField(max_length=50)
	text = models.TextField()
	content = models.ManyToManyField(Content)
	likes = models.IntegerField()
	timestamp = models.DateField()
	is_public = models.BooleanField(default=False)

class Comment(models.Model):
	post = models.ForeignKey(Post)
	author = models.ForeignKey(User)
	text = models.TextField()
	content = models.ManyToManyField(Content)
	likes = models.IntegerField()
	timestamp = models.DateField()

class EmailPreferences(models.Model):
	private_posts = models.BooleanField(default=True)
	private_commments = models.BooleanField(default=True)

	public_posts = models.BooleanField(default=True)
	public_commments = models.BooleanField(default=False)

	digest = models.BooleanField(default=True)
	digest_timeframe_days = models.IntegerField(default=1)

class Digest(models.Model):
	user = models.ForeignKey(User)
	posts = models.ManyToManyField(Post)
	comments = models.ManyToManyField(Comment)
	timestamp = models.DateField()


class Email(models.Model):
    headers = TextField()
    text = TextField()
    html = TextField()
    to = TextField()
    cc = TextField()
    subject = TextField()
    dkim = JSONField()
    SPF = JSONField()
    envelope = JSONField()
    charsets = CharField(max_length=255)
    spam_score = FloatField()
    spam_report = TextField()
    attachments = ManyToManyField(Attachment)

class Attachment(models.Model)
	link = Models.URLField()
