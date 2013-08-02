import sys, glob, os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.core import management

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
from upload import insert, clear
from download import getCrises, getPeople, getOrganizations
from search import normalize_query, get_query
import subprocess

def contextualize(summary, query_string):
    context = summary.split()
    i = [context.index(s) for s in context if query_string.lower() in s.lower()]
    if not len(i):
        context = ' '.join(context[:50]).lstrip('.?!,0123456789 ').rstrip(',')
        return context if context.endswith('.') else context + ' ...'
    else:
        start = max(0, i[0] - 25)
        end = min(len(context), start + 50)
        context = ' '.join(context[start:end]).lstrip('.?!,0123456789 ').rstrip(',')
        return ('... ' if (context[0].islower() or context[0].isdigit()) else '') + (context if context.endswith('.') else context + ' ...')

def search(request):
    query_string = ''
    found_entries = None
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query, terms = get_query(query_string, ['name', 'kind', 'location', 'summary',])
        found_entries = Entity.objects.filter(entry_query)
    return render(request, 'search.html', {'query_string': query_string, 'entries': [{
        'type': str(e.id).lower()[:3],
        'id': str(e.id).lower()[4:],
        'name': e.name, 
        'kind': e.kind, 
        'location': e.location if '<li>' not in e.location else ''.join(e.location.split('<li>')).replace('</li>', ', ').rstrip(', '),
        'summary': contextualize(e.summary, query_string)
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
    getCrises(root)
    getPeople(root)
    getOrganizations(root)
    response = HttpResponse(mimetype='text/xml')
    response['Content-Disposition'] = 'attachment; filename="crisix.xml"'
    minidom.parseString(tostring(root)).writexml(response, addindent='    ', indent='    ', newl='\n')
    return response

def validate(request, file):
    try:
        elementTreeWrapper = pyxsval.parseAndValidateXmlInput(file, xsdFile=os.path.join(settings.BASE_DIR, 'WCDB2.xsd.xml'),
                             xmlIfClass=pyxsval.XMLIF_ELEMENTTREE)
        elemTree = elementTreeWrapper.getTree()
        root = elemTree.getroot()
        insert(root)
    except pyxsval.XsvalError, errstr:
        return render(request, 'utility.html', {'view': 'failure', 'errstr': errstr})
    except ParseError, e:
        return render(request, 'utility.html', {'view': 'failure', 'errstr': 'Invalid token: line ' + str(e.position[0]) + ', column ' + str(e.position[1])})
    finally:
        os.remove(file)
    return render(request, 'utility.html', {'view': 'success'})

@lockdown()
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            if not form.cleaned_data['merge']:
                clear()
            tmp = os.path.join(settings.MEDIA_ROOT, default_storage.save('tmp/test.xml', ContentFile(request.FILES['file'].read())))
            return validate(request, tmp)
    else:
        form = UploadFileForm()
    return TemplateResponse(request, 'utility.html', {'view': 'form', 'form': form,})
