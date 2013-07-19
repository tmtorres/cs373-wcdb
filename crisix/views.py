from django.shortcuts import redirect
from django.http import HttpResponse
from database.models import *
from django.shortcuts import render_to_response
from django.template import RequestContext

def index(request):
    return redirect('crisix/index.html')

def people(request, id):
    return HttpResponse('Person page with id = ' + str(id).lower() + '.')

def organizations(request, id):
    return HttpResponse('Organization page.')

def crises(request, id):
    c = Crisis.objects.get(id='CRI_'+str(id).upper())
    #return HttpResponse(c.name)
    return render_to_response('crisis.html', {
        'c' : c, 
        'related_people' : [{'id': str(p.id).lstrip('PER_').lower(), 'name': p.name} for p in c.people.all()],
        'related_orgs' : [{'id': str(o.id).lstrip('ORG_').lower(), 'name': o.name} for o in c.organizations.all()],
        'citations' : [{'href': w.href, 'text': w.text} for w in c.elements.filter(ctype='CITE')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in c.elements.filter(ctype='MAP')],
        'images' : [{'embed': w.embed, 'text': w.text} for w in c.elements.filter(ctype='IMG')],
        'videos' : [{'embed': w.embed, 'text': w.text} for w in c.elements.filter(ctype='VID')],
        }, context_instance=RequestContext(request))
