from django.conf import settings

def domain_context_processor(request):

    return {
        'CUSTOM_TITLE': settings.CUSTOM_TITLE if hasattr(settings, 'CUSTOM_TITLE') else '',
        'CUSTOM_ORGANIZATION': settings.CUSTOM_ORGANIZATION if hasattr(settings, 'CUSTOM_ORGANIZATION') else '',
        'CUSTOM_NAME': settings.CUSTOM_NAME if hasattr(settings, 'CUSTOM_NAME') else '',
        'CUSTOM_SUBTITLE': settings.CUSTOM_SUBTITLE if hasattr(settings, 'CUSTOM_SUBTITLE') else '',
        'CUSTOM_DATA': settings.CUSTOM_DATA if hasattr(settings, 'CUSTOM_DATA') else '',
        'CUSTOM_CURATE': settings.CUSTOM_CURATE if hasattr(settings, 'CUSTOM_CURATE') else '',
        'CUSTOM_EXPLORE': settings.CUSTOM_EXPLORE if hasattr(settings, 'CUSTOM_EXPLORE') else '',
        'CUSTOM_COMPOSE': settings.CUSTOM_COMPOSE if hasattr(settings, 'CUSTOM_COMPOSE') else '',
        'CUSTOM_URL': settings.CUSTOM_URL if hasattr(settings, 'CUSTOM_URL') else '',
    }