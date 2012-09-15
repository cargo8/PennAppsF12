from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpRequest
from django.template import Context, RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
from django.views.generic.simple import direct_to_template
import SmtpApiHeader
import json
from django.core.mail import EmailMultiAlternatives
from emailr.models import *
from django.views.decorators.http import require_POST
from emailr.forms import TryItForm
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

def renderEmail(request):

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
    #msg.send()

    c = RequestContext(request, {

        })
    return render_to_response('email.html', c)

@require_POST
@csrf_exempt 
def receiveEmail(request):
    email_form = {}
    for key in request.POST.keys():
        if 'from' == key.lower():
            email_form['sender'] = request.POST[key]
        email_form[key] = request.POST[key]
   
    form = Email(email_form)
    if form.is_valid():
        form.instance.save()
        for i in range(1,form.cleaned_data['attachments']+1):
            attachment = request.FILES['attachment%d' % i]
            #Use filepicker.io file = attachment.read()
            link = None
            form.instance.attachments.create(link=link)
    contacts = None #parseContacts(None, None)
    #post = generatePost(form, contacts)
    return HttpResponse()

def parseContacts(user, input_strings):
    for emails in input_strings:
        if ";" in emails:
            email_list = emails.split(";")
        else:
            email_list = emails.split(",")
        for email in email_list:
            email_parts = email.replace('<', ' ').replace('>', ' ').split(" ")
            address = [x.strip() for x in email_parts]
            name = [x.strip() for x in email_parts if x not in address]
            if len(address) == 1:
                address = address[0]
                print address
                contact_user = User.objects.get(email = address.lower())
                if contact_user is None:
                    contact_user = User.objects.create(email = address.lower())
                    contact_user.save

                contacts = user.instance.contacts.filter(user = contact_user)

                if contact is None:
                    contact = user.instance.contacts.create(user = contact_user)

# generates a post out of the email and its recipients
"""
def generatePost(email, recipients):
    post = Post()
    post.author = User.objects.get(email = email.from)
    post.recipients = recipients
    post.subject = email.subject

    # refine the email's message
    post.text = ""
    lines = email.text.split("\n")
    for line in lines:
      if "r#" in line:
        continue
      else:
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
    post.timestampt = email.timestampt
    return post
"""
