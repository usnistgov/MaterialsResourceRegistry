from curate.models import SchemaElement
from models import BlobHosterModule, RawXMLModule, HandleModule,\
    RemoteBlobHosterModule, AdvancedBlobHosterModule, EnumAutoCompleteModule, AutoKeyRefModule
from django.http.response import HttpResponse
import json


def blob_hoster(request):
    return BlobHosterModule().render(request)


def remote_blob_hoster(request):
    return RemoteBlobHosterModule().render(request)


def advanced_blob_hoster(request):
    return AdvancedBlobHosterModule().render(request)


def raw_xml(request):
    return RawXMLModule().render(request)


def handle(request):
    return HandleModule().render(request)


def enum_autocomplete(request):
    return EnumAutoCompleteModule().render(request)


def auto_keyref(request):
    return AutoKeyRefModule().render(request)


def get_updated_keys(request):
    """
        updated_keys[key] = {'ids': [],
                            'tagIDs': []}
        key = key name
        ids = list of posssible values for a key
        tagIDs = HTML element that needs to be updated with the values (keyrefs)
    """

    # delete keys that have been deleted
    for key, values in request.session['keys'].iteritems():
        deleted_ids = []
        for module_id in values['module_ids']:
            try:
                SchemaElement.objects().get(pk=module_id)
            except Exception:
                deleted_ids.append(module_id)
        request.session['keys'][key]['module_ids'] = [item for item in request.session['keys'][key]['module_ids']
                                                if item not in deleted_ids]
    # delete keyrefs that have been deleted
    for keyref, values in request.session['keyrefs'].iteritems():
        deleted_ids = []
        for module_id in values['module_ids']:
            try:
                SchemaElement.objects().get(pk=module_id)
            except Exception:
                deleted_ids.append(module_id)
        request.session['keyrefs'][keyref]['module_ids'] = [item for item in request.session['keyrefs'][keyref]['module_ids']
                                                    if item not in deleted_ids]

    # get the list of keyrefs to update
    updated_keyrefs = []
    for keyref, values in request.session['keyrefs'].iteritems():
        updated_keyrefs.extend(values['module_ids'])


    return HttpResponse(json.dumps(updated_keyrefs), content_type='application/javascript')