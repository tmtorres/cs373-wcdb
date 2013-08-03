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
import glob, os, itertools, imagehash, re
from itertools import izip_longest

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def index(request):
    crises = [{'id': str(c.id).lower()[4:], 'name': c.name} for c in Crisis.objects.all()]
    organizations = [{'id': str(o.id).lower()[4:], 'name': o.name} for o in Organization.objects.all()]
    people = [{'id': str(p.id).lower()[4:], 'name': p.name} for p in Person.objects.all()]
    return render(request, 'index.html', {'crises' : crises, 'organizations' : organizations, 'people' : people})

def display(request, etype = ''):
    return HttpResponse(etype + ' list page.')

def thumbnails(e, n = 3):
    hash = dict([(i.hash, i) for i in e.elements.filter(ctype='IMG').exclude(hash=None)])
    if len(hash) < n:
        imgs = e.elements.filter(ctype='IMG').filter(hash=None)
        for i in imgs:
            if not i.thumb:
                i.thumb = str(i.entity.id).lower() + str(i.id) + '.thumbnail'
            path = os.path.join(settings.THUMB_ROOT, i.thumb)
            if not os.path.exists(path):
                urlretrieve(i.embed, path)
                t = Image.open(path)
                i.hash = str(imagehash.average_hash(t))
                if i.hash in hash:
                    os.remove(path)
                    i.delete()
                else:
                    hash[i.hash] = i
                    t.thumbnail((180, t.size[1]) if t.size[0] < t.size[1] else (t.size[0], 180))
                    t = t.crop((0, 0, 180, 180))
                    t.save(path, 'PNG')
                    i.save()
            if len(hash) == n:
                break
    return hash.values()[:n]

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def paragraphs(li_field):
    li_field = ''.join(li_field.split('<li>')).replace('</li>', ' ').strip()
    sentences = [' '.join(g) for g in grouper([s for s in re.split("(\S.+?[.!?])(?=\s+|$)", li_field) if len(s.strip())], 3, '')]
    return sentences

def people(request, id):
    p = Person.objects.get(id='PER_' + str(id).upper())
    return render(request, 'person.html', {
        'p' : p,
        'related_crises' : [{'id': str(c.id).lower()[4:], 'name': c.name} for c in p.crises.all()],
        'related_orgs' : [{'id': str(o.id).lower()[4:], 'name': o.name} for o in p.organizations.all()],
        'citations' : [{'href': w.href, 'text': w.text} for w in p.elements.filter(ctype='CITE')],
        'feeds' : [{'id': str(w.embed).split('/')[-1]} for w in p.elements.filter(ctype='FEED')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in p.elements.filter(ctype='MAP')],
        'images' : thumbnails(p),
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
        'history': ''.join(o.history.split('<li>')).replace('</li>', ' ').strip(),
        'feeds' : [{'id': str(w.embed).split('/')[-1]} for w in o.elements.filter(ctype='FEED')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in o.elements.filter(ctype='MAP')],
        'images' : thumbnails(o),
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
        'eimpact': paragraphs(c.eimpact),
        'resources': paragraphs(c.resources),
        'help' : [{'href': li.attrib.get('href'), 'text': li.text} for li in fromstring('<WaysToHelp>' + c.help + '</WaysToHelp>')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in c.elements.filter(ctype='MAP')],
        'images' : thumbnails(c),
        'videos' : [{'embed': w.embed, 'text': w.text} for w in list(c.elements.filter(ctype='VID'))[:1]],
        'external': [{'href': w.href, 'text': w.text} for w in c.elements.filter(ctype='LINK')],
        })
