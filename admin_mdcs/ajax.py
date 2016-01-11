################################################################################
#
# File Name: ajax.py
# Application: admin_mdcs
# Purpose:    AJAX methods used for administration purposes
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.http import HttpResponse
import lxml.etree as etree
import json
from io import BytesIO
from mgi.models import Template, TemplateVersion, Instance, Request, Module, Type, TypeVersion, Message, Bucket, MetaSchema, Exporter, ExporterXslt, ResultXslt
from django.contrib.auth.models import User
from utils.XSDflattenerMDCS.XSDflattenerMDCS import XSDFlattenerMDCS
from utils.XSDhash import XSDhash
import random
from utils.APIschemaLocator.APIschemaLocator import getSchemaLocation
from mgi import common


################################################################################
# 
# Function Name: upload_object(request)
# Inputs:        request - 
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Upload of an object (template or type)
# 
################################################################################
def upload_object(request):
    print 'BEGIN def upload_object(request)'

    object_name = request.POST['objectName']
    object_filename = request.POST['objectFilename']
    object_content = request.POST['objectContent']
    object_type = request.POST['objectType']
    
    # Save all parameters
    request.session['uploadObjectName'] = object_name
    request.session['uploadObjectFilename'] = object_filename
    request.session['uploadObjectContent'] = object_content
    request.session['uploadObjectType'] = object_type
    request.session['uploadObjectValid'] = False
    
    xmlTree = None

    response_dict = {}
    # is it a valid XML document ?
    try:            
        xmlTree = etree.parse(BytesIO(object_content.encode('utf-8')))
    except Exception, e:
        response_dict['errors'] = "Not a valid XML document."
        response_dict['message'] = e.message.replace("'","")
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    # is it supported by the MDCS ?
    errors = common.getValidityErrorsForMDCS(xmlTree, object_type)
    if len(errors) > 0:
        errorsStr = ""
        for error in errors:
            errorsStr += error + "<br/>"
        response_dict['errors'] = errorsStr
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    # get the imports
    imports = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}import")
    # get the includes
    includes = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}include")
    
    if len(imports) != 0 or len(includes) != 0:
        # Display array to resolve dependencies
        htmlString = generateHtmlDependencyResolver(imports, includes)
        response_dict['errors'] = htmlString
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    else:
        try:
            # is it a valid XML schema ?
            xmlSchema = etree.XMLSchema(xmlTree)
        except Exception, e:
            response_dict['errors'] = "Not a valid XML schema."
            response_dict['message'] = e.message.replace("'","")
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
        
        request.session['uploadObjectValid'] = True
        return HttpResponse(json.dumps({}), content_type='application/javascript')

    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: save_object(request)
# Inputs:        request - 
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Save an object (template or type) in mongodb
# 
################################################################################
def save_object(request):
    print 'BEGIN def save_object(request)'
    
    objectName = None
    objectFilename = None 
    objectContent = None
    objectType = None
    objectFlat = None
    objectApiurl = None
    
    if ('uploadObjectValid' in request.session and request.session['uploadObjectValid'] == True and
        'uploadObjectName' in request.session and request.session['uploadObjectName'] is not None and
        'uploadObjectFilename' in request.session and request.session['uploadObjectFilename'] is not None and
        'uploadObjectContent' in request.session and request.session['uploadObjectContent'] is not None and
        'uploadObjectType' in request.session and request.session['uploadObjectType'] is not None):    
        objectName = request.session['uploadObjectName']
        objectFilename = request.session['uploadObjectFilename'] 
        objectContent = request.session['uploadObjectContent']
        objectType = request.session['uploadObjectType']      
        if 'uploadObjectFlat' in request.session and request.session['uploadObjectFlat'] is not None:
            objectFlat = request.session['uploadObjectFlat']
        else:
            objectFlat = None
        if 'uploadObjectAPIurl' in request.session and request.session['uploadObjectAPIurl'] is not None:
            objectApiurl = request.session['uploadObjectAPIurl']
        else:
            objectApiurl = None
        if 'uploadDependencies' in request.session and request.session['uploadDependencies'] is not None:
            dependencies = request.session['uploadDependencies']
        else:
            dependencies = None
            
        hash = XSDhash.get_hash(objectContent)
        # save the object
        if objectType == "Template":
            objectVersions = TemplateVersion(nbVersions=1, isDeleted=False).save()
            object = Template(title=objectName, filename=objectFilename, content=objectContent, version=1, templateVersion=str(objectVersions.id), hash=hash).save()
            #We add default exporters
            try:
                exporters = Exporter.objects.filter(available_for_all=True)
                object.exporters = exporters
            except:
                pass
        elif objectType == "Type":                                                                                    
            objectVersions = TypeVersion(nbVersions=1, isDeleted=False).save()
            object = Type(title=objectName, filename=objectFilename, content=objectContent, version=1, typeVersion=str(objectVersions.id), hash=hash).save()
            buckets = request.POST.getlist('buckets[]')
            for bucket_id in buckets:
                bucket = Bucket.objects.get(pk=bucket_id)
                bucket.types.append(str(objectVersions.id))
                bucket.save()
        
        objectVersions.versions = [str(object.id)]
        objectVersions.current = str(object.id)
        objectVersions.save()    
        object.save()
        
        if objectFlat is not None and objectApiurl is not None and dependencies is not None:
            MetaSchema(schemaId=str(object.id), flat_content=objectFlat, api_content=objectApiurl).save()
            object.dependencies = dependencies
            object.save()
            
        clear_object(request)      
    else:
        response_dict = {'errors': 'True'}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: resolve_dependencies(request)
