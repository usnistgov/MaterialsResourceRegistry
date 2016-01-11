################################################################################
#
# File Name: models.py
# Application: exporter/json
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

from exporter.builtin.models import Exporter
import lxml.etree as etree
import os
import json
import xmltodict

def postprocessor(path, key, value):
        if(key == "#text"):
            return key, str(value)
        try:
            return key, int(value)
        except (ValueError, TypeError):
            try:
                return key, float(value)
            except (ValueError, TypeError):
                return key, value

class JSONExporter(Exporter):
    """
    JSON Exporter. Allows to transform a XML document to JSON file
    """
    def __init__(self):
        self.name = "JSON"
        self.extension= ".json"

    def _transform(self, results):
        """
            Method: Implement the abstract method.
            Outputs: Returns a list of results (title, content)
        """
        returnTransformation = []
        try:
            for result in results:
                xml = result['content']
                if xml != "":
                    #We remove the extension
                    result['title'] = os.path.splitext(result['title'])[0]
                    try:
                        #Parse the XML
                        contentEncoded = xmltodict.parse(xml,postprocessor=postprocessor)
                        #Transform to JSON
                        transformation = json.dumps(contentEncoded, indent=4)
                        returnTransformation.append({'title':result['title'], 'content': transformation})
                    except etree.ParseError as e:
                        raise
                    except:
                        raise
        except etree.ParseError as e:
            raise
        except:
            raise

        return returnTransformation




