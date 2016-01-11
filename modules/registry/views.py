from modules.registry.models import RegistryCheckboxesModule, NamePIDModule, \
    RelevantDateModule, StatusModule, LocalIDModule, DescriptionModule, TypeModule


def registry_checkboxes_materialType(request):
    return RegistryCheckboxesModule(xml_tag='materialType').render(request)


def registry_checkboxes_structuralMorphology(request):
    return RegistryCheckboxesModule(xml_tag='structuralMorphology').render(request)


def registry_checkboxes_propertyClass(request):
    return RegistryCheckboxesModule(xml_tag='propertyClass').render(request)


def registry_checkboxes_expAcquisitionMethod(request):
    return RegistryCheckboxesModule(xml_tag='experimentalDataAcquisitionMethod').render(request)


def registry_checkboxes_compAcquisitionMethod(request):
    return RegistryCheckboxesModule(xml_tag='computationalDataAcquisitionMethod').render(request)


def registry_checkboxes_sampleProcessing(request):
    return RegistryCheckboxesModule(xml_tag='sampleProcessing').render(request)


def name_pid(request):
    return NamePIDModule().render(request)


def relevant_date(request):
    return RelevantDateModule().render(request)


def status(request):
    return StatusModule().render(request)


def localid(request):
    return LocalIDModule().render(request)


def description(request):
    return DescriptionModule().render(request)

def resource_type(request):
    return TypeModule().render(request)