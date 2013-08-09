import sys, glob, os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.core import management
from django.db.models import Q
from django.db import connection, transaction


from xml.etree.ElementTree import ParseError
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, fromstring
from xml.etree.ElementTree import ElementTree
from xml.dom import minidom

from lockdown.decorators import lockdown
from lockdown.forms import AuthForm

from forms import UploadFileForm
from minixsv import pyxsval

from models import *
from upload import clear, validate, insert
from download import get_crises, get_people, get_organizations
from search import normalize_query, get_query, contextualize, relevance_sort
import subprocess, re, operator
from crisix.views import get_icon

DISPLAY_TYPE = {'per': 'people', 'cri': 'crises', 'org': 'organizations'}
def search(request):
    '''
    Takes in a request in the form ?q=  and searches the database for a match.
    AND entries for multiword search are displayed before OR entries
    '''
    query_string = ''
    found_entries = []
    if 'q' in request.GET:
        query_string = request.GET['q'].strip()
        if len(query_string):
            and_query = get_query(query_string, ['name', 'kind', 'location']) | Q(summary__iregex='(^| )' +  query_string + '($|[ .,!?])')
            or_query = get_query(query_string, ['name', 'kind', 'location'], operator.or_)
            and_entries = relevance_sort(query_string, ['name', 'kind', 'location'], Entity.objects.filter(and_query).order_by('name'))
            or_entries = relevance_sort(query_string, ['name', 'kind', 'location'], Entity.objects.filter(or_query).order_by('name'))
            found_entries = list(and_entries) + [o for o in or_entries if o not in and_entries]
    return render(request, 'search.html', {'query_string': query_string, 'entries': [{
        'type': DISPLAY_TYPE[str(e.id).lower()[:3]],
        'id': str(e.id).lower()[4:],
        'name': e.name, 
        'kind': e.kind, 
        'location': e.location if '<li>' not in e.location else ''.join(e.location.split('<li>')).replace('</li>', ', ').rstrip(', '),
        'summary': contextualize(e.summary, query_string),
        'thumb': get_icon(e)
    } for e in found_entries]})

def utility(request):
    """
    utility returns a rendered display of our utility page
    """
    return render(request, 'utility.html', {'view': 'index'})

newlines = ['\n', '\r\n', '\r']
def capture(request, process):
    yield open(os.path.join(settings.BASE_DIR, 'crisix/style.html')).read()
    while True:
        out = process.stderr.read(1)
        if out == '' and process.poll() != None:
            break
        if out in newlines:
            yield '</br>'
        if out != '':
            yield out

def runner(request):
    cmd = ['python', os.path.join(settings.BASE_DIR, 'crisix/manage.py'), 'test', 'database', '--noinput']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return HttpResponse((str(c) for c in capture(request, process)))

def test(request):
    """
    test renders a page when the unit tests are ran
    """
    return render(request, 'utility.html', {'view': 'test'})