# Inputs:        request - 
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Save an object (template or type) in mongodb
# 
################################################################################
def resolve_dependencies(request):
    print 'BEGIN def resolveDependencies(request)'
    dependencies = request.POST.getlist('dependencies[]')
     
    objectContent = None
    
    response_dict = {}
    if ('uploadObjectName' in request.session and request.session['uploadObjectName'] is not None and
        'uploadObjectFilename' in request.session and request.session['uploadObjectFilename'] is not None and
        'uploadObjectContent' in request.session and request.session['uploadObjectContent'] is not None and
        'uploadObjectType' in request.session and request.session['uploadObjectType'] is not None):    
        objectContent = request.session['uploadObjectContent']
#         contentSession = 'uploadObjectContent'
        validSession = 'uploadObjectValid'
        flatSession = 'uploadObjectFlat'
        apiSession = 'uploadObjectAPIurl'
        saveBtn = "<span class='btn' onclick='saveObject()'>Save</span>"
    elif ('uploadVersionFilename' in request.session and request.session['uploadVersionFilename'] is not None and
        'uploadVersionContent' in request.session and request.session['uploadVersionContent'] is not None):
        objectContent = request.session['uploadVersionContent']
#         contentSession = 'uploadVersionContent'
        validSession = 'uploadVersionValid'
        flatSession = 'uploadVersionFlat'
        apiSession = 'uploadVersionAPIurl'
        saveBtn = "<span class='btn' onclick='saveVersion()'>Save</span>"
    else:
        response_dict= {'errors': "Please upload a file first."}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
         
    xmlTree = etree.parse(BytesIO(objectContent.encode('utf-8')))        
    # get the imports
#     imports = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}import")
     
    # get the includes
    includes = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}include")
     
    idxInclude = 0        
    # replace includes/imports by API calls
    for dependency in dependencies:
        includes[idxInclude].attrib['schemaLocation'] = getSchemaLocation(request, str(dependency))
        idxInclude += 1            
     
#         flattener = XSDFlattenerURL(etree.tostring(xmlTree),'admin','admin')
    flattener = XSDFlattenerMDCS(etree.tostring(xmlTree))
    flatStr = flattener.get_flat()
    flatTree = etree.fromstring(flatStr)
    
    try:
        # is it a valid XML schema ?
        xmlSchema = etree.XMLSchema(flatTree)
#         request.session[contentSession] = etree.tostring(xmlTree)
        request.session[validSession] = True
        
        request.session[flatSession] = flatStr
        request.session[apiSession] = etree.tostring(xmlTree)
        request.session["uploadDependencies"] = dependencies
        message = "The uploaded template is valid. You can now save it." + saveBtn
        response_dict = {'message': message}
    except Exception, e:
        response_dict = {'errorDependencies': e.message.replace("'", "")}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')      

    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: clear_object(request)
