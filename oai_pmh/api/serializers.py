################################################################################
#
# Class Name: RegistrySerializer
#
# Description:   Serializer for OAI-PMH Registries
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
################################################################################

from rest_framework import serializers
from rest_framework_mongoengine.serializers import MongoEngineModelSerializer
from mgi.models import OaiRegistry, OaiSettings

class RegistrySerializer(MongoEngineModelSerializer):
    class Meta:
        model = OaiRegistry
        exclude = (['identity', 'metadataformats', 'sets', 'description', 'name'])

class UpdateRegistrySerializer(serializers.Serializer):
    id  = serializers.CharField(required=True)
    harvestrate = serializers.IntegerField(required=True)
    harvest = serializers.BooleanField(required=True)

class RegistryIdSerializer(serializers.Serializer):
    RegistryId = serializers.CharField(required=True)

class AddRegistrySerializer(serializers.Serializer):
    url = serializers.CharField(required=True)
    harvestrate = serializers.IntegerField(required=True)
    harvest = serializers.BooleanField(required=True)

class UpdateRegistryHarvestSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    metadataFormats = serializers.CharField(required=True)
    sets = serializers.CharField(required=False)

class ListRecordsSerializer(serializers.Serializer):
    url  = serializers.URLField(required=True)
    metadataprefix = serializers.CharField(required=False)
    set = serializers.CharField(required=False)
    resumptionToken = serializers.CharField(required=False)
    fromDate = serializers.CharField(required=False)
    untilDate  = serializers.CharField(required=False)

class RegistryURLSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    metadataprefix = serializers.CharField(required=True)
    set = serializers.CharField(required=False)
    fromDate = serializers.DateField(required=False)
    untilDate = serializers.DateField(required=False)

class RecordSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    datestamp = serializers.CharField()
    deleted = serializers.BooleanField()
    sets = serializers.CharField()
    metadataPrefix = serializers.CharField()
    metadata = serializers.CharField()
    raw = serializers.CharField()

class GetRecordSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    identifier = serializers.CharField(required=True)
    metadataprefix = serializers.CharField(required=True)

class IdentifySerializer(serializers.Serializer):
    url = serializers.URLField(required=True)

class IdentifyObjectSerializer(serializers.Serializer):
    adminEmail = serializers.CharField(required=False)
    baseURL = serializers.URLField(required=True)
    repositoryName = serializers.CharField(required=False)
    deletedRecord = serializers.CharField(required=False)
    delimiter = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    earliestDatestamp = serializers.CharField(required=False)
    granularity = serializers.CharField(required=False)
    oai_identifier = serializers.CharField(required=False)
    protocolVersion = serializers.CharField(required=False)
    repositoryIdentifier = serializers.CharField(required=True)
    sampleIdentifier = serializers.CharField(required=False)
    scheme = serializers.CharField(required=False)
    raw = serializers.CharField(required=False)

class SetSerializer(serializers.Serializer):
    setName = serializers.CharField()
    setSpec = serializers.CharField()
    raw = serializers.CharField()

class MetadataFormatSerializer(serializers.Serializer):
    metadataPrefix = serializers.CharField()
    metadataNamespace = serializers.CharField()
    schema = serializers.CharField()
    raw = serializers.CharField()

class UpdateMyRegistrySerializer(serializers.Serializer):
    repositoryName = serializers.CharField(required=True)
    enableHarvesting = serializers.BooleanField(required=True)

class MyMetadataFormatSerializer(serializers.Serializer):
    metadataPrefix = serializers.CharField(required=True)
    schema = serializers.CharField(required=True)

class MyTemplateMetadataFormatSerializer(serializers.Serializer):
    metadataPrefix = serializers.CharField(required=True)
    template = serializers.CharField(required=True)

class DeleteMyMetadataFormatSerializer(serializers.Serializer):
    MetadataFormatId  = serializers.CharField(required=True)

class MySetSerializer(serializers.Serializer):
    setSpec = serializers.CharField(required=True)
    setName = serializers.CharField(required=True)
    templates = serializers.CharField(required=True)
    description = serializers.CharField(required=False)

class DeleteMySetSerializer(serializers.Serializer):
    set_id  = serializers.CharField(required=True)

class UpdateMyMetadataFormatSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    metadataPrefix = serializers.CharField(required=True)

class UpdateMySetSerializer(serializers.Serializer):
    id = serializers.CharField(required=True)
    setSpec = serializers.CharField(required=True)
    setName = serializers.CharField(required=True)
    description = serializers.CharField(required=False)
    templates = serializers.CharField(required=False)

class DeleteXSLTSerializer(serializers.Serializer):
    xslt_id = serializers.CharField(required=True)

class EditXSLTSerializer(serializers.Serializer):
    xslt_id = serializers.CharField(required=True)
    name = serializers.CharField(required=True)

class OaiConfXSLTSerializer(serializers.Serializer):
    template_id = serializers.CharField(required=True)
    my_metadata_format_id = serializers.CharField(required=True)
    xslt_id = serializers.CharField(required=False)
    activated = serializers.CharField(required=True)

class OaiXSLTSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    filename = serializers.CharField(required=True)
    content = serializers.CharField(required=True)

class ListIdentifierSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    setSpecs = serializers.CharField(required=True)
    datestamp = serializers.CharField(required=True)

class HarvestSerializer(serializers.Serializer):
    registry_id = serializers.CharField(required=True)

class UpdateRegistryInfo(serializers.Serializer):
    registry_id = serializers.CharField(required=True)