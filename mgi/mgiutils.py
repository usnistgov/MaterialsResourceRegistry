################################################################################
#
# File Name: mgiutils.py
# Application: mgi
# Description:
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from collections import OrderedDict


def getListNameFromDependencies(dependencies):
    listName = ''
    if len(dependencies) >= 1:
        for dependencie in dependencies:
            from mgi.models import FormData
            if isinstance(dependencie, OrderedDict):
                listName += dependencie['title'] + ', '
            elif isinstance(dependencie, FormData):
                listName += dependencie.name + ', '
            else:
                listName += dependencie.title + ', '
    return listName[:-2] if listName != '' else listName


def getListTemplateDependenciesFormData(object_id):
    from mgi.models import FormData
    return list(FormData.objects(template=object_id, xml_data_id__exists=False, xml_data__exists=True))


def getListTemplateDependenciesRecord(object_id):
    from mgi.models import XMLdata
    return XMLdata.find({'schema': str(object_id)})


def getListTypeDependenciesType(object_id):
    from mgi.models import Type
    return list(Type.objects(dependencies=object_id))


def getListTypeDependenciesTemplate(object_id):
    from mgi.models import Template
    return list(Template.objects(dependencies=object_id))


def getListNameTemplateDependenciesRecordFormData(object_id):
    list = getListTemplateDependenciesFormData(object_id)
    list.extend(getListTemplateDependenciesRecord(object_id))
    return getListNameFromDependencies(list)


def getListNameTypeDependenciesTemplateType(object_id):
    list = getListTypeDependenciesType(object_id)
    list.extend(getListTypeDependenciesTemplate(object_id))
    return getListNameFromDependencies(list)



