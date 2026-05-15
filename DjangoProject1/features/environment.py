from splinter import Browser

def before_all(context):
    # behave-django handles DJANGO_SETTINGS_MODULE and django.setup() automatically.
    # It also provides context.base_url for the live test server.
    
    context.browser = Browser("firefox", headless=True)
    context.base_url = "http://127.0.0.1:8000"


def after_all(context):
    context.browser.quit()

def before_scenario(context, scenario):
    context.browser.cookies.delete()
    pass