from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpRequest
from django.template import Context, RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
from django.views.generic.simple import direct_to_template
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from django.contrib import auth
import SmtpApiHeader
import json
import re
from django.core.mail import EmailMultiAlternatives
from emailr.models import *
from django.views.decorators.http import require_POST
from emailr.forms import *
from django.views.decorators.csrf import csrf_exempt

#######################################################
###### WEB CLIENT VIEW CODE ###########################
#######################################################

def index(request):
    if request.user.is_authenticated:
        return redirect(home)
    if request.method == 'POST':
        form = TryItForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            #TODO: Send the email
            return render_to_response('index.html', {'form': form})
    else:
        form = TryItForm()
    return render_to_response('index.html', {'form': form, 'request': request})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            u = User.objects.get_or_create(email = request.POST['username'])[0]
            u.save()
            u.auth = new_user
            u.save()
            return redirect(register)
    else:
        form = UserCreationForm()

    c = RequestContext(request, {'request': request, 'form': form})

    return render_to_response("signup.html", c)
    
def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            return redirect(home)
        else:
            return redirect(index)
            #render_to_response('login.html', {'form':form})
    else:
        form = LoginForm()

    c = RequestContext(request, {'request':request, 'form': form})
    return render_to_response("login.html", c)

def logout(request):
    auth.logout(request)
    form = TryItForm()
    return render_to_response('index.html', {'request': request, 'form': form, 'msg': 'You have successfully logged out.'})

