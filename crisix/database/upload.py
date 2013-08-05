from models import *

import datetime, os, glob
from datetime import time
from django.conf import settings
from xml.etree.ElementTree import tostring
from minixsv import pyxsval

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
            c.kind = attr.text
        if attr.tag == 'Date':
            c.date = attr.text
        if attr.tag == 'Time':
            c.time = attr.text
        if attr.tag == 'Locations':
            c.location += ''.join([v for v in [tostring(li).strip() for li in attr] if v not in c.location])
        if attr.tag == 'HumanImpact':
            c.himpact += ''.join([v for v in [tostring(li).strip() for li in attr] if v not in c.himpact])
        if attr.tag == 'EconomicImpact':
            c.eimpact += ''.join([v for v in [tostring(li).strip() for li in attr] if v not in c.eimpact])
        if attr.tag == 'ResourcesNeeded':
            c.resources += ''.join([v for v in [tostring(li).strip() for li in attr] if v not in c.resources])
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
            o.kind = attr.text
        if attr.tag == 'Location':
            o.location = attr.text
        if attr.tag == 'History':
            o.history += ''.join([v for v in [tostring(li).strip() for li in attr] if v not in o.history])
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
            p.kind = attr.text
        if attr.tag == 'Location':
            p.location = attr.text
        if attr.tag == 'Common':
            com_handler(attr, p)
    assert p is not None
    p.save()

def insert_elem(query, attr):
    assert type(query) is dict
    assert type(attr) is dict
    try:
        WebElement.objects.get(**query)
    except WebElement.DoesNotExist:
        attr.update(query)
        w = WebElement(**attr)
        w.save()

def valid_link(embed):
    link = embed.lstrip('htps:')
    if 'youtube' in link or 'vimeo' in link:
        return link

def valid_map(embed):
    if ('output' in embed or 'source' in embed) and 'embed' in embed:
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
            e.summary = attr.text
