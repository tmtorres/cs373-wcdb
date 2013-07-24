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
from crisix.views import people, organizations, crises

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
        resp = self.client.get('/crisix/')
        self.assertEqual(resp.status_code, 200)

        # Test if database is properly populated
        self.assertEqual(self.p.name,'Barack Obama')


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
        self.assertNotEqual(htmlstring.find('<h1 class="main-focus">Barack Obama</h1>'),-1)

    def test_people4(self):
        # Test if related objects are on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/people/brobma')
        response = people(request, 'brobma')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<li><a href="/crisix/crises/haiear/">2010 Haiti Earthquake</a></li>'),-1)
        self.assertNotEqual(htmlstring.find('<li><a href="/crisix/organizations/whorgn/">World Health Organization</a></li>'),-1)

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
        self.assertNotEqual(htmlstring.find('<h1 class="main-focus">World Health Organization</h1>'),-1)

    def test_organization4(self):
        # Test if related objects are on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/organization/whorgn')
        response = organizations(request, 'whorgn')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<li><a href="/crisix/crises/haiear/">2010 Haiti Earthquake</a></li>'),-1)
        self.assertNotEqual(htmlstring.find('<li><a href="/crisix/people/brobma/">Barack Obama</a></li>'),-1)


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
        # Test if person kind is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/crises/haiear')
        response = crises(request, 'haiear')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<li>Natural Disaster</li>'),-1)

    def test_crisis3(self):
        # Test if person name is on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/crises/haiear')
        response = crises(request, 'haiear')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<h1 class="main-focus">2010 Haiti Earthquake</h1>'),-1)

    def test_crisis4(self):
        # Test if related objects are on page in format designated in template
        request_factory = RequestFactory()
        request = request_factory.get('/crisix/crises/haiear')
        response = crises(request, 'haiear')
        htmlstring = response.content
        self.assertNotEqual(htmlstring.find('<li><a href="/crisix/organizations/whorgn/">World Health Organization</a></li>'),-1)
        self.assertNotEqual(htmlstring.find('<li><a href="/crisix/people/brobma/">Barack Obama</a></li>'),-1)

