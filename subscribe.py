import os, django, shutil
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zuper.settings")
django.setup()

from notifications.pubsub import subscribe_global, listen_presence
subscribe_global()
listen_presence()