################################################################################
#
# File Name: models.py
# Application: exporter/builtin
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

class XSLTExporter(Exporter):
    """
    XSLT Exporter. Allows to transform a XML document with a XSLT file.
    """

    def __init__(self, xslt=""):
        """
            Method: Initialisation. Sets the exporter name and assigns the xslt given in parameter
            Outputs: -
        """
        self.name = "XSLT"
        if xslt != "":
            self._setXslt(xslt)

    def _setXslt(self, xslt):
        """
            Method: Set the XSLT to use for the transformation.
            Outputs: -
        """
        self.xslt = xslt
        #Default extension
        self.extension= "xml"

        xsltParsed = etree.parse(BytesIO(xslt.encode('utf-8')))
        #We define the extension
        try:
            method = xsltParsed.find("//xsl:output",namespaces={'xsl': 'http://www.w3.org/1999/XSL/Transform'}).attrib['method']
            self.extension = ".{!s}".format(method)
        except:
            pass

        self.transform = etree.XSLT(xsltParsed)

    def _transform(self, results):
        """
            Method: Implement the abstract method. Transforms each result thanks to the XSLT.
            Outputs: Returns a list of results (title, content)
        """
        resultsTransform = []

        if self.xslt != "":
            for result in results:
                xml = result['content']
                if xml != "":
                    try:
                        dom = etree.XML(xml.encode('utf-8'))
                        #Transformation
                        newdom = self.transform(dom)
                        resultsTransform.append({'title':result['title'], 'content': str(newdom)})
                    except etree.ParseError as e:
                        raise
                    except:
                        raise

        return resultsTransform


class BasicExporter(Exporter):
    """
    BasicExporter. Allows to get the XML file without any transformations
    """
    def __init__(self):
        self.name = "XML"
        self.extension = ".xml"

    def _transform(self, results):
        return results



