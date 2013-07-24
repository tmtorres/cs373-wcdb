from models import *
from django.http import HttpResponse

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, fromstring
from xml.etree.ElementTree import ElementTree
from xml.dom import minidom

def getCrises(root):
    assert root is not None
    for c in Crisis.objects.all():
        node = ET.SubElement(root, 'Crisis')
        node.set('ID', c.id)
        node.set('Name', c.name)

        attr = ET.SubElement(node, 'People')
        for p in c.people.all():
            ET.SubElement(attr, 'Person').set('ID', p.id)

        attr = ET.SubElement(node, 'Organizations')
        for o in c.organizations.all():
            ET.SubElement(attr, 'Org').set('ID', o.id)

        if c.kind is not None:
            ET.SubElement(node, 'Kind').text = c.kind
        if c.date is not None:
            ET.SubElement(node, 'Date').text = str(c.date)
        if c.time is not None:
            ET.SubElement(node, 'Time').text = str(c.time)
        if len(c.location) > 0:
            node.append(fromstring('<Locations>' + c.location + '</Locations>'))
        if len(c.himpact) > 0:
            node.append(fromstring('<HumanImpact>' + c.himpact + '</HumanImpact>'))
        if len(c.eimpact) > 0:
            node.append(fromstring('<EconomicImpact>' + c.eimpact + '</EconomicImpact>'))
        if len(c.resources) > 0:
            node.append(fromstring('<ResourcesNeeded>' + c.resources + '</ResourcesNeeded>'))
        if len(c.help) > 0:
            node.append(fromstring('<WaysToHelp>' + c.help + '</WaysToHelp>'))
        getCommon(node, c)

def getOrganizations(root):
    assert root is not None
    for o in Organization.objects.all():
        node = ET.SubElement(root, 'Organization')
        node.set('ID', o.id)
        node.set('Name', o.name)

        attr = ET.SubElement(node, 'Crises')
        for c in o.crises.all():
            ET.SubElement(attr, 'Crisis').set('ID', c.id)

        attr = ET.SubElement(node, 'People')
        for p in o.people.all():
            ET.SubElement(attr, 'Person').set('ID', p.id)

        if o.kind is not None:
            ET.SubElement(node, 'Kind').text = o.kind
        if len(o.location) > 0:
            ET.SubElement(node, 'Location').text = o.location
        if len(o.history) > 0:
            node.append(fromstring('<History>' + o.history + '</History>'))
        if len(o.contact) > 0:
            node.append(fromstring('<ContactInfo>' + o.contact + '</ContactInfo>'))
        getCommon(node, o)

def getPeople(root):
    assert root is not None
    for p in Person.objects.all():
        node = ET.SubElement(root, 'Person')
        node.set('ID', p.id)
        node.set('Name', p.name)
        
        attr = ET.SubElement(node, 'Crises')
        for c in p.crises.all():
            ET.SubElement(attr, 'Crisis').set('ID', c.id)

        attr = ET.SubElement(node, 'Organizations')
        for o in p.organizations.all():
            ET.SubElement(attr, 'Org').set('ID', o.id)

        if p.kind is not None:
            ET.SubElement(node, 'Kind').text = p.kind
        if len(p.location) > 0:
            ET.SubElement(node, 'Location').text = p.location
        getCommon(node, p)

def getCommon(node, entity):
    assert node is not None
    assert entity is not None
    attr = ET.SubElement(node, 'Common')
    w = entity.elements.filter(ctype='CITE')
    if len(w) > 0:
        elem = ET.SubElement(attr, 'Citations')
        for v in w:
            child = ET.SubElement(elem, 'li')
            child.set('href', v.href)
            child.text = v.text

    w = entity.elements.filter(ctype='LINK')
    if len(w) > 0:
        elem = ET.SubElement(attr, 'ExternalLinks')
        for v in w:
            child = ET.SubElement(elem, 'li')
            child.set('href', v.href)
            child.text = v.text

    w = entity.elements.filter(ctype='IMG')
    if len(w) > 0:
        elem = ET.SubElement(attr, 'Images')
        for v in w:
            child = ET.SubElement(elem, 'li')
            child.set('embed', v.embed)
            child.text = v.text

    w = entity.elements.filter(ctype='VID')
    if len(w) > 0:
        elem = ET.SubElement(attr, 'Videos')
        for v in w:
            child = ET.SubElement(elem, 'li')
            child.set('embed', v.embed)
            child.text = v.text

    w = entity.elements.filter(ctype='MAP')
    if len(w) > 0:
        elem = ET.SubElement(attr, 'Maps')
        for v in w:
            child = ET.SubElement(elem, 'li')
            child.set('embed', v.embed)
            child.text = v.text

    w = entity.elements.filter(ctype='FEED')
    if len(w) > 0:
        elem = ET.SubElement(attr, 'Feeds')
        for v in w:
            child = ET.SubElement(elem, 'li')
            child.set('embed', v.embed)
            child.text = v.text

    if len(list(attr)) == 0:
        node.remove(attr)
