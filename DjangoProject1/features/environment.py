import os
import django
from splinter import Browser


def before_all(context):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoProject1.settings")
    django.setup()

    context.browser = Browser("firefox", headless=True)
    context.server_url = "http://127.0.0.1:8000"


def after_all(context):
    context.browser.quit()