# Inputs:        request - 
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Clear variables in the session
# 
################################################################################
def clear_object(request):
    print 'BEGIN def clearObject(request)'
    
    if 'uploadObjectName' in request.session:
        del request.session['uploadObjectName']
    if 'uploadObjectFilename' in request.session:
        del request.session['uploadObjectFilename']
    if 'uploadObjectContent' in request.session: 
        del request.session['uploadObjectContent']
    if 'uploadObjectType' in request.session:
        del request.session['uploadObjectType']
    if 'uploadObjectValid' in request.session:
        del request.session['uploadObjectValid']
    if 'uploadObjectFlat' in request.session:
        del request.session['uploadObjectFlat']
    if 'uploadObjectAPIurl' in request.session:
        del request.session['uploadObjectAPIurl']
    if 'uploadDependencies' in request.session: 
        del request.session['uploadDependencies']
        
    print 'END def clearObject(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: clearVersion(request)
# Inputs:        request - 
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Clear variables in the session
# 
################################################################################
def clearVersion(request):
    print 'BEGIN def clearVersion(request)'
    
    if 'uploadVersionValid' in request.session:
        del request.session['uploadVersionValid']
    if 'uploadVersionID' in request.session:
        del request.session['uploadVersionID']
    if 'uploadVersionType' in request.session: 
        del request.session['uploadVersionType']
    if 'uploadVersionFilename' in request.session:
        del request.session['uploadVersionFilename']
    if 'uploadVersionContent' in request.session:
        del request.session['uploadVersionContent']
    if 'uploadVersionFlat' in request.session:
        del request.session['uploadVersionFlat']
    if 'uploadVersionAPIurl' in request.session:
        del request.session['uploadVersionAPIurl']
    if 'uploadDependencies' in request.session: 
        del request.session['uploadDependencies']

    print 'END def clearVersion(request)'


################################################################################
# 
# Function Name: generateHtmlDependencyResolver(imports, includes)
# Inputs:        request - 
#                imports -
#                includes - 
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Generate an HTML form to resolve dependencies of an uploaded schema
# 
################################################################################
def generateHtmlDependencyResolver(imports, includes):
    # there are includes or imports, need to resolve them
    htmlString = "Please choose a file from the database to resolve each import/include."
    htmlString += "<table id='dependencies'>"
    htmlString += "<tr><th>Import/Include</th><th>Value</th><th>Dependency</th></tr>"
    
    selectDependencyStr = "<select class='dependency'>"
    for type in Type.objects:
        selectDependencyStr += "<option objectid='" + str(type.id) + "'>" + type.title + "</option>"
    selectDependencyStr += "</select>"
    
    for el_include in includes:
        htmlString += "<tr>"
        htmlString += "<td>Include</td>"
        htmlString += "<td><textarea readonly>" + el_include.attrib['schemaLocation'] + "</textarea></td>"
        htmlString += "<td>"+ selectDependencyStr + "</td>"
        htmlString += "</tr>"
        
    htmlString += "</table>"   
    htmlString += "<span class='btn resolve' onclick='resolveDependencies();'>Resolve</span>"
    htmlString += "<div id='errorDependencies'></div>"
    
    return htmlString


