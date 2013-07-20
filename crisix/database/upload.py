from models import *

import datetime
from datetime import time
from xml.etree.ElementTree import tostring

def insert(root):
    for elem in root:
        if elem.tag == 'Crisis':
            criHandler(elem)
        elif elem.tag == 'Organization':
            orgHandler(elem)
        elif elem.tag == 'Person':
            perHandler(elem)

def getEntity(etype, eid):
    e = None
    try:
        e = etype.objects.get(id=eid)
    except etype.DoesNotExist:
        e = etype(id=eid)
    e.save()
    assert e is not None
    return e

def criHandler(node):
    c = getEntity(Crisis, node.attrib.get('ID'))
    c.name = node.attrib.get('Name')
    for attr in node:
        if attr.tag == 'Organizations':
            for elem in attr:
                c.organizations.add(getEntity(Organization, elem.attrib.get('ID')))
        if attr.tag == 'People':
            for elem in attr:
                c.people.add(getEntity(Person, elem.attrib.get('ID')))
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
            comHandler(attr, c)
    c.save()

def orgHandler(node):
    o = getEntity(Organization, node.attrib.get('ID'))
    o.name = node.attrib.get('Name')
    for attr in node:
        if attr.tag == 'Crises':
            for elem in attr:
                o.crises.add(getEntity(Crisis, elem.attrib.get('ID')))
        if attr.tag == 'People':
            for elem in attr:
                o.people.add(getEntity(Person, elem.attrib.get('ID')))
        if attr.tag == 'Kind':
            o.kind = attr.text
        if attr.tag == 'Location':
            o.location = attr.text
        if attr.tag == 'History':
            o.history += ''.join([v for v in [tostring(li).strip() for li in attr] if v not in o.history])
        if attr.tag == 'ContactInfo':
            o.contact += ''.join([v for v in [tostring(li).strip() for li in attr] if v not in o.contact])
        if attr.tag == 'Common':
            comHandler(attr, o)
    o.save()

def perHandler(node):
    p = getEntity(Person, node.attrib.get('ID'))
    p.name = node.attrib.get('Name')
    for attr in node:
        if attr.tag == 'Crises':
            for elem in attr:
                p.crises.add(getEntity(Crisis, elem.attrib.get('ID')))
        if attr.tag == 'Organizations':
            for elem in attr:
                p.organizations.add(getEntity(Organization, elem.attrib.get('ID')))
        if attr.tag == 'Kind' and p.kind is None:
            p.kind = attr.text
        if attr.tag == 'Location' and p.location is None:
            p.location = attr.text
        if attr.tag == 'Common':
            comHandler(attr, p)
    p.save()

def insertElem(query, attr):
    try:
        WebElement.objects.get(**query)
    except WebElement.DoesNotExist:
        attr.update(query)
        w = WebElement(**attr)
        w.save()

def comHandler(node, e):
    for attr in node:
        if attr.tag == 'Citations':
            for elem in attr:
                insertElem({'href' : elem.attrib.get('href')}, {'entity' : e, 'ctype' : 'CITE', 'text' : elem.text})
        if attr.tag == 'ExternalLinks':
            for elem in attr:
                insertElem({'href' : elem.attrib.get('href')}, {'entity' : e, 'ctype' : 'LINK', 'text' : elem.text})
        if attr.tag == 'Images':
            for elem in attr:
                insertElem({'embed' : elem.attrib.get('embed')}, {'entity' : e, 'ctype' : 'IMG', 'text' : elem.text})
        if attr.tag == 'Videos':
            for elem in attr:
                if 'youtube' in elem.embed:
                    insertElem({'embed' : elem.attrib.get('embed')}, {'entity' : e, 'ctype' : 'VID', 'text' : elem.text})
        if attr.tag == 'Maps':
            for elem in attr:
                if 'google' in elem.embed:
                    insertElem({'embed' : elem.attrib.get('embed')}, {'entity' : e, 'ctype' : 'MAP', 'text' : elem.text})
        if attr.tag == 'Feeds':
            for elem in attr:
                insertElem({'embed' : elem.attrib.get('embed')}, {'entity' : e, 'ctype' : 'FEED', 'text' : elem.text})
        if attr.tag == 'Summary':
            e.summary = attr.text
