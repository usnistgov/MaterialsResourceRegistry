################################################################################
#
# File Name: BLOBHoster.py
# 
# Purpose: BLOBHoster implementation for DSpace communication.
#
# Author: Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from BLOBHoster import BLOBHoster
    
class DSpaceHoster(BLOBHoster):
    
    def __init__(self, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD):
        BLOBHoster.__init__(self, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD)

    def get(self, handle):
        BLOBHoster.get(self)
        
    def list(self):
        BLOBHoster.list(self)
        
    def save(self, blob, filename=None):
        BLOBHoster.save(self)
    
    def delete(self, handle):
        BLOBHoster.delete(self)
        
    def query(self, query):
        BLOBHoster.query(self)
