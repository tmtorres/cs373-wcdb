from django.shortcuts import redirect, render, render_to_response
from django.http import HttpResponse
from database.models import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from xml.etree.ElementTree import fromstring
from xml.etree.ElementTree import ElementTree, Element

def index(request):
    return redirect('crisix/')

def home(request):
    crises = [{'id': str(c.id).lower()[4:], 'name': c.name} for c in Crisis.objects.all()]
    organizations = [{'id': str(o.id).lower()[4:], 'name': o.name} for o in Organization.objects.all()]
    people = [{'id': str(p.id).lower()[4:], 'name': p.name} for p in Person.objects.all()]
    return render(request, 'index.html', {'crises' : crises, 'organizations' : organizations, 'people' : people})

def display(request, etype = ''):
    return HttpResponse(etype + ' list page.')

def people(request, id):
    return HttpResponse('Person page with id = ' + str(id).lower() + '.')

def organizations(request, id):
    return HttpResponse('Organization page.')

def crises(request, id):
    c = Crisis.objects.get(id='CRI_' + str(id).upper())
    return render(request, 'crisis.html', {
        'c' : c, 
        'related_people' : [{'id': str(p.id).lower()[4:], 'name': p.name} for p in c.people.all()],
        'related_orgs' : [{'id': str(o.id).lower()[4:], 'name': o.name} for o in c.organizations.all()],
        'citations' : [{'href': w.href, 'text': w.text} for w in c.elements.filter(ctype='CITE')],
        'help' : [{'href': li.attrib.get('href'), 'text': li.text} for li in fromstring('<WaysToHelp>' + c.help + '</WaysToHelp>')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in c.elements.filter(ctype='MAP')],
        'images' : [{'embed': w.embed, 'text': w.text} for w in c.elements.filter(ctype='IMG')],
        'videos' : [{'embed': w.embed, 'text': w.text} for w in c.elements.filter(ctype='VID')],
        })
