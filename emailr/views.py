#from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpRequest
#from django.template import Context, RequestContext, TemplateDoesNotExist
#from django.template.loader import render_to_string
#from django.shortcuts import render_to_response, redirect
#from django.views.generic.simple import direct_to_template
#import SmtpApiHeader
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

def renderEmail(from_email, receiver_email, subject, post, commment = None):

    hdr = SmtpApiHeader.SmtpApiHeader()
    # The list of addresses this message will be sent to
    receiver = ['jason.mow@gmail.com', 'jason@jasonmow.com']

    # Another subsitution variable
    names = ['Jason', 'Jason']

    # Set all of the above variables
    hdr.addTo(receiver)
    hdr.addSubVal('-name-', names)

    # Specify that this is an initial contact message
    hdr.setCategory("initial")

    # Enable a text footer and set it
    hdr.addFilterSetting('footer', 'disable', 1)
    # hdr.addFilterSetting('footer', "text/plain", "Thank you for your business")

    # fromEmail is your email
    # toEmail is recipient's email address
    # For multiple recipient e-mails, the 'toEmail' address is irrelivant
    fromEmail =  'info@emailr.co'
    toEmail = 'info@emailr.co'

    # Create message container - the correct MIME type is multipart/alternative.
    # Using Django's 'EmailMultiAlternatives' class in this case to create and send.
    # Create the body of the message (a plain-text and an HTML version).

    # text is your plain-text email
    # html is your html version of the email
    # if the reciever is able to view html emails then only the html
    # email will be displayed

    subject = 'Hi <-name->, you have been sent an emailr'

    text_content = 'Hi -name-!\nHow are you?\n'

    html = render_to_string('email.html', {

    });

    msg = EmailMultiAlternatives(subject, text_content, fromEmail, [toEmail], headers={"X-SMTPAPI": hdr.asJSON()})
    msg.attach_alternative(html, "text/html")
    msg.send()

    c = RequestContext(request, {

        })
    return render_to_response('email.html', c)

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
    ccs_string = email.text.split('\n')[0]
    if "r#" in ccs_string:
        ccs_string = ccs_string.replace("r#", "")
    sender = User.objects.get_or_create(email = email.lower())
    contacts = parseContacts(sender , ccs_string)
    post = generatePost(email, sender, contacts)

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
    contacts = re.findall('([a-zA-Z,]+)(\s[a-zA-Z]+)?\s+<(([^<>,;"]+|".+")+)>(,\s+)?', ccs_string)
    recipients = []

    for contact in contacts:
        email = [x for x in contact if '@' in x]
        if len(email) < 1:
            continue

        email = email[0]
        contact_user = User.objects.get_or_create(email = email.lower())[0]
        contact_user.save()
        recipients.append(contact_user)

        if(email in contact[:2]):
            first_name = contact[0]
            last_name = None
        else:
            last_name = contact[1]
            first_name = contact[0]
            if first_name[-1] = ',':
                last_name = first_name
                first_name = contact[1]

        contact = user.instance.contacts.get_or_create(user = contact_user, first_name = first_name, last_name = last_name)
        contact.save()
    return recipients


# generates a post out of the email and its recipients
def generatePost(email, sender, recipients):
    post = Post()
    post.author = sender
    post.recipients = recipients
    post.subject = email.subject

    # refine the email's message
    post.text = ""
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
    return post
