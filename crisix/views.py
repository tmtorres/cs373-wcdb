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
    p = Person.objects.get(id='PER_' + str(id).upper())
    return render(request, 'person.html', {
        'p' : p,
        'related_crises' : [{'id': str(c.id).lower()[4:], 'name': c.name} for c in p.crises.all()],
        'related_orgs' : [{'id': str(o.id).lower()[4:], 'name': o.name} for o in p.organizations.all()],
        'citations' : [{'href': w.href, 'text': w.text} for w in p.elements.filter(ctype='CITE')],
        'feeds' : [{'id': str(w.embed).split('/')[-1]} for w in p.elements.filter(ctype='FEED')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in p.elements.filter(ctype='MAP')],
        'images' : [{'embed': w.embed, 'text': w.text} for w in list(p.elements.filter(ctype='IMG'))[:3]],
        'videos' : [{'embed': w.embed, 'text': w.text} for w in list(p.elements.filter(ctype='VID'))[:2]],
        'external': [{'href': w.href, 'text': w.text} for w in p.elements.filter(ctype='LINK')],
        })

def organizations(request, id):
    o = Organization.objects.get(id='ORG_' + str(id).upper())
    return render(request, 'organization.html', {
        'o' : o,
        'related_crises' : [{'id': str(c.id).lower()[4:], 'name': c.name} for c in o.crises.all()],
        'related_people' : [{'id': str(p.id).lower()[4:], 'name': p.name} for p in o.people.all()],
        'citations' : [{'href': w.href, 'text': w.text} for w in o.elements.filter(ctype='CITE')],
        'feeds' : [{'id': str(w.embed).split('/')[-1]} for w in o.elements.filter(ctype='FEED')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in o.elements.filter(ctype='MAP')],
        'images' : [{'embed': w.embed, 'text': w.text} for w in list(o.elements.filter(ctype='IMG'))[:3]],
        'videos' : [{'embed': w.embed, 'text': w.text} for w in list(o.elements.filter(ctype='VID'))[:2]],
        'external': [{'href': w.href, 'text': w.text} for w in o.elements.filter(ctype='LINK')],
        })

def crises(request, id):
    c = Crisis.objects.get(id='CRI_' + str(id).upper())
    return render(request, 'crisis.html', {
        'c' : c, 
        'related_people' : [{'id': str(p.id).lower()[4:], 'name': p.name} for p in c.people.all()],
        'related_orgs' : [{'id': str(o.id).lower()[4:], 'name': o.name} for o in c.organizations.all()],
        'citations' : [{'href': w.href, 'text': w.text} for w in c.elements.filter(ctype='CITE')],
        'help' : [{'href': li.attrib.get('href'), 'text': li.text} for li in fromstring('<WaysToHelp>' + c.help + '</WaysToHelp>')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in c.elements.filter(ctype='MAP')],
        'images' : [{'embed': w.embed, 'text': w.text} for w in list(c.elements.filter(ctype='IMG'))[:3]],
        'videos' : [{'embed': w.embed, 'text': w.text} for w in list(c.elements.filter(ctype='VID'))[:2]],
        'external': [{'href': w.href, 'text': w.text} for w in c.elements.filter(ctype='LINK')],
        })
