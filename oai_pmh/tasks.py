from __future__ import absolute_import
from logging import getLogger
from mgi.models import OaiRegistry
import os
from django.utils.importlib import import_module
settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
settings = import_module(settings_file)
from mgi.celery import app
import datetime
logger = getLogger(__name__)
import json
from oai_pmh.api.messages import APIMessage
from oai_pmh.api.models import update_registry_info as update_registry_info_model, harvest as harvest_model

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
            message = message + "Registry {!s} need to be updated and harvested.".format(registry.name.encode("utf-8"))
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
        #Check if the registry has been deactivated
        if registry.isDeactivated:
            registry.isQueued = False
            registry.save()
            message = "Registry {!s} has been deactivated. No need to harvest it anymore.".format(registry.name.encode("utf-8"))
        else:
            #Update registry
            if not registry.isUpdating:
                update_message = update_registry(registryId)
                message = "Date: {!s}, Registry {!s} has been updated"\
                   "Update Message: {!s}".format(datetime.datetime.now(), registry.name.encode("utf-8"), update_message)
            if registry.harvest and not registry.isHarvesting:
                harvest_message = harvest_registry(registryId)
                message = message + "Date: {!s}, Registry {!s} has been harvested. " \
                    "Harvest Message: {!s}".format(datetime.datetime.now(), registry.name.encode("utf-8"), harvest_message)

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
def update_registry(registryId):
     try:
        #Update the registry information
        req = update_registry_info_model(registryId)
        data = req.data
        return "Message: {!s}, Status code: {!s}".format(data[APIMessage.label], str(req.status_code))

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
def harvest_registry(registryId):
    try:
        #Harvest
        req = harvest_model(registryId)
        data = req.data
        return "Message: {!s}, Status code: {!s}".format(data[APIMessage.label], str(req.status_code))
    except Exception as e:
        return e.message
