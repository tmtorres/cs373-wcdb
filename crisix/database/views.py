import sys, glob, os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.core import management
from django.db.models import Q

from xml.etree.ElementTree import ParseError
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import tostring, fromstring
from xml.etree.ElementTree import ElementTree
from xml.dom import minidom

from lockdown.decorators import lockdown
from lockdown.forms import AuthForm

from forms import UploadFileForm
from minixsv import pyxsval

from models import Entity
from upload import clear, validate, insert
from download import get_crises, get_people, get_organizations
from search import normalize_query, get_query, contextualize, relevance_sort
import subprocess, re
from crisix.views import generate_thumbs

def search(request):
    query_string = ''
    found_entries = None
    if 'q' in request.GET:
        query_string = request.GET['q'].strip()
        entry_query = get_query(query_string, ['name', 'kind', 'location']) | Q(summary__iregex='(^| )' +  query_string + '($|[ .,!?])')
        found_entries = relevance_sort(query_string, ['name', 'kind', 'location'], Entity.objects.filter(entry_query).order_by('name'))
    return render(request, 'search.html', {'query_string': query_string, 'entries': [{
        'type': str(e.id).lower()[:3],
        'id': str(e.id).lower()[4:],
        'name': e.name, 
        'kind': e.kind, 
        'location': e.location if '<li>' not in e.location else ''.join(e.location.split('<li>')).replace('</li>', ', ').rstrip(', '),
        'summary': contextualize(e.summary, query_string),
        'thumb': generate_thumbs(e, 1)[0].thumb,
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
            tmp = os.path.join(settings.MEDIA_ROOT, default_storage.save('tmp/test.xml', ContentFile(request.FILES['file'].read())))
            try:
                insert(validate(tmp))
            except pyxsval.XsvalError, errstr:
                return render(request, 'utility.html', {'view': 'failure', 'errstr': errstr})
            except ParseError, e:
                return render(request, 'utility.html', {'view': 'failure', 'errstr': 'Invalid token: line ' + str(e.position[0]) + ', column ' + str(e.position[1])})
            finally:
                os.remove(tmp)
            return render(request, 'utility.html', {'view': 'success'})
    else:
        form = UploadFileForm()
    return TemplateResponse(request, 'utility.html', {'view': 'form', 'form': form,})
