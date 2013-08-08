"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os, sys
from django.test import TestCase
from django.test.client import RequestFactory

from models import *
from upload import *
from download import *
from views import *
from datetime import datetime
from crisix.views import people, organizations, crises, display, display_more, get_datetime, get_contact, convert_li, is_stub

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, fromstring
from xml.etree.ElementTree import ElementTree

class SimpleTest(TestCase, RequestFactory):
    fixtures = ['crisix_fixture.json']

    def setUp(self):
        self.c = Crisis(id='CRI_HAIEAR',name='2010 Haiti Earthquake',kind='Natural Disaster',location='Haiti',created=datetime.now(),summary='Haitian Earthquake')
        self.c.save()
        self.p = Person(id='PER_BROBMA',name='Barack Obama',kind='President',location='Washington, D.C., USA',created=datetime.now(),summary="President of the USA")
        self.p.save()
        self.o = Organization(id='ORG_WHORGN',name='World Health Organization',kind='Public Health',location='Geneva, Switzerland',created=datetime.now(),summary='UN WHO')
        self.o.save()
        self.c.organizations.add(self.o)
        self.c.people.add(self.p)
        self.o.crises.add(self.c)
        self.o.people.add(self.p)

	# ------------
	# Simple Tests
	# ------------

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_index(self):
        # Test if page can be accessed properly
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)

        # Test if database is properly populated
        self.assertEqual(self.p.name,'Barack Obama')
    
    def test_datetime_1(self):
	# Test if date and time match for given crisis
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSHESSG.xml')).read())
        insert(root)
	a = Crisis.objects.get(id='CRI_SHESSG')
	res = get_datetime(a)
	self.assertEqual(res, '2012-12-14, 09:35:00')
    
    def test_datetime_2(self):
	# Test if date and time match for given crisis
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestLYCLWR.xml')).read())
        insert(root)
	a = Crisis.objects.get(id='CRI_LYCLWR')
	res = get_datetime(a)
	self.assertEqual(res, '2011-02-15')

    def test_datetime_3(self):
	# Test if date and time are applicable to a non-crisis
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
        insert(root)
	a = Person.objects.get(id='PER_BROBMA')
	res = get_datetime(a)
	self.assertEqual(res, '')

    def test_contact_1(self):
	# Test if contact info is applicable to non-organization
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
        insert(root)
	a = Person.objects.get(id='PER_BROBMA')
	res = get_contact(a)
	self.assertEqual(res, '')

    def test_contact_2(self):
	# Test if contact info matches for given organization
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestUNDWAY.xml')).read())
        insert(root)
	a = Organization.objects.get(id='ORG_UNDWAY')
	res = get_contact(a)
	self.assertEqual(res, 'http://apps.unitedway.org/contact/')

    def test_contact_3(self):
	# Test if contact info matches for given organization
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSNQKRF.xml')).read())
        insert(root)
	a = Organization.objects.get(id='ORG_SNQKRF')
	res = get_contact(a)
	self.assertEqual(res, 'http://sichuan-quake-relief.org/contact-us/')

    def test_display_1(self):
        # Test if person name is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/people')
        response = display(request, 'people')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('President'),-1)   
        
    def test_display_2(self):
        # Test if person name is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/organizations')
        response = display(request, 'organizations')
        htmlstring = response.content   
        self.assertNotEqual(htmlstring.find('Public Health'),-1) 
       
    def test_display_3(self):
        # Test if person name is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crises')
        response = display(request, 'crises')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('Natural Disaster'),-1) 
        
    def test_display_more_1(self):
        # Test if person name is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/people/brobma/videos')
        response = display_more(request, 'people', 'brobma', 'videos')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('Barack Obama'),-1)
    
    def test_display_more_2(self):
        # Test if organization name is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/organizations/whorgn/videos')
        response = display_more(request, 'organizations', 'whorgn', 'videos')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('World Health Organization'),-1)
        
    def test_display_more_3(self):
        # Test if crisis name is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crises/haiear/videos')
        response = display_more(request, 'crises', 'haiear', 'videos')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('Haiti Earthquake'),-1)

    def test_convertli_1(self):
	text = "<li>World Health Organization</li>"
	res = convert_li(text)
	self.assertEqual(res, 'World Health Organization')

    def test_convertli_2(self):
	text = "<li>Barack Obama</li><li>Adam Lanza</li>"
	res = convert_li(text)
	self.assertEqual(res, 'Barack Obama Adam Lanza')

    def test_convertli_3(self):
	text = "<li>This is a sentence. Remove all li tags.</li>"
	res = convert_li(text)
	self.assertEqual(res, 'This is a sentence. Remove all li tags.')

    def test_stub_1(self):
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
        insert(root)
	a = Person.objects.get(id='PER_BROBMA')
	res = is_stub(a)
	self.assertFalse(res)

    def test_stub_2(self):
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSHESSG.xml')).read())
        insert(root)
	a = Crisis.objects.get(id='CRI_SHESSG')
	res = is_stub(a)
	self.assertFalse(res)

    def test_stub_3(self):
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestNLTLCL.xml')).read())
        insert(root)
	a = Organization.objects.get(id='ORG_NLTLCL')
	res = is_stub(a)
	self.assertFalse(res)

    def test_search_1(self):
	# Test functionality of search function in returning correct information
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
	insert(root)
	request_factory = RequestFactory()
	request = request_factory.get('/search')
	response = search(request)
	htmlstring = response.content
	self.assertNotEqual(htmlstring.find('Barack Obama'), -1)

    def test_search_2(self):
	# Test functionality of search function in returning correct information
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSHESSG.xml')).read())
	insert(root)
	request_factory = RequestFactory()
	request = request_factory.get('/search')
	response = search(request)
	htmlstring = response.content
	self.assertNotEqual(htmlstring.find('Sandy Hook'), -1)

    def test_search_3(self):
	# Test functionality of search function in returning correct information
	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestNLTLCL.xml')).read())
	insert(root)
	request_factory = RequestFactory()
	request = request_factory.get('/search')
	response = search(request)
	htmlstring = response.content
	self.assertNotEqual(htmlstring.find('National Transitional Council'), -1)
	
    def test_query_1(self):
	# Test if the given string exists inside the query 
	request_factory = RequestFactory()
	request = request_factory.get('/query/?q=1')
	response = query(request)
	htmlstring = response.content
	self.assertNotEqual(htmlstring.find('Magic Johnson'), -1)

    def test_query_2(self):
	# Test if the given string exists inside the query 
	request_factory = RequestFactory()
	request = request_factory.get('/query/?q=4')
	response = query(request)
	htmlstring = response.content
	self.assertNotEqual(htmlstring.find('Naoto Kan'), -1)

    def test_query_3(self):
	# Test if the given string exists inside the query 
	request_factory = RequestFactory()
	request = request_factory.get('/query/?q=7')
	response = query(request)
	htmlstring = response.content
	self.assertNotEqual(htmlstring.find('Sandy Hook Elementary School Shooting'), -1)
   
    # -----------
    # People View
    # -----------
    
    def test_people1(self):
        # Test if the instance page is accessible
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/people/brobma')
    	response = people(request, 'brobma')
    	self.assertEqual(response.status_code, 200)

    def test_people2(self):
        # Test if person kind is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/people/brobma')
        response = people(request, 'brobma')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<li>President</li>'),-1)

    def test_people3(self):
        # Test if person name is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/people/brobma')
        response = people(request, 'brobma')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<h1 class="main-focus;">Barack Obama</h1>'),-1)

    def test_people4(self):
        # Test if related objects are on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/people/brobma')
        response = people(request, 'brobma')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<li><a href="/crises/haiear/">2010 Haiti Earthquake</a></li>'),-1)
        self.assertNotEqual(htmlstring.find('<li><a href="/organizations/whorgn/">World Health Organization</a></li>'),-1)

    # -----------------
    # Organization View
    # -----------------

    def test_organization1(self):
        # Test if the instance page is accessible
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/organization/whorgn')
        response = organizations(request, 'whorgn')
        self.assertEqual(response.status_code, 200)

    def test_organization2(self):
        # Test if person kind is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/organization/whorgn')
        response = organizations(request, 'whorgn')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<li>Public Health</li>'),-1)

    def test_organization3(self):
        # Test if person name is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/organization/whorgn')
        response = organizations(request, 'whorgn')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<h1 class="main-focus;">World Health Organization</h1>'),-1)

    def test_organization4(self):
        # Test if related objects are on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/organization/whorgn')
        response = organizations(request, 'whorgn')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<li><a href="/crises/haiear/">2010 Haiti Earthquake</a></li>'),-1)
        self.assertNotEqual(htmlstring.find('<li><a href="/people/brobma/">Barack Obama</a></li>'),-1)

    # -----------
    # Crisis View
    # -----------

    def test_crisis1(self):
        # Test if the instance page is accessible
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/crises/haiear')
        response = crises(request, 'haiear')
        self.assertEqual(response.status_code, 200)

    def test_crisis2(self):
        # Test if crisis kind is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/crises/haiear')
        response = crises(request, 'haiear')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<li>Natural Disaster</li>'),-1)

    def test_crisis3(self):
        # Test if crisis name is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/crises/haiear')
        response = crises(request, 'haiear')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<h1 class="main-focus;">2010 Haiti Earthquake</h1>'),-1)

    def test_crisis4(self):
        # Test if related objects are on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crises/haiear')
        response = crises(request, 'haiear')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<li><a href="/organizations/whorgn/">World Health Organization</a></li>'),-1)
        self.assertNotEqual(htmlstring.find('<li><a href="/people/brobma/">Barack Obama</a></li>'),-1)

