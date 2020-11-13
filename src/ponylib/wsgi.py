import os

import sys
print('sys.path: {}'.format(';'.join(sys.path)))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ponylib.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
