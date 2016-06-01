# import unittest
# from utils.BLOBHoster.BLOBHosterFactory import BLOBHosterFactory
# import base64


# FIXME: Reinit these tests
# class TestGridFS(unittest.TestCase):
#     def setUp(self):
#         print "In method ", self._testMethodName
#         BLOB_HOSTER = 'GridFS'
#         BLOB_HOSTER_USER = "mgi_user"
#         BLOB_HOSTER_PSWD = "mgi_password"
#         BLOB_HOSTER_URI = "mongodb://" + BLOB_HOSTER_USER + ":" + BLOB_HOSTER_PSWD + "@localhost/mgi"
#         MDCS_URI = 'http://127.0.0.1:8000'
#
#         blobHosterFactory = BLOBHosterFactory(BLOB_HOSTER, BLOB_HOSTER_URI, BLOB_HOSTER_USER, BLOB_HOSTER_PSWD,
# MDCS_URI)
#         self.blobHoster = blobHosterFactory.createBLOBHoster()
#
#     def testText(self):
#         self.assertEqual(len(self.blobHoster.list()), 0)
#         text = 'test'
#         handle = self.blobHoster.save(text)
#         out = self.blobHoster.get(handle)
#         self.assertEqual(text, out)
#         self.assertEqual(len(self.blobHoster.list()), 1)
#         self.assertEqual(handle in self.blobHoster.list(), True)
#         self.blobHoster.delete(handle)
#         self.assertEqual(len(self.blobHoster.list()), 0)
#
#
#     def testImage(self):
#         self.assertEqual(len(self.blobHoster.list()), 0)
#         with open('Penguins.jpg','rb') as imageFile:
#             handle = self.blobHoster.save(imageFile, filename='Penguins.jpg')
#
#         out = self.blobHoster.get(handle)
#
#         with open("Penguins.out.jpg", "wb") as imageFile:
#             out.write(imageFile)
#
#         self.assertEqual(len(self.blobHoster.list()), 1)
#         self.blobHoster.delete(handle)
#         self.assertEqual(len(self.blobHoster.list()), 0)
#
#     def testList(self):
#         self.assertEqual(len(self.blobHoster.list()), 0)
#         text = 'test'
#         savedHandles = []
#         for i in range(1,10):
#             handle = self.blobHoster.save(text)
#             savedHandles.append(handle)
#             self.assertEqual(len(self.blobHoster.list()), i)
#             self.assertEqual(handle in self.blobHoster.list(), True)
#
#         for handle in savedHandles:
#             self.blobHoster.delete(handle)
#
#         self.assertEqual(len(self.blobHoster.list()), 0)
#
#     def testDelete(self):
#         self.assertEqual(len(self.blobHoster.list()), 0)
#         text = 'test'
#         handle = self.blobHoster.save(text)
#         self.assertEqual(len(self.blobHoster.list()), 1)
#         self.blobHoster.delete(handle)
#         self.assertEqual(len(self.blobHoster.list()), 0)
        
#     def testInt(self):              
#         self.assertEqual(len(self.blobHoster.list()), 0)
#         text = 3     
#         self.blobHoster.save(text)        
        
# if __name__ == '__main__':
#     unittest.main()
