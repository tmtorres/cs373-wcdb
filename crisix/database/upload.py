from models import *

import datetime, os, glob
from datetime import time
from django.conf import settings
from xml.etree.ElementTree import tostring, fromstring
from minixsv import pyxsval
from crisix.views import convert_li
from substr import str_match
from subseq import seq_match
import urlparse

def validate(file):
    elementTreeWrapper = pyxsval.parseAndValidateXmlInput(file, xsdFile=os.path.join(settings.BASE_DIR, 'WCDB2.xsd.xml'),
                         xmlIfClass=pyxsval.XMLIF_ELEMENTTREE)
    elemTree = elementTreeWrapper.getTree()
    return elemTree.getroot()

def insert(root):
    assert root is not None
    for elem in root:
        if elem.tag == 'Crisis':
            cri_handler(elem)
        elif elem.tag == 'Organization':
            org_handler(elem)
        elif elem.tag == 'Person':
            per_handler(elem)

def clear():
    for t in glob.glob(os.path.join(settings.THUMB_ROOT, '*.thumbnail')):
        os.remove(t)
    for e in Entity.objects.all():
        e.delete()

def get_entity(etype, eid):
    assert etype in (Crisis, Organization, Person)
    assert eid[:3] in ('CRI', 'ORG', 'PER')
    e = None
    try:
        e = etype.objects.get(id=eid)
    except etype.DoesNotExist:
        e = etype(id=eid)
    e.save()
    assert e is not None
    return e

def subelements(attr):
    return ''.join([tostring(li).strip() for li in attr])

def cri_handler(node):
    assert node is not None
    c = get_entity(Crisis, node.attrib.get('ID'))
    c.name = node.attrib.get('Name')
    for attr in node:
        if attr.tag == 'Organizations':
            for elem in attr:
                c.organizations.add(get_entity(Organization, elem.attrib.get('ID')))
        if attr.tag == 'People':
            for elem in attr:
                c.people.add(get_entity(Person, elem.attrib.get('ID')))
        if attr.tag == 'Kind':
            c.kind = attr.text.title() if attr.text is not None else c.kind
        if attr.tag == 'Date':
            c.date = attr.text if attr.text is not None else c.date
        if attr.tag == 'Time':
            c.time = attr.text if attr.text is not None else c.time
        if attr.tag == 'Locations':
            old = fromstring('<Locations>' + c.location + '</Locations>')
            c.location = ''.join([v for v in [('<li>' + li.text.strip().title() + '</li>') for li in str_match(attr, old)]])
        if attr.tag == 'HumanImpact':
            c.himpact = '<li>' + seq_match(convert_li(c.himpact), convert_li(subelements(attr))).strip() + '</li>'
        if attr.tag == 'EconomicImpact':
            c.eimpact = '<li>' + seq_match(convert_li(c.eimpact), convert_li(subelements(attr))).strip() + '</li>'
        if attr.tag == 'ResourcesNeeded':
            c.resources = '<li>' + seq_match(convert_li(c.resources), convert_li(subelements(attr))).strip() + '</li>'
        if attr.tag == 'WaysToHelp':
            c.help += ''.join([v for v in [tostring(li).strip() for li in attr] if v not in c.help])
        if attr.tag == 'Common':
            com_handler(attr, c)
    assert c is not None
    c.save()

def org_handler(node):
    assert node is not None
    o = get_entity(Organization, node.attrib.get('ID'))
    o.name = node.attrib.get('Name')
    for attr in node:
        if attr.tag == 'Crises':
            for elem in attr:
                o.crises.add(get_entity(Crisis, elem.attrib.get('ID')))
        if attr.tag == 'People':
            for elem in attr:
                o.people.add(get_entity(Person, elem.attrib.get('ID')))
        if attr.tag == 'Kind':
            o.kind = attr.text.title() if attr.text is not None else o.kind
        if attr.tag == 'Location':
            o.location = attr.text.title() if attr.text is not None else o.location
        if attr.tag == 'History':
            o.history = '<li>' + seq_match(convert_li(o.history), convert_li(subelements(attr))).strip() + '</li>'
        if attr.tag == 'ContactInfo':
            o.contact += ''.join([v for v in [tostring(li).strip() for li in attr] if v not in o.contact])
        if attr.tag == 'Common':
            com_handler(attr, o)
    assert o is not None
    o.save()

def per_handler(node):
    assert node is not None
    p = get_entity(Person, node.attrib.get('ID'))
    p.name = node.attrib.get('Name')
    for attr in node:
        if attr.tag == 'Crises':
            for elem in attr:
                p.crises.add(get_entity(Crisis, elem.attrib.get('ID')))
        if attr.tag == 'Organizations':
            for elem in attr:
                p.organizations.add(get_entity(Organization, elem.attrib.get('ID')))
        if attr.tag == 'Kind':
            p.kind = attr.text.title() if attr.text is not None else p.kind
        if attr.tag == 'Location':
            p.location = attr.text.title()
        if attr.tag == 'Common':
            com_handler(attr, p)
    assert p is not None
    p.save()

def insert_elem(query, attr):
    assert type(query) is dict
    assert type(attr) is dict
    try:
        w = attr['entity'].elements.get(**query)
    except WebElement.DoesNotExist:
        attr.update(query)
        w = WebElement(**attr)
        w.save()

def extract_ytid(link):
    return urlparse.parse_qs(urlparse.urlparse(link).query)["v"][0]

def valid_link(link):
    if 'youtube' in link:
        return link if 'embed' in link else ('//www.youtube.com/embed/' + extract_ytid(link) if '?v=' in link else None)
    elif 'vimeo' in link:
        if 'player' not in link:
            return 'http://player.vimeo.com/video/' + link.split('/')[-1]
        return link

def valid_map(embed):
    if 'maps.google.com' in embed:
        return embed + ('&output=embed' if 'embed' not in embed else '')
    elif 'bing.com/maps/embed/' in embed:
        return embed

def com_handler(node, e):
    assert node is not None
    assert e is not None
    for attr in node:
        if attr.tag == 'Citations':
            for elem in attr:
                insert_elem({'href' : elem.attrib.get('href')}, {'entity' : e, 'ctype' : 'CITE', 'text' : elem.text})
        if attr.tag == 'ExternalLinks':
            for elem in attr:
                insert_elem({'href' : elem.attrib.get('href')}, {'entity' : e, 'ctype' : 'LINK', 'text' : elem.text})
        if attr.tag == 'Images':
            for elem in attr:
                if str(elem.attrib.get('embed')).split('.')[-1].upper() in ('JPG', 'JPEG', 'PNG', 'GIF'):
                    insert_elem({'embed' : elem.attrib.get('embed')}, {'entity' : e, 'ctype' : 'IMG', 'text' : elem.text})
        if attr.tag == 'Videos':
            for elem in attr:
                embed = valid_link(elem.attrib.get('embed'))
                if embed is not None:
                    insert_elem({'embed' : embed}, {'entity' : e, 'ctype' : 'VID', 'text' : elem.text})
        if attr.tag == 'Maps':
            for elem in attr:
                embed = valid_map(elem.attrib.get('embed'))
                if embed is not None:
                    insert_elem({'embed' : embed}, {'entity' : e, 'ctype' : 'MAP', 'text' : elem.text}) 
        if attr.tag == 'Feeds':
            for elem in attr:
                insert_elem({'embed' : elem.attrib.get('embed')}, {'entity' : e, 'ctype' : 'FEED', 'text' : elem.text})
        if attr.tag == 'Summary':
            e.summary = attr.text if attr.text is not None and len(attr.text) > len(e.summary) else e.summary
