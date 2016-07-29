################################################################################
#
# File Name: BLOBHoster.py
# 
# Purpose: Abstract class for communication with BLOB Hoster.
#          Interface that BLOBHosters should implement
#
# Author: Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from abc import ABCMeta, abstractmethod


class BLOBHoster(object):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD):
        self.BLOB_HOSTER_URI = BLOB_HOSTER_URI
        self.BLOB_HOSTER_USER = BLOB_HOSTER_USER
        self.BLOB_HOSTER_PSWD = BLOB_HOSTER_PSWD
    
    @abstractmethod
    def save(self, blob, filename):
        # data is str or binaries
        # returns an URI
        raise NotImplementedError("This method is not implemented.")
    
    @abstractmethod    
    def get(self, handle):
        # returns a BLOB (str or binaries)
        raise NotImplementedError("This method is not implemented.")
    
    @abstractmethod    
    def list(self):
        # returns a list of URIs 
        raise NotImplementedError("This method is not implemented.")
    
    @abstractmethod    
    def query(self, query):
        # returns a list of URIs 
        raise NotImplementedError("This method is not implemented.")
    
    @abstractmethod    
    def delete(self, handle):
        # deletes data pointed by the handle
        raise NotImplementedError("This method is not implemented.")

    @abstractmethod
    def find(self, key, value):
        # returns a list of files filtered
        raise NotImplementedError("This method is not implemented.")
        