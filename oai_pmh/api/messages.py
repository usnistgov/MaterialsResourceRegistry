################################################################################
#
# Class Name: messages
#
# Description:   Serializer for OAI-PMH Registries
#
# Author: Pierre Francois RIGODIAT
#         pierre-francois.rigodiat@nist.gov
#
################################################################################


class APIMessage:
    label = 'message'
    errors = 'errors'

    @staticmethod
    def getMessageLabelled(message):
        return {APIMessage.label: message}

    @staticmethod
    def getMessageSerializeLabelled(message, errors=[]):
        return {APIMessage.label: message, APIMessage.errors: errors}