import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "moviehub.settings")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
application = app
