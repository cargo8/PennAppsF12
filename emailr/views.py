#from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpRequest
#from django.template import Context, RequestContext, TemplateDoesNotExist
#from django.template.loader import render_to_string
#from django.shortcuts import render_to_response, redirect
#from django.views.generic.simple import direct_to_template
#import SmtpApiHeader
import json
import re
#from django.core.mail import EmailMultiAlternatives
#from emailr.models import *
#from django.views.decorators.http import require_POST
#from emailr.forms import TryItForm

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
def receiveEmail(request):
    print request
    if 'from' in request.POST.keyset():
        request.POST['sender'] = request.POST['from']
        del request.POST['from']
    form = EmailForm(request.POST)
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
    for contact in contacts:
        for i in range(len(contact)):
            contact_user = User.objects.get_or_create(email = contact[2].lower(), first_name = contact[0], last_name = contact[1])[0]
            contact_user.save()
            contact = user.instance.contacts.get_or_create(user = contact_user)
            contact.save()

# generates a post out of the email and its recipients
def generatePost(email, recipients):
    post = Post()
    post.author = User.objects.get(email = email.sender)
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
    post.timestamp = email.timestamp
    return post
