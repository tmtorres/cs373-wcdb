"""
reset.py is a script that helps us reset and
sync the database very quickly
"""

import os, glob
import settings

os.system('echo "yes" | python manage.py reset database')
os.system('manage.py syncdb')
for f in glob.glob(settings.THUMB_ROOT + '/*'):
    os.remove(f)
