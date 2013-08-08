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
    return render(request, 'utility.html', {'view': 'test'})

def queryrunner(request):
    path = os.path.join(settings.BASE_DIR, 'crisix/wcdb-sql.sql')
    queries = [line for line in open(path) if line.find("SELECT") is not -1 and line.find("--") is -1]
    cursor = connection.cursor()
    rawresult = '<pre style="background-color:#fff;">'
    for item in queries:
        rawresult += item + '</br>'
        cursor.execute(item)
        row = cursor.fetchall()
        for elem in row:
            if str(type(elem[0])).find('date') is not -1:
                elemlist = list(elem)
                elemlist[0] = str(elemlist[0])
                rawresult += ' '.join(elemlist) + '<br>'
                continue
            rawresult += ' '.join(elem) + '<br>'
    return HttpResponse(rawresult + '</pre>')


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def query(request):
    if 'q' in request.GET:
        queryno = int(request.GET['q'])
        if queryno == 1:
            return render(request, 'utility.html', {'view': 'query', 'sql': 'A query in plain English.', 'output': 'ename, dname'})
    return render(request, 'utility.html', {'view': 'query'})

def download(request):
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
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if not form.cleaned_data['merge']:
                clear()
            tmp = os.path.join(settings.MEDIA_ROOT, default_storage.save('tmp/' + request.FILES['file'].name, ContentFile(request.FILES['file'].read())))
            backup = os.path.join(settings.MEDIA_ROOT, 'tmp', 'crisix.json')
            cmd = ['python', os.path.join(settings.BASE_DIR, 'crisix/manage.py'), 'dumpdata', '>', backup]
            os.system(' '.join(cmd).strip())
            '''
            try:
                insert(validate(tmp))
            except Exception, error:
                clear(thumbs=False)
                cmd = ['python', os.path.join(settings.BASE_DIR, 'crisix/manage.py'), 'loaddata', backup]
                os.system(' '.join(cmd).strip())
                return render(request, 'utility.html', {'view': 'form', 'message': 'failure', 'form': form, 'errstr': str(error)})
            '''
            try:
                insert(validate(tmp))
            finally:
                os.remove(tmp)
                os.remove(backup)
            return render(request, 'utility.html', {'view': 'form', 'message': 'success', 'form': UploadFileForm()})
    else:
        form = UploadFileForm()
    return TemplateResponse(request, 'utility.html', {'view': 'form', 'form': form,})
