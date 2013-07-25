import sys, glob, os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.core import management

from xml.etree.ElementTree import ParseError

from lockdown.decorators import lockdown
from lockdown.forms import AuthForm

from forms import UploadFileForm
from minixsv import pyxsval

from upload import *
from download import *
from models import *
import subprocess

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

def results(request):
    cmd = ['python', 'crisix/manage.py', 'test', 'database', '--noinput']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return HttpResponse((str(c) for c in capture(request, process)))

def test(request):
    return render(request, 'utility.html', {'view': 'test'})

def download(request):
    root = ET.Element('WorldCrises')
    getCrises(root)
    getPeople(root)
    getOrganizations(root)
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="crisix.xml"'
    minidom.parseString(tostring(root)).writexml(response, indent="    ")
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
            tmp = os.path.join(settings.MEDIA_ROOT, default_storage.save('tmp/test.xml', ContentFile(request.FILES['file'].read())))
            return validate(request, tmp)
    else:
        form = UploadFileForm()
    #return render(request, 'utility.html', {'view': 'form', 'form': form,})
    return TemplateResponse(request, 'utility.html', {'view': 'form', 'form': form,})