class TestUpload(TestCase):
    def test_insert_1(self):
        root = fromstring(open('TestCrisis.xml').read())
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

    def test_insert_2(self):
        root = fromstring(open('TestPerson.xml').read())
        insert(root)
        p = None
        
        try:
            p = Person.objects.get(id='PER_BROBMA')
        except Person.DoesNotExist:
    	    self.assertTrue(False)
        self.assertEqual(str(p.kind), 'President')
        self.assertEqual(str(p.location), 'Washington, D.C, United States of America')

    def test_insert_3(self):
        root = fromstring(open('TestOrganization.xml').read())
        insert(root)
        o = None
        
        try:
            o = Organization.objects.get(id='ORG_UNDWAY')
        except Organization.DoesNotExist:
    	    self.assertTrue(False)
        self.assertEqual(str(o.kind), 'Non-profit Organization')
        self.assertEqual(str(o.location), 'Worldwide')
        # self.assertTrue('<li>In 1887, a Denver woman, a priest, two ministers' in o.history)
        self.assertEqual(str(o.contact), '<li href="http://apps.unitedway.org/contact/">Contact Form</li>')

    def test_get_entity_1(self): 
    	root = fromstring(open('TestCrisis.xml').read())
    	insert(root)
    	
        a = getEntity(Crisis, 'CRI_SHESSG')
        self.assertEqual(str(a.kind), 'Spree Shooting')
        self.assertEqual(str(a.date), '2012-12-14')
        self.assertEqual(str(a.time), '09:35:00')
        self.assertEqual(str(a.location), '<li>Newtown, Connecticut</li>')

    def test_get_entity_2(self):
    	root2 = fromstring(open('TestPerson.xml').read())
    	insert(root2)
    	
    	b = getEntity(Person, 'PER_BROBMA')
    	self.assertEqual(str(b.kind), 'President')
    	self.assertEqual(str(b.location), 'Washington, D.C, United States of America')

    def test_get_entity_3(self):
    	root3 = fromstring(open('TestOrganization.xml').read())
    	insert(root3)
    	
    	c = getEntity(Organization, 'ORG_UNDWAY')   	
        self.assertEqual(str(c.kind), 'Non-profit Organization')
        self.assertEqual(str(c.location), 'Worldwide')
        self.assertEqual(str(c.contact), '<li href="http://apps.unitedway.org/contact/">Contact Form</li>')
    	
    def test_cri_handler_1(self):
    	root = fromstring(open('TestCrisis.xml').read())    
    	    
    	criHandler(root[0]) 
    	c = Crisis.objects.get(id='CRI_SHESSG')
    	self.assertEqual(str(c.kind), 'Spree Shooting')
        self.assertEqual(str(c.date), '2012-12-14')
        self.assertEqual(str(c.time), '09:35:00')
        self.assertEqual(str(c.location), '<li>Newtown, Connecticut</li>')
       
    def test_cri_handler_2(self):
        root = fromstring(open('TestCrisis.xml').read())
        
        criHandler(root[1])
        c = Crisis.objects.get(id='CRI_SCHERQ')
        self.assertEqual(str(c.kind), 'Earthquake')
        self.assertEqual(str(c.date), '2008-05-12')
        self.assertEqual(str(c.time), '14:28:01')
        self.assertEqual(str(c.location), '<li>Wenchuan County, Sichuan</li><li>Sichuan Province</li>')
           
    def test_cri_handler_3(self):
        root = fromstring(open('TestCrisis.xml').read())
        
        criHandler(root[2])
        c = Crisis.objects.get(id='CRI_LYCLWR')
        self.assertEqual(str(c.kind), 'Civil War')
        self.assertEqual(str(c.date), '2011-02-15')
        self.assertEqual(str(c.location), '<li>Libya</li>')

    def test_org_handler_1(self):
        root = fromstring(open('TestOrganization.xml').read())
        
        orgHandler(root[0])
        o = Organization.objects.get(id='ORG_UNDWAY')
        self.assertEqual(str(o.kind), 'Non-profit Organization')
        self.assertEqual(str(o.location), 'Worldwide')
        self.assertEqual(str(o.contact), '<li href="http://apps.unitedway.org/contact/">Contact Form</li>')

    def test_org_handler_2(self):
        root = fromstring(open('TestOrganization.xml').read())
        
        orgHandler(root[1])
        o = Organization.objects.get(id='ORG_SNQKRF')
        self.assertEqual(str(o.kind), 'Non-profit, humanitarian Organization')
        self.assertEqual(str(o.location), 'Chengdu, China')
        self.assertTrue('<li>Volunteer: volunteer@sichuan-quake-relief.org</li>' in str(o.contact)) 

    def test_org_handler_3(self):
        root = fromstring(open('TestOrganization.xml').read())
        
        orgHandler(root[2])
        o = Organization.objects.get(id='ORG_NLTLCL')
        self.assertEqual(str(o.kind), 'de facto Government')
        self.assertEqual(str(o.location), 'Benghazi, Libya')
        self.assertEqual(str(o.contact), '<li> Organization is no longer active. </li>')

    def test_per_handler_1(self):
        root = fromstring(open('TestPerson.xml').read())
        
        perHandler(root[0])
        p = Person.objects.get(id='PER_BROBMA')
        self.assertEqual(str(p.kind), 'President')
        self.assertEqual(str(p.location), 'Washington, D.C, United States of America')

    def test_per_handler_2(self):
        root = fromstring(open('TestPerson.xml').read())
        
        perHandler(root[1])
        p = Person.objects.get(id='PER_ADMLNZ')
        self.assertEqual(str(p.kind), 'Murderer')
        self.assertEqual(str(p.location), 'Newtown, Connecticut')

    def test_per_handler_3(self):
        root = fromstring(open('TestPerson.xml').read())
        
        perHandler(root[2])
        p = Person.objects.get(id='PER_HUJNTO')
        self.assertEqual(str(p.kind), 'President')
        self.assertEqual(str(p.location), 'Communist Party of China')

    def test_insert_elem_1(self):
        pass
        
    def test_insert_elem_2(self):
        pass

    def test_insert_elem_3(self):
        pass

    def test_com_handler_1(self):
    	"""
    	root = fromstring(open('TestCrisis.xml'))
    	
    	c = Crisis.objects.get(id='CRI_SHESSG')
    	comHandler(root[0][10], c)
    	self.assertEqual(str(c.maps), 
    	"""

    def test_com_handler_2(self):
        pass

    def test_com_handler_3(self):
        pass

class TestDownload(TestCase):
    def test_get_crises_1(self):
    	root = fromstring(open('TestCrisis.xml').read())
    	getCrises(root)
    	
    	self.assertEqual(root[0][2].text, 'Spree Shooting')
    	self.assertEqual(root[0][3].text, '2012-12-14')
    	self.assertEqual(root[1][2].text, 'Earthquake')
    	self.assertEqual(root[2][3].text, '2011-02-15')
        
    def test_get_crises_2(self):
        pass

    def test_get_crises_3(self):
        pass

    def test_get_organizations_1(self):
        root = fromstring(open('TestOrganization.xml').read())
    	getOrganizations(root)
    	
    	self.assertEqual(root[0][2].text, 'Non-profit Organization')
    	self.assertEqual(root[0][3].text, 'Worldwide')
    	self.assertEqual(root[1][2].text, 'Non-profit, humanitarian Organization')
    	self.assertEqual(root[2][3].text, 'Benghazi, Libya')

    def test_get_organizations_2(self):
        pass

    def test_get_organizations_3(self):
        pass

    def test_get_people_1(self):
        root = fromstring(open('TestPerson.xml').read())
    	getPeople(root)
    	
    	self.assertEqual(root[0][2].text, 'President')
    	self.assertEqual(root[0][3].text, 'Washington, D.C, United States of America')

    def test_get_people_2(self):
    	pass

    def test_get_people_3(self):
        pass

    def test_get_common_1(self):
        pass

    def test_get_common_2(self):
        pass

    def test_get_common_3(self):
        pass

class TestViews(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