class TestUpload(TestCase):
    def test_insert_1(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSHESSG.xml')).read())
        insert(root)
        c = None

        try:
            c = Crisis.objects.get(id='CRI_SHESSG')
        except Crisis.DoesNotExist:
            self.assertTrue(False)
        self.assertTrue(c is not None)
        self.assertEqual(str(c.kind), 'Spree Shooting')
        self.assertEqual(str(c.date), '2012-12-14')
        self.assertEqual(str(c.time), '09:35:00')
        self.assertEqual(str(c.location), '<li>Newtown, Connecticut</li>')
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_insert_2(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
        insert(root)
        p = None
     
        try:
            p = Person.objects.get(id='PER_BROBMA')
        except Person.DoesNotExist:
    	    self.assertTrue(False)
        self.assertEqual(str(p.kind), 'President')
        self.assertEqual(str(p.location), 'Washington, D.C, United States Of America')
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_insert_3(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestUNDWAY.xml')).read())
        insert(root)
        o = None
        
        try:
            o = Organization.objects.get(id='ORG_UNDWAY')
        except Organization.DoesNotExist:
    	    self.assertTrue(False)
        self.assertEqual(str(o.kind), 'Non-Profit Organization')
        self.assertEqual(str(o.location), 'Worldwide')
        # self.assertTrue('<li>In 1887, a Denver woman, a priest, two ministers' in o.history)
        self.assertEqual(str(o.contact), '<li href="http://apps.unitedway.org/contact/">Contact Form</li>')
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_get_entity_1(self): 
    	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSHESSG.xml')).read())
    	insert(root)
    	
        a = get_entity(Crisis, 'CRI_SHESSG')
        self.assertEqual(str(a.kind), 'Spree Shooting')
        self.assertEqual(str(a.date), '2012-12-14')
        self.assertEqual(str(a.time), '09:35:00')
        self.assertEqual(str(a.location), '<li>Newtown, Connecticut</li>')
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_get_entity_2(self):
    	root2 = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
    	insert(root2)
    	
    	b = get_entity(Person, 'PER_BROBMA')
    	self.assertEqual(str(b.kind), 'President')
    	self.assertEqual(str(b.location), 'Washington, D.C, United States Of America')
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_get_entity_3(self):
    	root3 = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestUNDWAY.xml')).read())
    	insert(root3)
    	
    	c = get_entity(Organization, 'ORG_UNDWAY')   	
        self.assertEqual(str(c.kind), 'Non-Profit Organization')
        self.assertEqual(str(c.location), 'Worldwide')
        self.assertEqual(str(c.contact), '<li href="http://apps.unitedway.org/contact/">Contact Form</li>')
     	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_cri_handler_1(self):
    	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSHESSG.xml')).read())
    	    
    	cri_handler(root[0]) 
    	c = Crisis.objects.get(id='CRI_SHESSG')
    	self.assertEqual(str(c.kind), 'Spree Shooting')
        self.assertEqual(str(c.date), '2012-12-14')
        self.assertEqual(str(c.time), '09:35:00')
        self.assertEqual(str(c.location), '<li>Newtown, Connecticut</li>')
     	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_cri_handler_2(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSCHERQ.xml')).read())
        
        cri_handler(root[0])
        c = Crisis.objects.get(id='CRI_SCHERQ')
        self.assertEqual(str(c.kind), 'Earthquake')
        self.assertEqual(str(c.date), '2008-05-12')
        self.assertEqual(str(c.time), '14:28:01')
        self.assertEqual(str(c.location), '<li>Wenchuan County, Sichuan</li><li>Sichuan Province</li>')
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_cri_handler_3(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestLYCLWR.xml')).read())
        
        cri_handler(root[0])
        c = Crisis.objects.get(id='CRI_LYCLWR')
        self.assertEqual(str(c.kind), 'Civil War')
        self.assertEqual(str(c.date), '2011-02-15')
        self.assertEqual(str(c.location), '<li>Libya</li>')
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_org_handler_1(self):
        root =fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestUNDWAY.xml')).read())
        
        org_handler(root[0])
        o = Organization.objects.get(id='ORG_UNDWAY')
        self.assertEqual(str(o.kind), 'Non-Profit Organization')
        self.assertEqual(str(o.location), 'Worldwide')
        self.assertEqual(str(o.contact), '<li href="http://apps.unitedway.org/contact/">Contact Form</li>')
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_org_handler_2(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSNQKRF.xml')).read())
        
        org_handler(root[0])
        o = Organization.objects.get(id='ORG_SNQKRF')
        self.assertEqual(str(o.kind), 'Non-Profit, Humanitarian Organization')
        self.assertEqual(str(o.location), 'Chengdu, China')
        self.assertTrue('<li>Volunteer: volunteer@sichuan-quake-relief.org</li>' in str(o.contact)) 
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_org_handler_3(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestNLTLCL.xml')).read())
        
        org_handler(root[0])
        o = Organization.objects.get(id='ORG_NLTLCL')
        self.assertEqual(str(o.kind), 'De Facto Government')
        self.assertEqual(str(o.location), 'Benghazi, Libya')
        self.assertEqual(str(o.contact), '<li> Organization is no longer active. </li>')
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_per_handler_1(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
        
        per_handler(root[0])
        p = Person.objects.get(id='PER_BROBMA')
        self.assertEqual(str(p.kind), 'President')
        self.assertEqual(str(p.location), 'Washington, D.C, United States Of America')
    	for c in Crisis.objects.all():
    		c.delete()

    def test_per_handler_2(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestADMLNZ.xml')).read())
        
        per_handler(root[0])
        p = Person.objects.get(id='PER_ADMLNZ')
        self.assertEqual(str(p.kind), 'Murderer')
        self.assertEqual(str(p.location), 'Newtown, Connecticut')
    	for c in Crisis.objects.all():
    		c.delete()
    		
    def test_per_handler_3(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestHUJNTO.xml')).read())
        
        per_handler(root[0])
        p = Person.objects.get(id='PER_HUJNTO')
        self.assertEqual(str(p.kind), 'President')
        self.assertEqual(str(p.location), 'Communist Party Of China')
    	for c in Crisis.objects.all():
    		c.delete()

    def test_insert_elem_1(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
        per_handler(root[0])
        p = Person.objects.get(id='PER_BROBMA')

        # Test is proper amount of Videos are in DB
        element = p.elements.filter(ctype='VID')
        self.assertEqual(len(element), 2)
        # Test is insertion works without prior functions
        insert_elem({'href':'www.youtube.com/videos'}, {'entity':p, 'ctype':'VID', 'text': 'Test Youtube Video'})
        element = str(p.elements.filter(ctype='VID'))
        self.assertNotEqual(element.find('www.youtube.com/videos'), -1)
        element = p.elements.filter(ctype='VID')
        self.assertEqual(len(element), 3)
        element = p.elements.filter(ctype='CITE')
        self.assertEqual(len(element), 2)
    	for c in Crisis.objects.all():
    		c.delete()

    def test_insert_elem_2(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSHESSG.xml')).read())
        cri_handler(root[0])
        c = Crisis.objects.get(id='CRI_SHESSG')

        # Test is proper amount of Videos are in DB
        element = c.elements.filter(ctype='VID')
        self.assertEqual(len(element), 1)
        # Test is insertion works without prior functions
        insert_elem({'href':'www.youtube.com/videos'}, {'entity':c, 'ctype':'VID', 'text': 'Test Youtube Video'})
        element = str(c.elements.filter(ctype='VID'))
        self.assertNotEqual(element.find('www.youtube.com/videos'), -1)
        element = c.elements.filter(ctype='VID')
        self.assertEqual(len(element), 2)
        element = c.elements.filter(ctype='CITE')
        self.assertEqual(len(element), 3)
    	for c in Crisis.objects.all():
    		c.delete()

    def test_insert_elem_3(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestUNDWAY.xml')).read())
        org_handler(root[0])
        o = Organization.objects.get(id='ORG_UNDWAY')

        # Test is proper amount of Videos are in DB
        element = o.elements.filter(ctype='VID')
        self.assertEqual(len(element), 1)
        # Test is insertion works without prior functions
        insert_elem({'href':'www.youtube.com/videos'}, {'entity':o, 'ctype':'VID', 'text': 'Test Youtube Video'})
        element = str(o.elements.filter(ctype='VID'))
        self.assertNotEqual(element.find('www.youtube.com/videos'), -1)
        element = o.elements.filter(ctype='VID')
        self.assertEqual(len(element), 2)
        element = o.elements.filter(ctype='MAP')
        self.assertEqual(len(element), 1)
    	for c in Crisis.objects.all():
    		c.delete()

    def test_com_handler_1(self):
    	root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
        per_handler(root[0])
        p = Person.objects.get(id='PER_BROBMA')

        com_handler(root[0], p)
        p.save()
        summary = p.summary
        self.assertNotEqual(summary.find('Barack Obama is the 44th President of the United States'), -1)
    	for c in Crisis.objects.all():
    		c.delete()

    def test_com_handler_2(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSHESSG.xml')).read())
        cri_handler(root[0])
        c = Crisis.objects.get(id='CRI_SHESSG')

        com_handler(root[0], c)
        c.save()
        summary = c.summary
        self.assertNotEqual(summary.find('Adam Lanza is believed to have shot his mother'), -1)
    	for c in Crisis.objects.all():
    		c.delete()

    def test_com_handler_3(self):
        root = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestUNDWAY.xml')).read())
        org_handler(root[0])
        o = Organization.objects.get(id='ORG_UNDWAY')

        com_handler(root[0], o)
        o.save()
        summary = o.summary
        self.assertNotEqual(summary.find('The Sandy Hook School SupportFund (SHSSF) was created by United Way of Western Connecticut'), -1)
    	for c in Crisis.objects.all():
    		c.delete()

    def test_valid_map_1(self):
        """
        testing a valid Google Map
        """
        s = 'https://maps.google.com/maps?f=q&amp;source=s_q&amp;hl=en&amp;geocode=&amp;q=zhongnanhai,+Beijing,+China&amp;aq=1&amp;oq=Zhongnanhai&amp;sll=30.307761,-97.753401&amp;sspn=1.046869,2.113495&amp;ie=UTF8&amp;hq=zhongnanhai,&amp;hnear=Beijing,+China&amp;t=m&amp;z=15&amp;output=embed" text="Zhongnanhai, Beijing, China'

        assert (valid_map(s) is not None)

    def test_valid_map_2(self):
        """
        testing an invalid Google Map
        """
        s = 'https://maps.google/maps?client=ubuntu&channel=fs&q=white+house&oe=utf-8&ie=UTF-8&ei=5xgAUsqdFIGMyQHknYCoDQ&ved=0CAoQ_AUoAg'

        assert (valid_map(s) is None)

    def test_valid_map_3(self):
        """
        testing a valid Google map with a co.uk extension
        """

        s = 'https://maps.google.co.uk/maps/ms?ie=UTF8&amp;oe=UTF8&amp;msa=0&amp;msid=200809166078445189642.00049f7a79747b94b2b24&amp;t=m&amp;ll=37.300275,12.65625&amp;spn=41.526391,52.734375&amp;z=3&amp;output=embed'

        assert (valid_map(s) is not None)

    def test_valid_map_4(self):
        """
        testing a valid Bing Map
        """
        s = 'http://www.bing.com/maps/embed/?v=2&amp;cp=38.897610~-77.036720&amp;lvl=18&amp;dir=0&amp;sty=r&amp;q=white%20house&amp;form=LMLTEW&amp;emid=85759cd1-e41e-4e69-9d3b-dacd3d688a9c'
        t = 'http://www.bing.com/maps/embed/?v=2&amp;cp=17.573495~-3.998823&amp;lvl=6&amp;dir=0&amp;sty=r&amp;q=mali&amp;form=LMLTEW&amp;emid=e012f5fb-e4f7-1293-6e86-377c384ee67a'

        assert (valid_map(s) is not None)
        assert (valid_map(t) is not None)
        

class TestDownload(TestCase):
    def test_get_crises_1(self):
    	test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSHESSG.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
    	get_crises(root)
    	
    	self.assertEqual(root[0][2].text, 'Spree Shooting')
    	self.assertEqual(root[0][3].text, '2012-12-14')
    	self.assertEqual(root[0][4].text, '09:35:00')
    	for c in Crisis.objects.all():
    		c.delete()
       
    def test_get_crises_2(self):
    	test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSCHERQ.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
    	get_crises(root)
    	
    	self.assertEqual(root[0][2].text, 'Earthquake')
    	self.assertEqual(root[0][3].text, '2008-05-12')
    	self.assertEqual(root[0][4].text, '14:28:01')
    	for c in Crisis.objects.all():
    		c.delete()

    def test_get_crises_3(self):
    	test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestLYCLWR.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
    	get_crises(root)
    	
    	self.assertEqual(root[0][2].text, 'Civil War')
    	self.assertEqual(root[0][3].text, '2011-02-15')
    	for c in Crisis.objects.all():
    		c.delete()

    def test_get_organizations_1(self):
    	test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestUNDWAY.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
    	get_organizations(root)
    	
    	self.assertEqual(root[0][2].text, 'Non-Profit Organization')
    	self.assertEqual(root[0][3].text, 'Worldwide')
    	for c in Crisis.objects.all():
    		c.delete()

    def test_get_organizations_2(self):
    	test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSNQKRF.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
    	get_organizations(root)
    	
    	self.assertEqual(root[0][2].text, 'Non-Profit, Humanitarian Organization')
    	self.assertEqual(root[0][3].text, 'Chengdu, China')
    	for c in Crisis.objects.all():
    		c.delete()

    def test_get_organizations_3(self):
    	test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestNLTLCL.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
    	get_organizations(root)
    	
    	self.assertEqual(root[0][2].text, 'De Facto Government')
    	self.assertEqual(root[0][3].text, 'Benghazi, Libya')
    	for c in Crisis.objects.all():
    		c.delete()

    def test_get_people_1(self):
    	test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestADMLNZ.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
    	get_people(root)
    	
    	self.assertEqual(root[0][2].text, 'Murderer')
    	self.assertEqual(root[0][3].text, 'Newtown, Connecticut')
    	for c in Crisis.objects.all():
    		c.delete()

    def test_get_people_2(self):
    	test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
    	get_people(root)
    	
    	self.assertEqual(root[0][2].text, 'President')
    	self.assertEqual(root[0][3].text, 'Washington, D.C, United States Of America')
    	for c in Crisis.objects.all():
    		c.delete()

    def test_get_people_3(self):
    	test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestHUJNTO.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
    	get_people(root)
    	
    	self.assertEqual(root[0][2].text, 'President')
    	self.assertEqual(root[0][3].text, 'Communist Party Of China')
    	for c in Crisis.objects.all():
    		c.delete()

    def test_get_common_1(self):
    	test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestSHESSG.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
        c = Crisis.objects.get(id='CRI_SHESSG')   	
    	x = ET.SubElement(root, 'Crisis')
        get_common(x, c)
        
        c.save()
        summary= c.summary
        self.assertNotEqual(summary.find('According to reports, most of the shooting'), -1)
    	for c in Crisis.objects.all():
    		c.delete()

    def test_get_common_2(self):
        test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestUNDWAY.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
        c = Organization.objects.get(id='ORG_UNDWAY')   	
    	x = ET.SubElement(root, 'Organization')
        get_common(x, c)
        
        c.save()
        summary= c.summary
        self.assertNotEqual(summary.find('Immediately following the tragedy on December 14, 2012,'), -1)
    	for c in Crisis.objects.all():
    		c.delete()

    def test_get_common_3(self):
        test = fromstring(open(os.path.join(settings.BASE_DIR, 'crisix/database/TestXML/TestBROBMA.xml')).read())
    	insert(test)
    	
    	root = ET.Element('WorldCrises')
        c = Person.objects.get(id='PER_BROBMA')   	
    	x = ET.SubElement(root, 'Person')
        get_common(x, c)
        
        c.save()
        summary= c.summary
        self.assertNotEqual(summary.find('He was re-elected president in November 2012,'), -1)
    	for c in Crisis.objects.all():
    		c.delete()

