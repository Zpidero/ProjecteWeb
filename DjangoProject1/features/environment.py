from splinter import Browser

def before_all(context):
    # behave-django handles DJANGO_SETTINGS_MODULE and django.setup() automatically.
    # It also provides context.base_url for the live test server.
    
    context.browser = Browser("firefox", headless=True)

def after_all(context):
    context.browser.quit()

def before_scenario(context, scenario):
    # Optional: If you want to reset the browser state between scenarios
    pass