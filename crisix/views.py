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
import nltk

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.core.paginator import Paginator, InvalidPage, EmptyPage

def index(request):
    crises = [{'id': str(c.id).lower()[4:], 'name': c.name} for c in Crisis.objects.all()]
    organizations = [{'id': str(o.id).lower()[4:], 'name': o.name} for o in Organization.objects.all()]
    people = [{'id': str(p.id).lower()[4:], 'name': p.name} for p in Person.objects.all()]
    return render(request, 'index.html', {'crises' : crises, 'organizations' : organizations, 'people' : people})

def get_datetime(e):
    out = []
    if hasattr(e, 'date') and e.date is not None:
        out += [str(e.date)]
    if hasattr(e, 'time') and e.time is not None:
        out += [str(e.time)]
    return ', '.join(out).strip(', ')

def get_contact(e):
    if hasattr(e, 'contact') and len(e.contact) > 0:
        return ''.join([c for c in [v.attrib.get('href') for v in fromstring('<Contact>' + e.contact + '</Contact>')] if c is not None][:1])
    return ''

def get_icon(e):
    t = generate_thumbs(e, 1)
    if not len(t):
        return 'noimage.jpg'
    return t[0].thumb

def display(request, etype = ''):
    e = None
    order = 'name'
    if 'q' in request.GET:
        order = request.GET['q']
    if etype == 'people':
        e = Person.objects.all().order_by(order)
    elif etype == 'crises':
        e = Crisis.objects.all().order_by(order)
    elif etype == 'organizations':
        e = Organization.objects.all().order_by(order)
    entity_list = [{
            'type': etype,
            'datetime': get_datetime(v),
            'contact': get_contact(v),
            'name': v.name, 
            'kind': v.kind, 
            'location': v.location if '<li>' not in v.location else ''.join(v.location.split('<li>')).replace('</li>', ', ').rstrip(', '),
            'id': str(v.id).lower()[4:], 
            'summary': ' '.join(v.summary.split()[:50]) + ' ...' if len(v.summary) else '',
            'thumb': get_icon(v),
            } for v in e]
    paginator = Paginator(entity_list, 10)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        entity = paginator.page(page)
    except (EmptyPage, InvalidPage):
        entity = paginator.page(paginator.num_pages)

    return render(request, 'display.html', {
        'order': order,
        'entity': entity
        })

def display_more(request, etype = '', id = '', ctype = '') :

    if etype == 'organizations' :
        e = Organization.objects.get(id='ORG_' + str(id).upper())
    if etype == 'people' :
        e = Person.objects.get(id='PER_' + str(id).upper())
    if etype == 'crises' :
        e = Crisis.objects.get(id='CRI_' + str(id).upper())


    if(ctype == 'videos'):
        vids = e.elements.filter(ctype='VID').filter(hash=None)
        return render(request, 'more_photos_videos.html', {
            'etype' : etype,
            'e' : e,
            'ctype' : ctype,
            'id' : id,
            'videos' : vids,
            'name' : e.name,
            })

    return render(request, 'more_photos_videos.html', {
        'etype' : etype,
        'e' : e,
        'ctype' : ctype,
        'id' : id,
        'name' : e.name,
        'images' : generate_thumbs(e, len(e.elements.filter(ctype='IMG'))),
        })



def generate_thumbs(e, n = 3):
    hash = dict([(i.hash, i) for i in e.elements.filter(ctype='IMG').exclude(hash=None)])
    if len(hash) < n:
        imgs = e.elements.filter(ctype='IMG').filter(hash=None)
        for i in imgs:
            if not i.thumb:
                i.thumb = str(i.entity.id).lower() + str(i.id) + '.thumbnail'
            path = os.path.join(settings.THUMB_ROOT, i.thumb)
            if not os.path.exists(path):
                urlretrieve(i.embed, path)
                try:
                    t = Image.open(path)
                    i.hash = str(imagehash.average_hash(t))
                except IOError:
                    os.remove(path)
                    continue
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

