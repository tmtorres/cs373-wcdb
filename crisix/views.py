from django.shortcuts import redirect, render, render_to_response
from django.http import HttpResponse
from database.models import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from xml.etree.ElementTree import fromstring
from xml.etree.ElementTree import ElementTree, Element
from django.conf import settings
from django.core.files import File
from PIL import Image
from urllib import urlretrieve
import glob, os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def index(request):
    crises = [{'id': str(c.id).lower()[4:], 'name': c.name} for c in Crisis.objects.all()]
    organizations = [{'id': str(o.id).lower()[4:], 'name': o.name} for o in Organization.objects.all()]
    people = [{'id': str(p.id).lower()[4:], 'name': p.name} for p in Person.objects.all()]
    return render(request, 'index.html', {'crises' : crises, 'organizations' : organizations, 'people' : people})

def display(request, etype = ''):
    return HttpResponse(etype + ' list page.')

def thumbnail(e):
    r = iter(xrange(0, 3))
    imgs = [i for i in e.elements.filter(ctype='IMG') if str(i.embed).split('/')[-1].split('.')[-1].upper() in ('JPG', 'JPEG', 'PNG', 'GIF')][:3]
    thumbs = [{'embed': w.embed, 'text': w.text, 'file': str(w.entity.id).lower() + str(r.next()) + '.thumbnail'} for w in imgs]
    for t in thumbs:
        tmp = os.path.join(settings.THUMB_ROOT, t['file'])
        if not os.path.exists(tmp):
            urlretrieve(t['embed'], tmp)
            im = Image.open(tmp)
            im.thumbnail((180, im.size[1]) if im.size[0] < im.size[1] else (im.size[0], 180))
            th = im.crop((0, 0, 180, 180))
            th.save(tmp, 'PNG')
    return thumbs

def people(request, id):
    p = Person.objects.get(id='PER_' + str(id).upper())
    return render(request, 'person.html', {
        'p' : p,
        'related_crises' : [{'id': str(c.id).lower()[4:], 'name': c.name} for c in p.crises.all()],
        'related_orgs' : [{'id': str(o.id).lower()[4:], 'name': o.name} for o in p.organizations.all()],
        'citations' : [{'href': w.href, 'text': w.text} for w in p.elements.filter(ctype='CITE')],
        'feeds' : [{'id': str(w.embed).split('/')[-1]} for w in p.elements.filter(ctype='FEED')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in p.elements.filter(ctype='MAP')],
        'images' : thumbnail(p),
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
        'contact' : [{'href': li.attrib.get('href'), 'text': li.text} for li in fromstring('<ContactInfo>' + o.contact + '</ContactInfo>')],
        'feeds' : [{'id': str(w.embed).split('/')[-1]} for w in o.elements.filter(ctype='FEED')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in o.elements.filter(ctype='MAP')],
        'images' : thumbnail(o),
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
        'images' : thumbnail(c),
        'videos' : [{'embed': w.embed, 'text': w.text} for w in list(c.elements.filter(ctype='VID'))[:2]],
        'external': [{'href': w.href, 'text': w.text} for w in c.elements.filter(ctype='LINK')],
        })
