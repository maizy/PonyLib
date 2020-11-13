import os
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] [%(levelname)s] %(name)s:%(message)s",
)

logging.info('sys.path: %s', sys.path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ponylib.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
