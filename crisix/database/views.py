import sys, os

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, render

from lockdown.decorators import lockdown
from lockdown.forms import AuthForm

from forms import UploadFileForm
from minixsv import pyxsval

from upload import *
from download import *
from models import *

cwd = os.path.dirname(os.path.realpath(sys.argv[0]))

def index(request):
    return render(request, 'utility.html')

def download(request):
    '''
        The download module acts as the export facility by taking the information from the Django models and
        creating a valid XML from the retrieved information. The download function takes in a request from the
        web site. This request is for the export to be performed. The function begins by creating an Element
        Tree and then by first constructing the crises XML portions first, then the people and organizations.
    '''
    root = ET.Element('WorldCrises')
    getCrises(root)
    getPeople(root)
    getOrganizations(root)
    return HttpResponse(minidom.parseString(tostring(root)).toprettyxml(indent="    "), mimetype="text/plain")

def validate(file):
    try:
        elementTreeWrapper = pyxsval.parseAndValidateXmlInput(file, xsdFile='/u/tmtorres/CS373/cs373-wcdb/WCDB1.xsd.xml',
                             xmlIfClass=pyxsval.XMLIF_ELEMENTTREE)
        elemTree = elementTreeWrapper.getTree()
        root = elemTree.getroot()
        insert(root)

    except pyxsval.XsvalError, errstr:
        return HttpResponse(errstr)
    finally:
        os.remove(file)
    c = '\n'.join([str(e) for e in Crisis.objects.all()])
    o = '\n'.join([str(e) for e in Organization.objects.all()])
    p = '\n'.join([str(e) for e in Person.objects.all()])
    return HttpResponse(c + o + p, mimetype="text/plain")
    #return HttpResponse('Success!')

@lockdown()
def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            tmp = os.path.join(settings.MEDIA_ROOT, default_storage.save('tmp/test.xml', ContentFile(request.FILES['file'].read())))
            return validate(tmp)
        else:
            assert False
    else:
        form = UploadFileForm()

    return render_to_response('import.html', {'form': form,})
