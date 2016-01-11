################################################################################
#
# File Name: models.py
# Application: exporter
# Purpose:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
#         Pierre Francois RIGODIAT
#		  pierre-francois.rigodiat@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from abc import ABCMeta, abstractmethod
import os

class Exporter(object):
    """
    Export data to different formats
    This class contains 2 principal methods:
        - transform: transforms a XML to another format
        - transformAndZIp: transforms all XML given in parameter and Zip all
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        """
            Method: Initialisation.
            Outputs: -
        """
        self.name = "Results"
        self.extension= ".xml"


    def _transformAndZip(self, instance, results, zip):
        """
            Method: Calls the specific transform method of the object over all results and creates a Zip file
            Outputs: Zip file in parameter
        """
        resultsTransform = self._transform(results)
        for result in resultsTransform:
            # We check if the extension is already ok
            if self.extension and not result['title'].endswith(self.extension):
                #We remove the extension
                result['title'] = os.path.splitext(result['title'])[0]
                result['title'] += self.extension

            if instance == None:
                path = "{!s}/{!s}".format(self.name,result['title'])
                zip.writestr(path, result['content'].encode('utf-8'))
            else:
                path = "{!s}/{!s} {!s}/{!s}".format(self.name,self.name,instance,result['title'])
                zip.writestr(path, result['content'].encode('utf-8'))

         # fix for Linux zip files read in Windows
        for xmlFile in zip.filelist:
            xmlFile.create_system = 0


    @abstractmethod
    def _transform(self, results):
        """
            Method: Get the convert data
            Outputs: returns the data converted
        """
        raise NotImplementedError("This method is not implemented.")

