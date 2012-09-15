from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpRequest
from django.template import Context, RequestContext, TemplateDoesNotExist
from django.shortcuts import render_to_response, redirect
from django.views.generic.simple import direct_to_template

def renderEmail(request):

    c = RequestContext(request, {
            
        })
    return render_to_response('postcard.html', c)
