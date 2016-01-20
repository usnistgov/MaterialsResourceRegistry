################################################################################
#
# File Name: models.py
# Application: exporter/graph
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
from cStringIO import StringIO
import matplotlib.pyplot as plt


class GRAPHExporter(Exporter):
    """
    Graph Exporter. Allows to transform a XML document to several graph
    Works for demo.diffusion schema
    """
    def __init__(self):
        self.name = "GRAPH"
        self.extension= ".png"

    def _transform(self, results):
        """
            Method: Implement the abstract method.
            Outputs: Returns a list of results (title, content)
        """
        returnTransformation = []
        percentage = 0.3
        try:
            for result in results:
                xml = result['content'].encode('utf-8')
                if xml != "":
                    #We remove the extension
                    result['title'] = os.path.splitext(result['title'])[0]
                    try:
                        root = etree.XML(xml)
                        tables = root.xpath(".//profile/table")

                        for table in tables:
                            #We retrieve the X axis. Column with id=0
                            labelX = table.find("./headers/column[@id='0']").text
                            x = table.xpath("./rows/row/column[@id='0']")
                            x = [float(value.text) for value in iter(x)]
                            columns = table.xpath("./headers/column[not(@id='0')]")
                            for column in columns:
                                plt.xlabel(labelX)
                                label = column.text
                                id = column.attrib['id']
                                plt.ylabel(label)
                                y = table.xpath("./rows/row/column[@id='"+id+"']")
                                y = [float(value.text) for value in iter(y)]
                                plt.plot(list(x), list(y), marker='+', mec='b', mew=1, linestyle='--', color='r', lw=0.4)
                                plt.grid(True)
                                fig = plt.gcf()
                                imgdata = StringIO()
                                fig.savefig(imgdata, format='png')
                                plt.close()
                                # rewind the data
                                imgdata.seek(0)
                                returnTransformation.append({'title':result['title']+"_"+str(id), 'content': imgdata.read()})
                                imgdata.close()
                    except etree.ParseError as e:
                        raise
                    except:
                        raise
        except etree.ParseError as e:
            raise
        except:
            raise

        return returnTransformation




