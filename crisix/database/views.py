import sys, glob, os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse

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

'''
def test(request):
    process = subprocess.Popen('python manage.py test database > TestWCDB2.out 2>&1', shell=True)
    process.wait()
    assert os.path.exists('TestWCDB2.out')
    return render(request, 'utility.html', {'view': 'test', 'output': open('TestWCDB2.out').read().split('\n')[:-4]})
'''
newlines = ['\n', '\r\n', '\r']
def capture(child):
    while True:
        out = child.stderr.read(1)
        if out == '' and child.poll() != None:
            break
        if out in newlines:
            yield '</br>'
        if out != '':
            yield out

def results(request):
    cmd = ['python', 'manage.py', 'test', 'database']
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return HttpResponse((str(c) for c in capture(child)))

def test(request):
    return render(request, 'utility.html', {'view': 'test'})

def download(request):
    root = ET.Element('WorldCrises')
    getCrises(root)
    getPeople(root)
    getOrganizations(root)
    response = HttpResponse(content_type='text/xml')
    response['Content-Disposition'] = 'attachment; filename="crisix.xml"'
    minidom.parseString(tostring(root)).writexml(response, indent="    ")
    return response

def validate(request, file):
    try:
        elementTreeWrapper = pyxsval.parseAndValidateXmlInput(file, xsdFile='/u/tmtorres/CS373/cs373-wcdb/WCDB1.xsd.xml',
                             xmlIfClass=pyxsval.XMLIF_ELEMENTTREE)
        elemTree = elementTreeWrapper.getTree()
        root = elemTree.getroot()
        insert(root)
    except:
        return render(request, 'utility.html', {'view': 'failure'})
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
            assert False
    else:
        form = UploadFileForm()
    #return render(request, 'utility.html', {'view': 'form', 'form': form,})
    return TemplateResponse(request, 'utility.html', {'view': 'form', 'form': form,})
