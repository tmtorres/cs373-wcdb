"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import RequestFactory
from crisix.views import people, organizations, crises
from database.models import *
from datetime import datetime

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
