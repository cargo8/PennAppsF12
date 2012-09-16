from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpRequest
from django.template import Context, RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
from django.views.generic.simple import direct_to_template
import SmtpApiHeader
import json
import re
from django.core.mail import EmailMultiAlternatives
from emailr.models import *
from django.views.decorators.http import require_POST
from emailr.forms import *
from django.views.decorators.csrf import csrf_exempt

def index(request):
    if request.method == 'POST':
        form = TryItForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            #TODO: Send the email
            return render_to_response('index.html', {'form': form})
    else:
        form = TryItForm()
    return render_to_response('index.html', {'form': form})

def signup(request):
    return render_to_response('signup.html')

def login(request):
    return render_to_response('login.html')

def renderComment(recipient, comment):
    #Check if recipent = comment.author
    pass

def testRender(request):
    return render_to_response('one_img_post.html')


def renderPost(recipient, post):
    #Check if recipent = post.author
    hdr = SmtpApiHeader.SmtpApiHeader()

    # Specify that this is an initial contact message
    hdr.setCategory("initial")  
    replyToEmail = "p" + str(comment.post.id) + "@emailr.co"
    hdr.setReplyTo(replyToEmail)

    fromEmail =  "info@emailr.co"
    toEmail = recipent.email

    # text is your plain-text email
    # html is your html version of the email
    # if the reciever is able to view html emails then only the html
    # email will be displayed

    subject = post.subject
    
    is_author = recipent == post.author

    name =  post.author.first_name + " " + post.author.last_name
    text_content = name + " has shared something with you using Emailr:\n\n" + post.text
    text_content += "\n\n\nIf you would like to comment on this post just reply to this email."

    pictures = []
    links = []
    files = []

    for attachment in post.attachments:
        if attachment.link_type == attachment.PICTURE:
            pictures.append(attachment)
        elif attachment.link_type == attachment.WEBSITE:
            links.append(attachment)
        else:
            files.append(attachment)

    template = None
    inputs = {'post' : post, 'recipent' : recipent, 'is_author' : is_author}
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


        #

    html = render_to_string(template, inputs);

    msg = EmailMultiAlternatives(subject, text_content, fromEmail, [toEmail], headers={"X-SMTPAPI": hdr.asJSON()})
    msg.attach_alternative(html, "text/html")
    #msg.send()

    c = RequestContext(request, inputs)
    return render_to_response(template, c)

@require_POST
@csrf_exempt 
def receiveEmail(request):
    output = {}

    data = request.POST
    print data
    
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

    for i in range(1,attachments+1):
        attachment = request.FILES['attachment%d' % i]
        #Use filepicker.io file = attachment.read()
        link = None
        email.attachments.create(link=link)

    #This is for a new post
    ###########################################
    ccs_string = email.text.split('\n')[0]
    if "r#" in ccs_string:
        ccs_string = ccs_string.replace("r#", "")
    sender = User.objects.get_or_create(email = email)[0]
    contacts = parseContacts(sender , ccs_string)
    post = generatePost(email, sender, contacts)
    
    renderPost(sender, post)
    for contact in contacts:
        renderPost(contact, post)
    ##

    #Comment
    """
    renderComment(sender, post)
    for contact in contacts:
        renderComment(contact, post)
    """
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
    contacts = re.findall('(([^, ]+)(\s*,\s*)?)', ccs_string)
    recipients = []

    for contact in contacts:
        c_email = contact[1]
           
        # find or create user from parsed info 
        contact_user = user.instance.contacts.get_or_create(email = c_email.lower())[0]
        contact_user.save()
        
        # add parsed user to recipient list
        recipients.append(contact_user)

        # add new contact user to sender's contacts
        contact = user.instance.contacts.get_or_create(user = contact_user)[0]

        contact.save()

    return recipients

# generates a post out of the email and its recipients
def generatePost(email, sender, recipients):
    post = Post()
    post.author = sender
    post.save()
    post.recipients = recipients
    post.subject = email.subject

    post.text = email.text
    #lines = email.text.split("\n")
    lines = re.split(r'[\n\r]+', email.text)
    for line in lines:
      if not "r#" in line:
        post.text += line

    # extract images/links from Attachments
    for att in email.instance.attachments:
      link = att.link
      ext = link.split(".")[-1].lower()
      cnt = Content()
      cnt.link = link
      if ext in ["jpg", "png", "gif"]:
        cnt.link_type = cnt.PICTURE
      else:
        cnt.link_type = cnt.FILE
    post.instance.content.add(cnt)

    return post.save()[0]
