################################################################################
#
# File Name: models.py
# Application: exporter/pop
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

from exporter.models import Exporter
import lxml.etree as etree
from io import BytesIO
import os
import datetime
from django.conf import settings
from dateutil import tz

RESOURCES_PATH = os.path.join(settings.SITE_ROOT, 'exporter/diffusion/pop/resources/')

class POPExporter(Exporter):
    """
    POP Exporter. Allows to transform a XML document to POP file
    Works for demo.diffusion schema
    """
    def __init__(self):
        #Invoke parent constructor
        self.name = "POP"
        self.extension= ".pop"
        self.data = []


    def params(self, context):
    # this is the extension function
        return self.data

    def _transform(self, results):
        """
            Method: Implement the abstract method.
            Outputs: Returns a list of results (title, content)
        """
        transformation = []
        self.data = []
        try:
            for result in results:
                xml = result['content'].encode('utf-8')
                if xml != "":
                    self.data.append(etree.XML(xml))

            #Take the previous file and generate one POP file
            dir = os.path.join(RESOURCES_PATH, 'xslt/xml2pop.xsl')
            xslt = open(dir,'r')
            contentXslt = xslt.read()
            xslt.close()
            #Parse XSLT
            xsltParsed = etree.parse(BytesIO(contentXslt.encode('utf-8')))
            transform = etree.XSLT(xsltParsed)
            #Get current date and time
            from_zone = tz.tzutc()
            to_zone = tz.tzlocal()
            datetimeUTC = datetime.datetime.now().replace(tzinfo=from_zone)
            datetimeLocal = datetimeUTC.astimezone(to_zone)
            now = datetimeLocal.strftime("%m-%d-%Y %I:%M %p")
            #Args
            args = ({"Date": "\""+now+"\""})
            dom = etree.XML(xml)
            ns = etree.FunctionNamespace('uri:params') # register global namespace
            ns['params'] = self.params # define function in new global namespace
            #Transformation with arguments. Used to transmit the date to the XSLT file
            newdom = transform(dom, **(args))
            transformation.append({'title':'Results.pop', 'content': str(newdom)})

        except etree.ParseError as e:
            raise
        except:
            raise


        return transformation




