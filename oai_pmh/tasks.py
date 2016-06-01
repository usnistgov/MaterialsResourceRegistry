from __future__ import absolute_import
from logging import getLogger
from mgi.models import OaiRegistry
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
OAI_HOST_URI = settings.OAI_HOST_URI
OAI_USER = settings.OAI_USER
OAI_PASS = settings.OAI_PASS
import requests
from mgi.celery import app
from django.core.urlresolvers import reverse
import datetime
logger = getLogger(__name__)
import json
from oai_pmh.api.messages import APIMessage


def init_harvest():
    #Kill all tasks
    purge_all_tasks()
    #Init all registry isQueued to False in case of a server reboot after an issue
    registries = OaiRegistry.objects(isDeactivated=False).all()
    for registry in registries:
        registry.isQueued = False
        registry.save()

    #Check every X seconds if a registry need to be harvested
    watch_harvest_task.apply_async()

@app.task
def watch_harvest_task():
    registries = OaiRegistry.objects(isDeactivated=False).all()
    message = "No new registries need to be updated and harvested"
    #We launch the backround task for each registry
    for registry in registries:
        #If we need to harvest and a task doesn't already exist for this registry
        if registry.harvest and not registry.isQueued:
            message = message + "Registry {!s} need to be updated and harvested.".format(registry.name)
            task = harvest_task.apply_async((str(registry.id),))
            registry.isQueued = True
            registry.save()

    #Periodic call every X seconds
    watch_harvest_task.apply_async(countdown=10)
    return message

@app.task
def harvest_task(registryId):
    message = ""
    try:
        #Get the registry
        registry = OaiRegistry.objects.get(pk=registryId)
        #Update registry
        if not registry.isUpdating:
            update_message = update_registry(registryId, registry.name)
            message = "Date: {!s}, Registry {!s} has been updated"\
               "Update Message: {!s}".format(datetime.datetime.now(), registry.name, update_message)
        if registry.harvest and not registry.isHarvesting:
            harvest_message = harvest_registry(registryId, registry.name)
            message = message + "Date: {!s}, Registry {!s} has been harvested. " \
                "Harvest Message: {!s}".format(datetime.datetime.now(), registry.name, harvest_message)

        #New update in harvestrate seconds
        harvest_task.apply_async((registryId,), countdown=registry.harvestrate)
        return message

    except Exception as e:
        return e.message


################################################################################
#
# Function Name: purge_all_tasks(request)
# Inputs:        request -
# Outputs:       -
# Exceptions:    None
# Description:   Purge all waiting tasks
#
################################################################################
#TODO Not working
def purge_all_tasks():
    app.control.purge()


################################################################################
#
# Function Name: update_registry(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Check OAI Error and Exception - Illegal and required arguments
#
################################################################################
def update_registry(registryId, registryName):
     try:
        #Update the registry information
        uri= OAI_HOST_URI + reverse("api_update_registry_info")
        # Call the API to update registry information
        req = requests.put(uri, {"registry_id": registryId}, auth=(OAI_USER, OAI_PASS))
        data = json.loads(req.text)
        return "Date: {!s}, Registry: {!s}, Message: {!s}, Status code: {!s}".format(datetime.datetime.now(),registryName,
                                                                            data[APIMessage.label], str(req.status_code))
     except Exception as e:
        return e.message

################################################################################
#
# Function Name: harvest_registry(request)
# Inputs:        request -
# Outputs:       An XML Schema
# Exceptions:    None
# Description:   Check OAI Error and Exception - Illegal and required arguments
#
################################################################################
def harvest_registry(registryId, registryName):
    try:
        #Get the uri
        uri= OAI_HOST_URI + reverse("api_harvest")
        # Call the API to harvest records
        req = requests.post(uri,
                           {"registry_id": registryId},
                           auth=(OAI_USER, OAI_PASS))
        data = json.loads(req.text)
        return "Date: {!s}, Registry: {!s}, Message: {!s}, Status code: {!s}".format(datetime.datetime.now(),registryName,
                                                                            data[APIMessage.label], str(req.status_code))
    except Exception as e:
        return e.message
