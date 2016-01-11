################################################################################
#
# File Name: BLOBHosterFactory.py
# 
# Purpose: BLOB Hoster Factory
# 
#
#
# Author: Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
#         Sharief Youssef
#         sharief.youssef@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from utils.BLOBHoster.DSpaceHoster import DSpaceHoster
from utils.BLOBHoster.GridFSHoster import GridFSHoster

class BLOBHosterFactory(object):
    
    BLOB_HOSTERS = ['DSPACE', 'GRIDFS']
    
    def __init__(self, BLOB_HOSTER=None, BLOB_HOSTER_URI=None, BLOB_HOSTER_USER=None, BLOB_HOSTER_PSWD=None, MDCS_URI=None):
        if BLOB_HOSTER == None:
            self.BLOB_HOSTER = None
        else:
            self.BLOB_HOSTER = str(BLOB_HOSTER).upper()
            
        if BLOB_HOSTER_URI == None:
            self.BLOB_HOSTER_URI = None
        else:            
            self.BLOB_HOSTER_URI = str(BLOB_HOSTER_URI)
            
        if BLOB_HOSTER_USER == None:
            self.BLOB_HOSTER_USER = None
        else:
            self.BLOB_HOSTER_USER = str(BLOB_HOSTER_USER)
            
        if BLOB_HOSTER_PSWD == None:
            self.BLOB_HOSTER_PSWD = None
        else:
            self.BLOB_HOSTER_PSWD = str(BLOB_HOSTER_PSWD)
            
        if MDCS_URI == None:
            self.MDCS_URI = None
        else:
            self.MDCS_URI = str(MDCS_URI)
    
    def createBLOBHoster(self):
        if self.BLOB_HOSTER is not None and self.BLOB_HOSTER in self.BLOB_HOSTERS:
            if self.BLOB_HOSTER == self.BLOB_HOSTERS[0]:
                return self.createDSpaceHoster()
            elif self.BLOB_HOSTER == self.BLOB_HOSTERS[1]:
                return self.createGridFSHoster()
        else:
            raise ValueError('BLOB_HOSTER should take a value in ' + str(self.BLOB_HOSTERS))
    
    def createDSpaceHoster(self):
        if self.BLOB_HOSTER_URI is not None and self.BLOB_HOSTER_USER is not None and self.BLOB_HOSTER_PSWD is not None:
            return DSpaceHoster(self.BLOB_HOSTER_URI, self.BLOB_HOSTER_USER, self.BLOB_HOSTER_PSWD)
        else:
            raise ValueError('BLOB_HOSTER_URI, BLOB_HOSTER_USER and BLOB_HOSTER_PSWD should be set.')
    
    def createGridFSHoster(self):
        if self.BLOB_HOSTER_URI is not None and self.BLOB_HOSTER_USER is not None and self.BLOB_HOSTER_PSWD is not None:
            return GridFSHoster(self.BLOB_HOSTER_URI, self.BLOB_HOSTER_USER, self.BLOB_HOSTER_PSWD, self.MDCS_URI)
        else:
            raise ValueError('BLOB_HOSTER_URI, BLOB_HOSTER_USER and BLOB_HOSTER_PSWD should be set.')
    
    
    
    