from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpRequest
from django.template import Context, RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django.shortcuts import render_to_response, redirect
from django.views.generic.simple import direct_to_template
import SmtpApiHeader
import json
from django.core.mail import EmailMultiAlternatives

def index(request):
    return render_to_response('index.html')

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

def receiveEmail(request):
    if request.method != 'POST' :
        raise Http404('Only POSTs allowed')
    
    
