def show_callback(request):
    #INTERNAL_IPS doesn't work with docker or something:  https://github.com/jazzband/django-debug-toolbar/issues/937
    return 'html' in request.META['HTTP_ACCEPT']