def register(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            user = User.objects.get_or_create(email = request.POST['email'])[0]
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.save()

            user.activated = True
            user.save()
            return render_to_response("index.html", {'request':request})
    else:
        form = ProfileForm()
        
    c = RequestContext(request, {'request':request, 'form': form})
    return render_to_response("register.html", c)

def home(request):
    c = RequestContext(request, {'request': request})
    return render_to_response('home.html', c)
    
def talks(request):
    return render_to_response("home.html")

def testRender(request):
    return render_to_response('one_img_post.html')

#######################################################
###### BACKEND PROCESSING CODE ########################
#######################################################

def renderPost(recipient, post):
    #Check if recipent = post.author
    hdr = SmtpApiHeader.SmtpApiHeader()

    # Specify that this is an initial contact message
    hdr.setCategory("initial")  
    replyToEmail = "p" + str(post.id) + "@emailr.co"
    
    fromEmail =  "info@emailr.co"
    toEmail = recipient.email.strip()

    # text is your plain-text email
    # html is your html version of the email
    # if the reciever is able to view html emails then only the html
    # email will be displayed

    subject = post.subject
    
    is_author = recipient == post.author

    name =  ""
    if post.author.first_name:
        name = post.author.first_name
    if post.author.last_name:
        name += post.author.last_name
    if len(name) < 1:
        name = post.author.email

    text_content = name + " has shared something with you using Emailr:\n\n" + post.text
    text_content += "\n\n\nIf you would like to comment on this post just reply to this email."

    pictures = []
    links = []
    files = []

    for attachment in post.content.all():
        if attachment.link_type == attachment.PICTURE:
            pictures.append(attachment)
        elif attachment.link_type == attachment.WEBSITE:
            links.append(attachment)
        else:
            files.append(attachment)

    template = None
    inputs = {'post' : post, 'recipent' : recipient, 'is_author' : is_author}

    if recipient in post.likes.all():
        inputs['liked'] = 1
    else:
        inputs['liked'] = 0

    inputs['likes'] = len(post.likes)

    if len(pictures) > 1:
        template = 'two_img_post.html'
        inputs['img1'] = pictures[0]
        inputs['img2'] = pictures[1]
        inputs['other_attachments'] = pictures[2:] + links + files
    elif len(pictures) == 1:
        template = 'one_img_post.html'
        inputs['img1'] = pictures[0]
        inputs['other_attachments'] = links + files
    elif len(links) > 0:
        template = 'link_post.html'
        if len(links) > 1:
            inputs['other_attachments'] = links[1:] + files
        else:
            inputs['other_attachments'] = files
    else:
        template = 'text_post.html'
        inputs['other_attachments'] = files

    html = render_to_string(template, inputs);

    msg = EmailMultiAlternatives(subject, text_content, fromEmail, [toEmail], headers={"Reply-To" : replyToEmail, "X-SMTPAPI": hdr.asJSON()})
    msg.attach_alternative(html, "text/html")
    msg.send()
    

def renderComment(recipient, comment):
    hdr = SmtpApiHeader.SmtpApiHeader()
    hdr.setCategory("initial")  
    replyToEmail = "p" + str(comment.post.id) + "c" + str(comment.id) + "@emailr.co"
    
    fromEmail =  "info@emailr.co"
    toEmail = recipient.email.strip()

    is_author = recipient == comment.author

    template = None
    inputs = {'comment' : comment, 'recipent' : recipient, 'is_author' : is_author}

    html = render_to_string(template, inputs);
    
    msg = EmailMultiAlternatives(subject, text_content, fromEmail, [toEmail], headers={"Reply-To" : replyToEmail, "X-SMTPAPI": hdr.asJSON()})
    msg.attach_alternative(html, "text/html")
    msg.send()

@require_POST
@csrf_exempt 
def receiveEmail(request):
    output = {}

    data = request.POST
    attachments = 0

    if 'from' in data.keys():
        if type(data['from']) is list:
            output['sender'] = "; ".join(data['from'])
        else:
            output['sender'] = data['from']
    if 'attachments' in data.keys():
        attachments = data['attachments']
        if type(attachments) is list:
            attachments = attachments[0]

    if 'to' in data.keys():
        if type(data['to']) is list:
            output['to'] = "; ".join(data['to'])
        else:
            output['to'] = data['to']
    if 'cc' in data.keys():
        output['cc'] = "; ".join(data['cc'])
    if 'text' in data.keys():
        output['text'] = data['text']

    if 'headers' in data.keys():
        output['headers'] = data['headers']
    if 'html' in data.keys():
        output['html'] = data['html']
    if 'subject' in data.keys():
        output['subject'] = data['subject']

    email = Email(**output)
    email.save()

    for i in range(1,int(attachments)+1):
        attachment = request.FILES['attachment%d' % i]
        #Use filepicker.io file = attachment.read()
        link = None
        email.attachments.create(link=link)
    sender_email = re.findall('(([^, ]+)(\s*,\s*)?)', email.sender)
    first_last = email.sender.split(" ")
    first_name = None
    last_name = None
    if "@" not in first_last[0]:
        if "," not in first_last[0]:
            first_name = first_last[0]
        else:
            last_name = first_last[0]
        if len(first_last) > 2 and "@" not in first_last[1]:
            if last_name:
                first_name = first_last[1]
            else:
                last_name = first_last[1]

    sender = User.objects.get_or_create(email = sender_email[0][1])[0]
    if not sender.first_name:
        sender.first_name = first_name
    if not sender.last_name:
        sender.last_name = last_name

    sender.save()
    if "info" in email.to:
        #This is for a new post
        ccs_string = email.text.split('\n')[0]
        if "r#" in ccs_string:
            ccs_string = ccs_string.replace("r#", "")
        else:
            ccs_string = None
        
        contacts = parseContacts(sender , ccs_string)
        post = generatePost(email, sender, contacts)
        try:
            renderPost(sender, post)
            for contact in contacts:
                renderPost(contact, post)
            print "HELLO WORLD"
        except Exception as e:
            print e.message
    to_groups = re.match('p(\d+)(c(\d+))?', email.to)
    if to_groups:
        post = Post.objects.get(id = to_groups.group(1))
        if to_groups.group(3):
            last_comment = Comment.objects.get(id = to_groups.group(3))
            content = []
            for att in email.attachments.all():
                link = att.link
                ext = link.split(".")[-1].lower()
                cnt = Content()
                cnt.link = link
                if ext in ["jpg", "png", "gif"]:
                    cnt.link_type = cnt.PICTURE
                else:
                    cnt.link_type = cnt.FILE
                content.add(cnt)
        comment = Comment.objects.create(author = sender, text = email.text, post = post, content = content)
        contacts = post.recipients + post.author
        for contact in contacts:
            renderComment(contact, comment)
    return HttpResponse()

# @params:
#   (User) user
#   (String) ccs_string of the format:
#       <name> <\<email\>>[, or ;] . . .
#       example:
#           bobby bo <hhaf@adfads.com>, john <email@gmail.com>
# @does:
#   Adds contacts to user
#@returns : all recipients

def parseContacts(user, ccs_string):
##    contacts = re.findall('([a-zA-Z]+)(\s[a-zA-Z]+)?\s+<(([^<>,;"]+|".+")+)>(,\s+)?', ccs_string)
##    recipients = []
##
##    for contact in contacts:
##        for i in range(len(contact)):
##            c_fname = contact_user[0]
##            c_lname = c_email = ""
##            for i in range(1, len(contact_user)):
##                if "@" in contact_user[i]:
##                    c_email = contact_user[i]
##                    break
##                c_lname += contact_user[i] + " "
##            c_lname = c_lname.strip()
    if ccs_string is None:
        return None
    contacts = re.findall('(([^, ]+)(\s*,\s*)?)', ccs_string)
    recipients = []

    for contact in contacts:
        c_email = contact[1]
           
        # find or create user from parsed info 
        
        contact_user = user.friends.get_or_create(email = c_email)[0]
        contact_user.save()
        
        # add parsed user to recipient list
        recipients.append(contact_user)
    return recipients

# generates a post out of the email and its recipients
def generatePost(email, sender, recipients):
    post = Post()
    post.author = sender
    post.save()
    post.recipients = recipients
    post.subject = email.subject

    #lines = email.text.split("\n")
    lines = re.split(r'[\n\r]+', email.text)
    for line in lines:
      if not "r#" in line:
        post.text += line

    # extract images/links from Attachments
    for att in email.attachments.all():
      link = att.link
      ext = link.split(".")[-1].lower()
      cnt = Content()
      cnt.link = link
      if ext in ["jpg", "png", "gif"]:
        cnt.link_type = cnt.PICTURE
      else:
        cnt.link_type = cnt.FILE
      post.content.add(cnt)
    post.save()
    return post