################################################################################
# 
# Function Name: delete_object(request)
# Inputs:        request - 
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Delete an object (template or type).
# 
################################################################################
def delete_object(request):
    print 'BEGIN def delete_object(request)'
    object_id = request.POST['objectID']
    object_type = request.POST['objectType']

    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)

    objectVersions.deletedVersions.append(str(object.id))    
    objectVersions.isDeleted = True
    objectVersions.save()

    print 'END def delete_object(request)'
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: set_schema_version_content(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Save the name and content of uploaded schema before save
#
################################################################################
def set_schema_version_content(request):
    version_content = request.POST['versionContent']
    version_filename = request.POST['versionFilename']
    
    request.session['uploadVersionContent'] = version_content
    request.session['uploadVersionFilename'] = version_filename 
    request.session['uploadVersionValid'] = False
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: set_type_version_content(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Save the name and content of uploaded type before save
#
################################################################################
def set_type_version_content(request):
    version_content = request.POST['versionContent']
    version_filename = request.POST['versionFilename']
    
    request.session['uploadVersionContent'] = version_content
    request.session['uploadVersionFilename'] = version_filename
    request.session['uploadVersionValid'] = False
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: upload_version(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Upload the object (template or type)
#
################################################################################
def upload_version(request):
    object_version_id = request.POST['objectVersionID']
    object_type = request.POST['objectType']
    
    response_dict = {}
    
    versionContent = None
    if ('uploadVersionFilename' in request.session and request.session['uploadVersionFilename'] is not None and
        'uploadVersionContent' in request.session and request.session['uploadVersionContent'] is not None):    
        request.session['uploadVersionID'] = object_version_id
        request.session['uploadVersionType'] = object_type
        
        versionContent = request.session['uploadVersionContent'] 
        
        xmlTree = None
        # is it a valid XML document ?
        try:            
            xmlTree = etree.parse(BytesIO(versionContent.encode('utf-8')))
        except Exception, e:
            response_dict['errors'] = "Not a valid XML document."
            response_dict['message'] = e.message.replace("'","")
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
        
        # is it supported by the MDCS ?
        errors = common.getValidityErrorsForMDCS(xmlTree, object_type)
        if len(errors) > 0:
            errorsStr = ""
            for error in errors:
                errorsStr += error + "<br/>"            
            response_dict['errors'] = errorsStr
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
        
        # get the imports
        imports = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}import")
        # get the includes
        includes = xmlTree.findall("{http://www.w3.org/2001/XMLSchema}include")
        
        if len(imports) != 0 or len(includes) != 0:
            # Display array to resolve dependencies
            htmlString = generateHtmlDependencyResolver(imports, includes)
            response_dict['errors'] = htmlString
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
        else:
            try:
                # is it a valid XML schema ?
                xmlSchema = etree.XMLSchema(xmlTree)
            except Exception, e:
                response_dict['errors'] = "Not a valid XML schema."
                response_dict['message'] = e.message.replace("'","")
                return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
            
            request.session['uploadVersionValid'] = True
            return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    else:
        response_dict['errors'] = "Please select a document first."
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: save_version(request)
# Inputs:        request - 
# Outputs:       JSON data 
# Exceptions:    None
# Description:   Save a version of an object (template or type) in mongodb
# 
################################################################################
def save_version(request):
    print 'BEGIN def saveVersion(request, objectType)'
    
    versionFilename = None 
    versionContent = None
    objectVersionID = None
    objectType = None
    
    if ('uploadVersionValid' in request.session and request.session['uploadVersionValid'] == True and
        'uploadVersionID' in request.session and request.session['uploadVersionID'] is not None and
        'uploadVersionType' in request.session and request.session['uploadVersionType'] is not None and
        'uploadVersionFilename' in request.session and request.session['uploadVersionFilename'] is not None and
        'uploadVersionContent' in request.session and request.session['uploadVersionContent'] is not None):    
        versionFilename = request.session['uploadVersionFilename']
        versionContent = request.session['uploadVersionContent'] 
        objectVersionID = request.session['uploadVersionID']
        objectType = request.session['uploadVersionType']
        if 'uploadVersionFlat' in request.session and request.session['uploadVersionFlat'] is not None:
            versionFlat = request.session['uploadVersionFlat']
        else:
            versionFlat = None
        if 'uploadVersionAPIurl' in request.session and request.session['uploadVersionAPIurl'] is not None:
            versionApiurl = request.session['uploadVersionAPIurl']
        else:
            versionApiurl = None  
        if 'uploadDependencies' in request.session and request.session['uploadDependencies'] is not None:
            dependencies = request.session['uploadDependencies']
        else:
            dependencies = None
            
        hash = XSDhash.get_hash(versionContent)
        # save the object
        if objectType == "Template":
            objectVersions = TemplateVersion.objects.get(pk=objectVersionID)
            objectVersions.nbVersions += 1
            object = Template.objects.get(pk=objectVersions.current)            
            newObject = Template(title=object.title, filename=versionFilename, content=versionContent, version=objectVersions.nbVersions, templateVersion=objectVersionID, hash=hash).save()
        elif objectType == "Type":    
            objectVersions = TypeVersion.objects.get(pk=objectVersionID)
            objectVersions.nbVersions += 1
            object = Type.objects.get(pk=objectVersions.current)                                                                                
            newObject = Type(title=object.title, filename=versionFilename, content=versionContent, version=objectVersions.nbVersions, typeVersion=objectVersionID, hash=hash).save()
        
        objectVersions.versions.append(str(newObject.id))
        objectVersions.save()
        
        if versionFlat is not None and versionApiurl is not None and dependencies is not None:
            MetaSchema(schemaId=str(newObject.id), flat_content=versionFlat, api_content=versionApiurl).save()
            object.dependencies = dependencies
            object.save()
           
        clearVersion(request)
    else:    
        response_dict = {'errors': 'True'}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')

    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: set_current_version(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Set the current version of the object (template or type)
#
################################################################################
def set_current_version(request):
    object_id = request.GET['objectid']
    object_type = request.GET['objectType']
    
    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)
    
    objectVersions.current = str(object.id)
    objectVersions.save()
     
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: delete_version(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Delete a version of the object (template or type) by adding it to the list of deleted
#
################################################################################
def delete_version(request):
    object_id = request.POST['objectid']
    object_type = request.POST['objectType']
    new_current = request.POST['newCurrent']
    
    response_dict = {}
    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)
      

    if len(objectVersions.versions) == 1 or len(objectVersions.versions) == len(objectVersions.deletedVersions) + 1:
        objectVersions.deletedVersions.append(str(object.id))    
        objectVersions.isDeleted = True
        objectVersions.save()
        response_dict = {'deleted': 'object'}
    
    else:
        if new_current != "": 
            objectVersions.current = new_current
        objectVersions.deletedVersions.append(str(object.id))   
        objectVersions.save()        
        response_dict = {'deleted': 'version'}
    
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: assign_delete_custom_message(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Assign a message to the dialog box regarding the situation of the version that is about to be deleted
#
################################################################################
def assign_delete_custom_message(request):
    object_id = request.GET['objectid']
    object_type = request.GET['objectType']
    
    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)  
    
    message = ""

    if len(objectVersions.versions) == 1:
        message = "<span style='color:red'>You are about to delete the only version of this " + object_type + ". The " + object_type + " will be deleted from the "+ object_type + " manager.</span>"
    elif objectVersions.current == str(object.id) and len(objectVersions.versions) == len(objectVersions.deletedVersions) + 1:
        message = "<span style='color:red'>You are about to delete the last version of this " + object_type + ". The " + object_type + " will be deleted from the "+ object_type + " manager.</span>"
    elif objectVersions.current == str(object.id):
        message = "<span>You are about to delete the current version. If you want to continue, please select a new current version: <select id='selectCurrentVersion'>"
        for version in objectVersions.versions:
            if version != objectVersions.current and version not in objectVersions.deletedVersions:
                if object_type == "Template":
                    obj = Template.objects.get(pk=version)
                else:
                    obj = Type.objects.get(pk=version)
                message += "<option value='"+version+"'>Version " + str(obj.version) + "</option>"
        message += "</select></span>"

    response_dict = {'message': message}
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: edit_information(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Edit information of an object (template or type)
#
################################################################################
def edit_information(request):
    object_id = request.POST['objectID']
    object_type = request.POST['objectType']
    new_name = request.POST['newName']
    new_filename = request.POST['newFilename']

    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:        
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)
        # check if a type with the same name already exists
        testFilenameObjects = Type.objects(filename=new_filename)    
        if len(testFilenameObjects) == 1: # 0 is ok, more than 1 can't happen
            #check that the type with the same filename is the current one
            if testFilenameObjects[0].id != object.id:
                response_dict = {'errors': 'True'}
                return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    
    # change the name of every version but only the filename of the current
    for version in objectVersions.versions:
        if object_type == "Template":
            obj = Template.objects.get(pk=version)
        else:
            obj = Type.objects.get(pk=version)
        obj.title = new_name
        if version == object_id:
            obj.filename = new_filename
        obj.save()
    
    if object_type == "Type":
        new_buckets = request.POST.getlist('newBuckets[]')
        # update the buckets
        allBuckets = Bucket.objects
        for bucket in allBuckets:
            if str(bucket.id) in new_buckets:
                if str(objectVersions.id) not in bucket.types:
                    bucket.types.append(str(objectVersions.id))
            
            else:   
                if str(objectVersions.id) in bucket.types:
                    bucket.types.remove(str(objectVersions.id))
            
            bucket.save()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: restore_object(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Restore an object previously deleted (template or type)
#
################################################################################
def restore_object(request):
    object_id = request.POST['objectID']
    object_type = request.POST['objectType']
    
    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)
        
    objectVersions.isDeleted = False
    del objectVersions.deletedVersions[objectVersions.deletedVersions.index(objectVersions.current)]
    objectVersions.save()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: restore_version(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   Restore a version of an object previously deleted (template or type)
#
################################################################################
def restore_version(request):
    object_id = request.POST['objectID']
    object_type = request.POST['objectType']
    
    if object_type == "Template":
        object = Template.objects.get(pk=object_id)
        objectVersions = TemplateVersion.objects.get(pk=object.templateVersion)
    else:
        object = Type.objects.get(pk=object_id)
        objectVersions = TypeVersion.objects.get(pk=object.typeVersion)
        
    del objectVersions.deletedVersions[objectVersions.deletedVersions.index(object_id)]
    objectVersions.save()
       
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: edit_instance(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Edit the instance information
#
################################################################################
def edit_instance(request):
    instance_id = request.POST['instanceid']
    name = request.POST['name']
    
    errors = ""
    response_dict = {}
    
    # test if the name is "Local"
    if name.upper() == "LOCAL":
        errors += "By default, the instance named Local is the instance currently running."
    else:   
        # test if an instance with the same name exists
        instance = Instance.objects(name=name)
        if len(instance) != 0 and str(instance[0].id) != instance_id:
            errors += "An instance with the same name already exists.<br/>"
    
    # If some errors display them, otherwise insert the instance
    if errors == "":
        instance = Instance.objects.get(pk=instance_id)
        instance.name = name
        instance.save()
    else:
        response_dict = {'errors': errors}
    
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: delete_instance(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Delete an instance
#
################################################################################
def delete_instance(request):
    instance_id = request.POST['instanceid']
    
    instance = Instance.objects.get(pk=instance_id)
    instance.delete()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: accept_request(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Accepts a request and creates the user account
# 
################################################################################
def accept_request(request):
    request_id = request.POST['requestid']
    
    response_dict = {}
    
    userRequest = Request.objects.get(pk=request_id)
    try:
        existingUser = User.objects.get(username=userRequest.username)
        response_dict = {'errors': 'User already exists.'} 
    except:
        user = User.objects.create_user(username=userRequest.username, password=userRequest.password, first_name=userRequest.first_name, last_name=userRequest.last_name, email=userRequest.email)
        user.save()
        userRequest.delete()
        
    return HttpResponse(json.dumps(response_dict), content_type='application/javascript')


################################################################################
# 
# Function Name: deny_request(request)
# Inputs:        request - 
# Outputs:        
# Exceptions:    None
# Description:   Denies a request
# 
################################################################################
def deny_request(request):
    request_id = request.POST['requestid']
    
    userRequest = Request.objects.get(pk=request_id)
    userRequest.delete()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: remove_message(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Remove a message from Contact form
#
################################################################################
def remove_message(request):
    message_id = request.POST['messageid']
    
    message = Message.objects.get(pk=message_id)
    message.delete()
            
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: add_bucket(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Add a new bucket
#
################################################################################
def add_bucket(request):
    label = request.POST['label']
    
    # check that the label is unique
    labels = Bucket.objects.all().values_list('label') 
    if label in labels:
        response_dict = {"errors": "True"}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    # get an unique color
    colors = Bucket.objects.all().values_list('color') 
    color = rdm_hex_color()
    while color in colors:
        color = rdm_hex_color()
        
    Bucket(label=label, color=color).save()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: delete_bucket(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Delete a bucket
#
################################################################################
def delete_bucket(request):
    bucket_id = request.POST['bucket_id']
    
    bucket = Bucket.objects.get(pk=bucket_id)
    bucket.delete()
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: rdm_hex_color()
# Inputs:        None
# Outputs:       hex color
# Exceptions:    None
# Description:   Generates a random color code
#
################################################################################
def rdm_hex_color():
    return '#' +''.join([random.choice('0123456789ABCDEF') for x in range(6)])


################################################################################
# 
# Function Name: insert_module(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Insert a module in the template by adding an attribute.
#
################################################################################
def insert_module(request):
    module_id = request.POST['moduleID']
    xpath = request.POST['xpath']
    
    defaultPrefix = request.session['moduleDefaultPrefix']
    namespace = request.session['moduleNamespaces'][defaultPrefix]
    template_content = request.session['moduleTemplateContent']
    
    dom = etree.parse(BytesIO(template_content.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix +":", namespace)
    # add the element to the sequence
    element = dom.find(xpath)
    
    module = Module.objects.get(pk=module_id)
        
    element.attrib['{http://mdcs.ns}_mod_mdcs_'] =  module.url
        
    # save the tree in the session
    request.session['moduleTemplateContent'] = etree.tostring(dom) 
    print etree.tostring(element)
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
# 
# Function Name: remove_module(request)
# Inputs:        request -
# Outputs:       
# Exceptions:    None
# Description:   Remove a module from the template by removing an attribute and the automatic namespace.
#
################################################################################
def remove_module(request):
    xpath = request.POST['xpath']
    
    defaultPrefix = request.session['moduleDefaultPrefix']
    namespace = request.session['moduleNamespaces'][defaultPrefix]
    template_content = request.session['moduleTemplateContent']
    
    dom = etree.parse(BytesIO(template_content.encode('utf-8')))
    
    # set the element namespace
    xpath = xpath.replace(defaultPrefix +":", namespace)
    # add the element to the sequence
    element = dom.find(xpath)
    
    if '{http://mdcs.ns}_mod_mdcs_' in element.attrib:
        del element.attrib['{http://mdcs.ns}_mod_mdcs_']
    
    # remove prefix from namespaces
    nsmap = element.nsmap
    for prefix, ns in nsmap.iteritems():
        if ns == 'http://mdcs.ns':
            del nsmap[prefix]
            break
    
    # create a new element to replace the previous one (can't replace directly the nsmap using lxml)
    element = etree.Element(element.tag, nsmap = nsmap);
    
    # save the tree in the session
    request.session['moduleTemplateContent'] = etree.tostring(dom) 
    print etree.tostring(element)
    
    return HttpResponse(json.dumps({}), content_type='application/javascript')
    

################################################################################
#
# Function Name: save_modules(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Save the template with its modules.
#
################################################################################
def save_modules(request):
    template_content = request.session['moduleTemplateContent']
    template_id = request.session['moduleTemplateID']

    template = Template.objects.get(pk=template_id)
    template.content = template_content
    template.save()

    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: save_exporters(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Save exporters and XSLT for a template.
#
################################################################################
def save_exporters(request):
    template_id = request.session['moduleTemplateID']
    listIdOn = request.POST.getlist('listIdOn[]')
    listIdOnXslt = request.POST.getlist('listIdOnXslt[]')
    #We retrieve the exporter
    template = Template.objects.get(pk=template_id)
    #We reinitialise exporters and XSLT
    template.exporters = None
    template.XSLTFiles = None
    template.save()
    #We add exporters
    for exp in listIdOn:
        exp = Exporter.objects.get(pk=exp)
        Template.objects(id=template_id).update_one(push__exporters=exp)
    #We add XSLT files
    for xslt in listIdOnXslt:
        xslt = ExporterXslt.objects.get(pk=xslt)
        Template.objects(id=template_id).update_one(push__XSLTFiles=xslt)
    template.save()

    return HttpResponse(json.dumps({}), content_type='application/javascript')

################################################################################
#
# Function Name: save_result_xslt(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Save result XSLT for a template.
#
################################################################################
def save_result_xslt(request):
    template_id = request.session['moduleTemplateID']
    idXsltShort = request.POST.get('idXsltShort')
    idXsltDetailed = request.POST.get('idXsltDetailed')
    #We retrieve the exporter
    template = Template.objects.get(pk=template_id)
    #We reinitialise exporters and XSLT
    template.ResultXsltList = None
    template.ResultXsltDetailed = None
    template.save()
    #We add short XSLT
    if idXsltShort:
        shortXslt = ResultXslt.objects.get(pk=idXsltShort)
        template.ResultXsltList = shortXslt
    #We add detailed XSLT
    if idXsltDetailed:
        detailedXSLT = ResultXslt.objects.get(pk=idXsltDetailed)
        template.ResultXsltDetailed = detailedXSLT

    if idXsltShort or idXsltDetailed:
        template.save()

    return HttpResponse(json.dumps({}), content_type='application/javascript')


################################################################################
#
# Function Name: check_name(request)
# Inputs:        request -
# Outputs:
# Exceptions:    None
# Description:   Check the name of the template.
#
################################################################################
def check_name(request):
    name = request.POST['name']
    # check that the name is unique
    names = Template.objects.all().values_list('title')
    if name in names:
        response_dict = {'errors': 'True'}
        return HttpResponse(json.dumps(response_dict), content_type='application/javascript')
    return HttpResponse(json.dumps({}), content_type='application/javascript')