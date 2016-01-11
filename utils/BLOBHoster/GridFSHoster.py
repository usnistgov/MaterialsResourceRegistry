################################################################################
#
# File Name: BLOBHoster.py
# 
# Purpose: BLOBHoster implementation for GridFS communication.
#
# Author: Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from BLOBHoster import BLOBHoster

from pymongo import MongoClient
import gridfs
from urlparse import urlparse
from bson.objectid import ObjectId

class GridFSHoster(BLOBHoster):
    
    def __init__(self, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD, MDCS_URI=None):
        BLOBHoster.__init__(self, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD)        
        
        self.client = MongoClient(self.BLOB_HOSTER_URI)    
        self.db = self.client['mgi']
        self.fs = gridfs.GridFS(self.db)
        
        if MDCS_URI is not None:   
            if len(MDCS_URI) > 0:
                if MDCS_URI[-1] != '/':
                    MDCS_URI = MDCS_URI + '/'
                self.uri = MDCS_URI
            else:
                raise ValueError('MDCS_URI is empty.')
        else:
            raise ValueError('MDCS_URI is not set.')
        
    def get(self, handle):
        #return requests.get(handle) -> needs authentication
        try:
            try:
                url = urlparse(handle)
                blob_id = url.query.split("=")[1]
            except:
                raise ValueError('The handle is not well formed.') 
            if self.fs.exists(ObjectId(blob_id)):
                return self.fs.get(ObjectId(blob_id))
#                 with self.fs.get(ObjectId(blob_id)) as blob:
#                     return blob.read()
            else:
                raise ValueError('id not found')
        except:
            raise ValueError('')
        
    def list(self):
        handles = []
        for blob in self.fs.find():
            handle = self.uri + 'rest/blob?id=' + str(blob._id)
            handles.append(handle)
        return handles
        
    def save(self, blob, filename=None):            
        blob_id = self.fs.put(blob, filename=filename)
        handle = self.uri + 'rest/blob?id=' + str(blob_id)
        return handle    
    
    def delete(self, handle):
        try:
            url = urlparse(handle)
            blob_id = url.query.split("=")[1]
        except:
            raise ValueError('The handle is not well formed.') 
        if self.fs.exists(ObjectId(blob_id)):
            self.fs.delete(ObjectId(blob_id))
            
    def query(self, query):
        BLOBHoster.query(self)
        