def convert_li(li_field):
    '''
    Removes '<li>' tags from a string.
    '''
    return ''.join(li_field.split('<li>')).replace('</li>', ' ').strip()

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def paragraph_split(block):
    '''
    Splits a block of text into multiple paragraphs.
    '''
    tokenizer = nltk.data.load('file:' + os.path.join(settings.BASE_DIR, 'nltk_data/tokenizers/punkt/english.pickle'))
    groups = [filter(lambda x: len(x), g) for g in grouper(tokenizer.tokenize(block), 3, '')]

    if len(groups) > 1 and len(groups[-1]) < 2:
        groups[-2] += groups[-1]
        groups.pop()
    return [' '.join(g) for g in groups]

def is_stub(e):
    if hasattr(e, 'crisis'):
        return len(e.summary.split() + e.eimpact.split() + e.himpact.split() + e.resources.split() + e.help.split()) < 100
    if hasattr(e, 'organization'):
        return len(e.summary.split() + e.contact.split() + e.history.split()) < 100 

def common(e):
    return {
        'stub': is_stub(e),
        'name': e.name,
        'summary': paragraph_split(e.summary),
        'citations' : [{'href': w.href, 'text': w.text} for w in e.elements.filter(ctype='CITE')],
        'feeds' : [{'id': str(w.embed).split('/')[-1]} for w in e.elements.filter(ctype='FEED')],
        'maps' : [{'embed': w.embed, 'text': w.text} for w in e.elements.filter(ctype='MAP')[:1]],
        'images' : generate_thumbs(e),
        'videos' : [{'embed': w.embed, 'text': w.text} for w in list(e.elements.filter(ctype='VID'))[:1]],
        'additional': {'images': len(e.elements.filter(ctype='IMG')) > 3, 'videos': len(e.elements.filter(ctype='VID')) > 1},
        'external': [{'href': w.href, 'text': w.text} for w in e.elements.filter(ctype='LINK')],
    }

def people(request, id):
    p = Person.objects.get(id='PER_' + str(id).upper())
    attr = {
        'p': p,
        'related_crises' : [{'id': str(c.id).lower()[4:], 'name': c.name} for c in p.crises.all()],
        'related_orgs' : [{'id': str(o.id).lower()[4:], 'name': o.name} for o in p.organizations.all()],
    }
    attr.update(common(p))
    return render(request, 'person.html', attr)

def organizations(request, id):
    o = Organization.objects.get(id='ORG_' + str(id).upper())
    attr = {
        'o': o,
        'related_crises' : [{'id': str(c.id).lower()[4:], 'name': c.name} for c in o.crises.all()],
        'related_people' : [{'id': str(p.id).lower()[4:], 'name': p.name} for p in o.people.all()],
        'contact' : [{'href': li.attrib.get('href'), 'text': li.text} for li in fromstring('<ContactInfo>' + o.contact + '</ContactInfo>')],
        'history': paragraph_split(convert_li(o.history)),
    }
    attr.update(common(o))
    return render(request, 'organization.html', attr)

def crises(request, id):
    c = Crisis.objects.get(id='CRI_' + str(id).upper())
    attr = {
        'c': c,
        'related_people' : [{'id': str(p.id).lower()[4:], 'name': p.name} for p in c.people.all()],
        'related_orgs' : [{'id': str(o.id).lower()[4:], 'name': o.name} for o in c.organizations.all()],
        'eimpact': paragraph_split(convert_li(c.eimpact)),
        'resources': paragraph_split(convert_li(c.resources)),
        'help' : [{'href': li.attrib.get('href'), 'text': li.text} for li in fromstring('<WaysToHelp>' + c.help + '</WaysToHelp>')],
    }
    attr.update(common(c))
    return render(request, 'crisis.html', attr)
