from django.db import models
from django.contrib.auth.models import User as UserCred

class User(models.Model):
    cred = models.OneToOneField(UserCred, related_name = 'user_cred', null=True)
    friends = models.ManyToManyField('self', null=True)
    email = models.EmailField()
    profile_picture = models.URLField(null=True)
    first_name = models.CharField(max_length=50, null=True)
    last_name = models.CharField(max_length=50, null=True)
    activated = models.BooleanField(default=False)

class MailingListGroup(models.Model):
    owner = models.ForeignKey(User, related_name='mailing_list_owner')
    members = models.ManyToManyField(User, related_name='mailing_list_members')

class Content(models.Model):
    WEBSITE = 0
    PICTURE = 1
    FILE = 2

    LINK_TYPE = (
        (WEBSITE, 'Website'),
        (PICTURE, 'Picture'),
        (FILE, 'File'),
    )

    link = models.URLField()
    link_type = models.IntegerField(null=False, choices=LINK_TYPE)
    

class Post(models.Model):
    author = models.ForeignKey(User, related_name='post_author')
    recipients = models.ManyToManyField(User, related_name='recipients')
    subject = models.CharField(max_length=50)
    text = models.TextField()
    content = models.ManyToManyField(Content)
    likes = models.ManyToManyField(User, related_name='post_likes')
    timestamp = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)

class Comment(models.Model):
    post = models.ForeignKey(Post)
    author = models.ForeignKey(User, related_name='comment_author')
    text = models.TextField()
    content = models.ManyToManyField(Content)
    likes = models.ManyToManyField(User, related_name='comment_likes')
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
    attachments = models.ManyToManyField(Attachment)
    timestamp = models.DateTimeField(auto_now_add=True)



