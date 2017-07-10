from modules.registry.models import RegistryCheckboxesModule, StatusModule, LocalIDModule, DescriptionModule, TypeModule, \
    NamePIDModule, FancyTreeModule


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


def status(request):
    return StatusModule().render(request)


def localid(request):
    return LocalIDModule().render(request)


def description(request):
    return DescriptionModule().render(request)


def resource_type(request):
    return TypeModule().render(request)


def name_pid(request):
    return NamePIDModule().render(request)


def fancy_tree_data_origin(request):
    return FancyTreeModule(xml_tag='dataOrigin').render(request)


def fancy_tree_material_type(request):
    return FancyTreeModule(xml_tag='materialType').render(request)


def fancy_tree_structural_feature(request):
    return FancyTreeModule(xml_tag='structuralFeature').render(request)


def fancy_tree_property_addressed(request):
    return FancyTreeModule(xml_tag='propertyAddressed').render(request)


def fancy_tree_experimental_method(request):
    return FancyTreeModule(xml_tag='experimentalMethod').render(request)


def fancy_tree_characterization_method(request):
    return FancyTreeModule(xml_tag='characterizationMethod').render(request)


def fancy_tree_computational_method(request):
    return FancyTreeModule(xml_tag='computationalMethod').render(request)


def fancy_tree_compute_scale(request):
    return FancyTreeModule(xml_tag='computeScale').render(request)


def fancy_tree_synthesis_processing(request):
    return FancyTreeModule(xml_tag='synthesisProcessing').render(request)
