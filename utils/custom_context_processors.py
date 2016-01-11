from django.conf import settings

def domain_context_processor(request):

    return {
        'CUSTOM_TITLE': settings.CUSTOM_TITLE if hasattr(settings, 'CUSTOM_TITLE') else '',
        'CUSTOM_SUBTITLE': settings.CUSTOM_SUBTITLE if hasattr(settings, 'CUSTOM_SUBTITLE') else '',
        'CUSTOM_DATA': settings.CUSTOM_DATA if hasattr(settings, 'CUSTOM_DATA') else '',
        'CUSTOM_DESCRIPTION': settings.CUSTOM_DESCRIPTION if hasattr(settings, 'CUSTOM_DESCRIPTION') else '',
        'CUSTOM_CURATE': settings.CUSTOM_CURATE if hasattr(settings, 'CUSTOM_CURATE') else '',
        'CUSTOM_EXPLORE': settings.CUSTOM_EXPLORE if hasattr(settings, 'CUSTOM_EXPLORE') else '',
        'CUSTOM_COMPOSE': settings.CUSTOM_COMPOSE if hasattr(settings, 'CUSTOM_COMPOSE') else '',
    }