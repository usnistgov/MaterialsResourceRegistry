################################################################################
#
# File Name: models.py
# Application: exporter/csv
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
from exporter.builtin.models import XSLTExporter
import lxml.etree as etree
import os
import re
from django.conf import settings

RESOURCES_PATH = os.path.join(settings.SITE_ROOT, 'exporter/diffusion/csv/resources/')

class CSVExporter(XSLTExporter):
    """
    CSV Exporter. Allows to transform a XML document to a CSV file thanks to a XSLT file.
    """
    def __init__(self):
        #Invoke parent constructor
        dir = os.path.join(RESOURCES_PATH, 'xslt/xml2csv.xsl')
        xslt = open(dir,'r')
        contentXslt = xslt.read()
        xslt.close()
        super(CSVExporter, self).__init__(contentXslt)
        self.name = "CSV"
        self.extension= ".csv"

    def _transform(self, results):
        """
            Method: Implement the abstract method. Transforms each result thanks to the XSLT.
            Outputs: Returns a list of results (title, content)
        """
        transformation = ""
        returnTransformation = []
        try:
            #Invoke parent transformation
            transformation = super(CSVExporter, self)._transform(results)
            #We generate one file per table
            for result in transformation:
                nb_table = 1;
                xml = result['content']
                if xml != "":
                    #We remove the extension
                    result['title'] = os.path.splitext(result['title'])[0]
                    try:
                        data = xml.split("\t\t\n")
                        data = filter(None, data)
                        if len(data) == 1:
                            returnTransformation.append({'title':result['title'], 'content': str(data[0])})
                        else:
                            for res in data:
                                returnTransformation.append({'title':result['title']+"_Table"+str(nb_table), 'content': str(res)})
                                nb_table += 1
                    except etree.ParseError as e:
                        raise
                    except:
                        raise
        except etree.ParseError as e:
            raise
        except:
            raise

        return returnTransformation




