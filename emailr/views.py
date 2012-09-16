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

def sendPostEmail(request):

    pref1 = EmailPreferences()
    pref1.save()
    pref2 = EmailPreferences()
    pref2.save()
 
    user1 = User(first_name = 'Jason', last_name = 'Mow', activated = True, email = 'jason.mow@gmail.com',)
    user1.save()

    user2 = User(first_name = 'Ron', last_name = 'Weasley', activated = True, email = 'jason@jasonmow.com', email_preferences = EmailPreferences())
    user2.save()
    
    post = Post(author = user1, subject = 'Testing out Emailr Templates', text = 'Hey I just want to test that this template works', likes = 0)
    post.save()

    hdr = SmtpApiHeader.SmtpApiHeader()
    # The list of addresses this message will be sent to
    #TODO: extract recipient emails from User objects
    recipients = post.recipients

    hdr.addTo(recipients)

    # Specify that this is an initial contact message
    hdr.setCategory("initial")

    # toEmail is recipient's email address
    # For multiple recipient e-mails, the 'toEmail' address is irrelivant
    fromEmail =  'info@emailr.co'
    # toEmail = 'info@emailr.co'

    # text is your plain-text email
    # html is your html version of the email
    # if the reciever is able to view html emails then only the html
    # email will be displayed

    subject = 'Hi <-name->, you have been sent an emailr'
    
    name =  post.author.first_name + " " + post.author.last_name
    text_content = name + " has shared something with you using Emailr:\n\n" + post.text
    text_content += "\n\n\nIf you would like to comment on this post just reply to this email."

    html = render_to_string('postcard.html', {
        
    });

    msg = EmailMultiAlternatives(subject, text_content, fromEmail, [toEmail], headers={"X-SMTPAPI": hdr.asJSON()})
    msg.attach_alternative(html, "text/html")
    #msg.send()

    c = RequestContext(request, {

        })
    return render_to_response('postcard.html', c)

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
    else:
            print "F*CK THIS"

    sender = User.objects.get_or_create(email = email.sender)
    sender.save()

    contacts = parseContacts(sender, email.cc)
    # post = generatePost(email, contacts)
    # sendPostEmail(post)
    return HttpResponse()

# @params:
#   (User) user
#   (String) ccs_string of the format:
#       <name> <\<email\>>[, or ;] . . .
#       example:
#           bobby bo <hhaf@adfads.com>, john <email@gmail.com>
# @does:
#   Adds contacts to user
def parseContacts(user, ccs_string):
    contacts = re.findall('([a-zA-Z]+)(\s[a-zA-Z]+)?\s+<(([^<>,;"]+|".+")+)>(,\s+)?', ccs_string)
    recipients = []

    for contact in contacts:
        for i in range(len(contact)):
            c_fname = contact_user[0]
            c_lname = c_email = ""
            for i in range(1, len(contact_user)):
                if "@" in contact_user[i]:
                    c_email = contact_user[i]
                    break
                c_lname += contact_user[i] + " "
            c_lname = c_lname.strip()
           
            # find or create user from parsed info 
            contact_user = User.objects.get_or_create(email = c_email.lower(), first_name = c_fname, last_name = c_lname)[0]
            contact_user.save()
            
            # add parsed user to recipient list
            recipients.append(contact_user)

            # add new contact user to sender's contacts
            contact = user.instance.contacts.get_or_create(user = contact_user)
            contact.save()

    return recipients

# generates a post out of the email and its recipients
def generatePost(email, recipients):
    post = Post()
    post.author = User.objects.get(email = email.sender)
    post.recipients = recipients
    post.subject = email.subject

    post.text = email.text
    #lines = email.text.split("\n")
    lines = re.split(r'[\n\r]+', email.text)
    for line in lines:
      if not "r#" in line:
        post.text += line

    # extract images/links from Attachments
    for att in email.attachments:
      link = att.link
      ext = link.split(".")[-1].lower()
      cnt = Content()
      if ext in ["jpg", "png", "gif"]:
        cnt.link = None
        cnt.picture = link
      else:
        cnt.link = link
        cnt.picture = None
      post.instance.content.add(cnt)

    post.likes = 0
    post.timestamp = email.timestamp
    return post
