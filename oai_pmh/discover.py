################################################################################
#
# File Name: discover.py
# Purpose:
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from django.conf import settings
from mgi.models import OaiSettings, OaiMyMetadataFormat, Template, OaiMySet, OaiRegistry, ResultXslt
from lxml import etree
from lxml.etree import XMLSyntaxError
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
SITE_ROOT = settings.SITE_ROOT
OAI_HOST_URI = settings.OAI_HOST_URI
from django.core.urlresolvers import reverse

def init_settings():
    """
    Init settings for the OAI-PMH feature.
    Set the name, identifier and the harvesting information
    """
    try:
        #Get OAI-PMH settings information about this server
        information = OaiSettings.objects.all()
        #If we don't have settings in database, we have to initialize them
        if not information:
            OaiSettings(repositoryName = settings.OAI_NAME, repositoryIdentifier = settings.OAI_REPO_IDENTIFIER,
                        enableHarvesting= False).save()

    except Exception, e:
        print('ERROR : Impossible to init the settings : ' + e.message)


def load_metadata_prefixes():
    """
    Load default metadata prefixes for OAI-PMH
    """
    metadataPrefixes = OaiMyMetadataFormat.objects.all()
    if len(metadataPrefixes) == 0:
        #Add OAI_DC metadata prefix
        schemaURL = "http://www.openarchives.org/OAI/2.0/oai_dc.xsd"
        file = open(os.path.join(SITE_ROOT, 'oai_pmh', 'resources', 'xsd', 'oai_dc.xsd'),'r')
        xsdContent = file.read()
        dom = etree.fromstring(xsdContent.encode('utf-8'))
        if 'targetNamespace' in dom.find(".").attrib:
            metadataNamespace = dom.find(".").attrib['targetNamespace'] or "namespace"
        else:
            metadataNamespace = "http://www.w3.org/2001/XMLSchema"
        OaiMyMetadataFormat(metadataPrefix='oai_dc',
                            schema=schemaURL,
                            metadataNamespace=metadataNamespace,
                            xmlSchema=xsdContent,
                            isDefault=True).save()
        #Add NMRR templates as metadata prefixes
        templates = {
            'all': {'path': 'res-md.xsd', 'metadataPrefix': 'oai_all'},
            'organization': {'path': 'res-md.xsd', 'metadataPrefix': 'oai_org'},
            'datacollection': {'path': 'res-md.xsd', 'metadataPrefix': 'oai_datacol'},
            'repository': {'path': 'res-md.xsd', 'metadataPrefix': 'oai_repo'},
            'projectarchive': {'path': 'res-md.xsd', 'metadataPrefix': 'oai_proj'},
            'database': {'path': 'res-md.xsd', 'metadataPrefix': 'oai_database'},
            'dataset': {'path': 'res-md.xsd', 'metadataPrefix': 'oai_dataset'},
            'service': {'path': 'res-md.xsd', 'metadataPrefix': 'oai_serv'},
            'informational': {'path': 'res-md.xsd', 'metadataPrefix': 'oai_info'},
            'software': {'path': 'res-md.xsd', 'metadataPrefix': 'oai_soft'},
        }

        for template_name, info in templates.iteritems():
            try:
                template = Template.objects.get(title=template_name, filename=info['path'])
                #Check if the XML is well formed
                try:
                    xml_schema = template.content
                    dom = etree.fromstring(xml_schema.encode('utf-8'))
                    if 'targetNamespace' in dom.find(".").attrib:
                        metadataNamespace = dom.find(".").attrib['targetNamespace'] or "namespace"
                    else:
                        metadataNamespace = "http://www.w3.org/2001/XMLSchema"
                except XMLSyntaxError:
                    print('ERROR : Impossible to set the template "%s" as a metadata prefix. The template XML is not well formed.'% template_name)
                #Create a schema URL
                schemaURL = OAI_HOST_URI + reverse('getXSD', args=[template.filename])
                #Add in database
                OaiMyMetadataFormat(metadataPrefix=info['metadataPrefix'],
                                   schema=schemaURL,
                                   metadataNamespace=metadataNamespace, xmlSchema='', isDefault=False,
                                   isTemplate=True, template=template).save()
            except Exception, e:
                print('ERROR : Impossible to set the template "{!s}" as a metadata prefix. {!s}'.format(template_name, e.message))


