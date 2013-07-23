"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import *
from upload import *
from download import *
from views import *

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, fromstring
from xml.etree.ElementTree import ElementTree

class TestUpload(TestCase):
    def test_insert_1(self):
        root = fromstring(''.join([
                          '<WorldCrises>',
                          '<Crisis ID="CRI_SHESSG" Name="Sandy Hook Elementary School Shooting">',
                          '<Kind>Spree Shooting</Kind>',
                          '<Date>2012-12-14</Date>',
                          '<Time>09:35:00</Time>',
                          '<Locations><li>Newtown, Connecticut</li></Locations>',
                          '</Crisis>'
                          '</WorldCrises>',
        ]))
        insert(root)
        c = Crisis.objects.get(id='CRI_SHESSG')
        self.assertEqual(str(c.kind), 'Spree Shooting')
        self.assertEqual(str(c.date), '2012-12-14')
        self.assertEqual(str(c.time), '09:35:00')
        self.assertEqual(str(c.location), '<li>Newtown, Connecticut</li>')

    def test_insert_2(self):
        root = fromstring(''.join([
                          '<WorldCrises>',
                          '<Person ID="PER_ADMLNZ" Name="Adam Lanza">',
                          '<Kind>Murderer</Kind>',
                          '<Location>Newtown, Connecticut</Location>',
                          '</Person>'
                          '</WorldCrises>',
        ]))
        insert(root)
        c = Person.objects.get(id='PER_ADMLNZ')
        self.assertEqual(str(c.kind), 'Murderer')
        self.assertEqual(str(c.location), 'Newtown, Connecticut')

    def test_insert_3(self):
        pass

    def test_get_entity_1(self):
        pass

    def test_get_entity_2(self):
        pass

    def test_get_entity_3(self):
        pass

    def test_cri_handler_1(self):
        pass

    def test_cri_handler_2(self):
        pass

    def test_cri_handler_3(self):
        pass

    def test_org_handler_1(self):
        pass

    def test_org_handler_2(self):
        pass

    def test_org_handler_3(self):
        pass

    def test_per_handler_1(self):
        pass

    def test_per_handler_2(self):
        pass

    def test_per_handler_3(self):
        pass

    def test_insert_elem_1(self):
        pass

    def test_insert_elem_2(self):
        pass

    def test_insert_elem_3(self):
        pass

    def test_com_handler_1(self):
        pass

    def test_com_handler_2(self):
        pass

    def test_com_handler_3(self):
        pass

class TestDownload(TestCase):
    def test_get_crises_1(self):
        pass

    def test_get_crises_2(self):
        pass

    def test_get_crises_3(self):
        pass

    def test_get_organizations_1(self):
        pass

    def test_get_organizations_2(self):
        pass

    def test_get_organizations_3(self):
        pass

    def test_get_people_1(self):
        pass

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
