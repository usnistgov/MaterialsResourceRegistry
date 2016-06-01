################################################################################
#
# File Name: exceptions.py
# Application: Informatics Core
# Description: All OAI-PMH exceptions
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
ID_DOES_NOT_EXIST = 'idDoesNotExist'
NO_METADATA_FORMAT = 'noMetadataFormat'
NO_RECORDS_MATCH = 'noRecordsMatch'
DISSEMINATE_FORMAT = 'cannotDisseminateFormat'
BAD_ARGUMENT = 'badArgument'
NO_SET_HIERARCHY = 'noSetHierarchy'
BAD_VERB = 'badVerb'
BAD_RESUMPTION_TOKEN = 'badResumptionToken'


class OAIExceptions(Exception):
    def __init__(self, errors):
        self.message = 'Error'
        self.code = 'OAIExceptions'
        self.errors = errors

    def __str__(self):
        return self.errors

class OAIException (Exception):
    def __init__(self):
        self.message = 'Error'
        self.code = 'OAIException'

    def __str__(self):
        return repr(self.message)

class badArgument(OAIException):
    def __init__(self, customMessage):
        if customMessage:
            self.message = customMessage
        else:
            self.message = 'The request includes illegal arguments, is missing required arguments, includes a repeated' \
                        ' argument, or values for arguments have an illegal syntax.'
        self.code = BAD_ARGUMENT

class badResumptionToken(OAIException):
    def __init__(self, resumptionToken):
        self.message = 'The value of the resumptionToken argument (%s) is invalid or expired.' %resumptionToken
        self.code = 'badResumptionToken'

class badVerb(OAIException):
    def __init__(self, message):
        self.message = message
        self.code = BAD_VERB

class cannotDisseminateFormat(OAIException):
    def __init__(self, metadataPrefix):
        self.message = 'The metadata format identified by the value given for the metadataPrefix argument' \
                       ' (%s) is not supported by the item or by the repository.' % metadataPrefix
        self.code = DISSEMINATE_FORMAT

class idDoesNotExist(OAIException):
    def __init__(self, identifier):
        self.message = 'The value of the identifier argument (%s) is unknown or illegal in this repository.' %identifier
        self.code = ID_DOES_NOT_EXIST

class noRecordsMatch(OAIException):
    def __init__(self):
        self.message = 'The combination of the values of the from, until, set and metadataPrefix arguments ' \
                       'results in an empty list.'
        self.code = NO_RECORDS_MATCH

class noMetadataFormat(OAIException):
    def __init__(self):
        self.message = 'There are no metadata formats available for the specified item.'
        self.code = NO_METADATA_FORMAT

class noSetHierarchy(OAIException):
    def __init__(self):
        self.message = 'The repository does not support sets.'
        self.code = NO_SET_HIERARCHY