def query(request):
    if 'q' in request.GET:
        queryno = int(request.GET['q'])
        if queryno == 1:
            querystring = 'Get celebrities (actors, musicians, athletes) related to crises/organizations'
            sql = ['SELECT id, kind, name FROM database_entity e WHERE id LIKE "PER_%%"',
                   'AND kind REGEXP ".*(Actor|Actress|Singer|Celebrity|Athlete|Player).*"', 
                   'AND (EXISTS (SELECT * from database_crisis_people cp WHERE cp.person_id = e.id)',
                   'OR EXISTS (SELECT * from database_organization_people cp WHERE cp.person_id = e.id))']
            cursor = connection.cursor()
            cursor.execute(' '.join(sql).strip())
            rows = cursor.fetchall()
            return render(request, 'utility.html', {'view': 'query', 
                                                    'querystring': querystring, 
                                                    'rows': '\n'.join([', '.join(r).strip(', ') for r in rows])})
        elif queryno == 2:
            querystring = 'Get all crises/organizations/people who have feeds'
            sql = 'SELECT DISTINCT entity_id, name FROM database_webelement AS w, database_entity AS e WHERE ctype = "FEED" AND w.entity_id = e.id'
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return render(request, 'utility.html', {'view': 'query', 
                                                    'querystring': querystring, 
                                                    'rows': '\n'.join([', '.join(r).strip(', ') for r in rows])})
        elif queryno == 3:
            querystring = 'Get the name and location of all crises related to natural disasters'
            sql = 'SELECT kind, name, location FROM database_entity WHERE kind REGEXP ".*(Earthquake|Fire|Tsunami|Natural Disaster|Epidemic|Hurricane|Tornado|Flood|Storm|Blizzard).*" AND id LIKE "CRI_%%"'
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return render(request, 'utility.html', {'view': 'query', 
                                                    'querystring': querystring, 
                                                    'rows': '\n'.join([', '.join(r).strip(', ') for r in rows])})
        elif queryno == 4:
            querystring = 'People involved in crises that happened in China/Japan'
            sql = 'SELECT person_id, name FROM database_crisis_people AS p, database_entity AS e WHERE p.person_id=e.id AND crisis_id IN (SELECT id FROM database_entity WHERE (location LIKE "%%China%%" OR location LIKE "%%Japan%%") AND id LIKE "CRI_%%")'
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return render(request, 'utility.html', {'view': 'query', 
                                                    'querystring': querystring, 
                                                    'rows': '\n'.join([', '.join(r).strip(', ') for r in rows])})
        elif queryno == 5:
            querystring = 'Crises that are tied to a president'
            sql = 'SELECT crisis_id, name FROM database_crisis_people AS p, database_entity AS e WHERE p.crisis_id=e.id AND person_id IN (SELECT id FROM database_entity WHERE kind LIKE "%%President%%")'
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return render(request, 'utility.html', {'view': 'query', 
                                                    'querystring': querystring, 
                                                    'rows': '\n'.join([', '.join(r).strip(', ') for r in rows])})
        elif queryno == 6:
            querystring = 'All crises in alphabetical order by name of crisis (no duplicates)'
            sql = 'SELECT DISTINCT id, name FROM database_entity WHERE id LIKE "CRI_%%" ORDER BY name'
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return render(request, 'utility.html', {'view': 'query', 
                                                    'querystring': querystring, 
                                                    'rows': '\n'.join([', '.join(r).strip(', ') for r in rows])})
        elif queryno == 7:
            querystring = 'Crises whose kind value contains the word "shooting"'
            sql = 'SELECT id, kind, name FROM database_entity WHERE kind LIKE "%%Shooting%%" AND id LIKE "CRI_%%"'
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return render(request, 'utility.html', {'view': 'query', 
                                                    'querystring': querystring, 
                                                    'rows': '\n'.join([', '.join(r).strip(', ') for r in rows])})
        elif queryno == 8:
            querystring = 'All people with first names that start with letters A through P (no duplicates)'
            sql = 'SELECT id, name FROM database_entity WHERE name REGEXP "^[A-P]" AND id LIKE "PER_%%" ORDER BY name'
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return render(request, 'utility.html', {'view': 'query', 
                                                    'querystring': querystring, 
                                                    'rows': '\n'.join([', '.join(r).strip(', ') for r in rows])})
        elif queryno == 9:
            querystring = 'Show the name and economic impact of natural disasters occuring after 2001'
            sql = 'SELECT e.name, c.eimpact FROM database_crisis c, database_entity e WHERE date >= "2002-01-01" AND kind REGEXP ".*(Earthquake|Fire|Tsunami|Natural Disaster|Epidemic|Hurricane|Tornado|Flood|Storm|Blizzard).*" AND c.entity_ptr_id = e.id ORDER BY c.date'
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return render(request, 'utility.html', {'view': 'query', 
                                                    'querystring': querystring, 
                                                    'rows': '\n'.join([', '.join(r).strip(', ') for r in rows])})
        elif queryno == 10:
            querystring = 'Crises that took place in Texas (Location data should contain "Texas" or "TX")'
            sql = 'SELECT id, name, location FROM database_entity WHERE (location LIKE "%%Texas%%" OR location LIKE "%%TX%%") and id LIKE "CRI_%%"'
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return render(request, 'utility.html', {'view': 'query', 
                                                    'querystring': querystring, 
                                                    'rows': '\n'.join([', '.join(r).strip(', ') for r in rows])})

    return render(request, 'utility.html', {'view': 'query'})

def download(request):
    """
    download renders a page for the export page within utilities
    """
    root = ET.Element('WorldCrises')
    get_crises(root)
    get_people(root)
    get_organizations(root)
    response = HttpResponse(mimetype='text/xml')
    response['Content-Disposition'] = 'attachment; filename="crisix.xml"'
    minidom.parseString(tostring(root)).writexml(response, addindent='    ', indent='    ', newl='\n')
    return response

@lockdown()
def upload(request):
    """
    upload renders a page for the import page within utilities
    """
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if not form.cleaned_data['merge']:
                clear()
            tmp = os.path.join(settings.MEDIA_ROOT, default_storage.save('tmp/' + request.FILES['file'].name, ContentFile(request.FILES['file'].read())))
            backup = os.path.join(settings.MEDIA_ROOT, 'tmp', 'crisix.json')
            cmd = ['python', os.path.join(settings.BASE_DIR, 'crisix/manage.py'), 'dumpdata', '>', backup]
            os.system(' '.join(cmd).strip())
            try:
                insert(validate(tmp))
            except Exception, error:
                clear(thumbs=False)
                cmd = ['python', os.path.join(settings.BASE_DIR, 'crisix/manage.py'), 'loaddata', backup]
                os.system(' '.join(cmd).strip())
                return render(request, 'utility.html', {'view': 'form', 'message': 'failure', 'form': form, 'errstr': str(error)})
            finally:
                os.remove(tmp)
                os.remove(backup)
            return render(request, 'utility.html', {'view': 'form', 'message': 'success', 'form': UploadFileForm()})
    else:
        form = UploadFileForm()
    return TemplateResponse(request, 'utility.html', {'view': 'form', 'form': form,})