def load_sets():
    """
    Load default metadata prefixes for OAI-PMH
    """
    sets = OaiMySet.objects.all()
    if len(sets) == 0:
        #Add NMRR templates as sets
        templates = {
            'all': {'path': 'res-md.xsd', 'setSpec': 'all', 'setName': 'all', 'description': 'Get all records'},
            'organization': {'path': 'res-md.xsd', 'setSpec': 'org', 'setName': 'organization', 'description': 'Get organization records'},
            'datacollection': {'path': 'res-md.xsd', 'setSpec': 'datacol', 'setName': 'datacollection', 'description': 'Get datacollection records'},
            'repository': {'path': 'res-md.xsd', 'setSpec': 'repo', 'setName': 'repository', 'description': 'Get repository records'},
            'projectarchive': {'path': 'res-md.xsd', 'setSpec': 'proj', 'setName': 'projectarchive', 'description': 'Get projectarchive records'},
            'database': {'path': 'res-md.xsd', 'setSpec': 'database', 'setName': 'database', 'description': 'Get database records'},
            'dataset': {'path': 'res-md.xsd', 'setSpec': 'dataset', 'setName': 'dataset', 'description': 'Get dataset records'},
            'service': {'path': 'res-md.xsd', 'setSpec': 'serv', 'setName': 'service', 'description': 'Get service records'},
            'informational': {'path': 'res-md.xsd', 'setSpec': 'info', 'setName': 'informational', 'description': 'Get informational records'},
            'software': {'path': 'res-md.xsd', 'setSpec': 'soft', 'setName': 'software', 'description': 'Get software records'},
        }

        for template_name, info in templates.iteritems():
            try:
                template = Template.objects.get(title=template_name, filename=info['path'])
                #Add in database
                OaiMySet(setSpec=info['setSpec'], setName=info['setName'], description=info['description'], templates=[template]).save()
            except Exception, e:
                print('ERROR : Impossible to set the template "{!s}" as a set. {!s}'.format(template_name, e.message))


def load_xslt():
    # Add OAI Xslt
    xsltFullName = 'full_demo-oai_pmh'
    xsltFullPath = 'nmrr-full_demo-oai_pmh.xsl'
    xsltDetailName = 'detail_demo-oai_pmh'
    sltDetailPath = 'nmrr-detail_demo-oai_pmh.xsl'

    objFull = ResultXslt.objects(filename=xsltFullPath)
    if not objFull:
        file = open(os.path.join(SITE_ROOT, 'oai_pmh', 'resources', 'xsl', xsltFullPath),'r')
        fileContent = file.read()
        objFull = ResultXslt(name=xsltFullName, filename=xsltFullPath, content=fileContent).save()
        Template.objects().update(set__ResultXsltList=objFull, upsert=True)

    objDetail = ResultXslt.objects(filename=sltDetailPath)
    if not objDetail:
        file = open(os.path.join(SITE_ROOT, 'oai_pmh', 'resources', 'xsl', sltDetailPath),'r')
        fileContent = file.read()
        objDetail = ResultXslt(name=xsltDetailName, filename=sltDetailPath, content=fileContent).save()
        Template.objects().update(set__ResultXsltDetailed=objDetail, upsert=True)

def init_registries_status():
    """
    Init registries status. Avoid a wrong state due to a bad server shutdown
    """
    registries = OaiRegistry.objects.all()
    for registry in registries:
        registry.isUpdating = False
        registry.isHarvesting = False
        registry.save()
