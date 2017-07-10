################################################################################
#
# File Name: tests.py
# Application: xerces_server
# Purpose:
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

import zmq
import time
import json

SERVER_ENDPOINT = "tcp://127.0.0.1:5555"

context = zmq.Context(7)
socket = context.socket(zmq.REP)
socket.bind(SERVER_ENDPOINT)


def _xerces_exists():
    """
    Check if xerces wrapper is installed
    :return:
    """
    try:
        __import__('xerces_wrapper')
    except ImportError:
        print "XERCES DOES NOT EXIST"
        return False
    else:
        print "XERCES EXISTS"
        return True


def _xerces_validate_xsd(xsd_string):
    """
    Validate schema using Xerces
    :param xsd_string
    :return: errors
    """
    if _xerces_exists():
        import xerces_wrapper
        print "XERCES IMPORTED"
        error = xerces_wrapper.validate_xsd(xsd_string)
        print "SCHEMA validated"
        if len(error) <= 1:
            print "SCHEMA valid"
            error = None

        return error
    else:
        return "Xerces is not installed"


def _xerces_validate_xml(xsd_string, xml_string):
    """
    Validate document using Xerces
    :param xsd_string
    :param xml_string
    :return: errors
    """
    if _xerces_exists():
        import xerces_wrapper
        print "XERCES IMPORTED"
        error = xerces_wrapper.validate_xml(xsd_string, xml_string)
        print "DATA validated"
        if len(error) <= 1:
            print "DATA valid"
            error = None

        return error
    else:
        return "Xerces is not installed"


MUTEX = True
while True:
    if MUTEX:
        #  Wait for next request from client
        message = socket.recv()
        print "Received request"

        try:
            message = json.loads(message)

            response = ''
            # validate data against schema
            if 'xml_string' in message:
                print "VALIDATE XML"
                MUTEX = False
                try:
                    xsd_string = message['xsd_string'].encode('utf-8')
                except:
                    xsd_string = message['xsd_string']
                try:
                    xml_string = message['xml_string'].encode('utf-8')
                except:
                    xml_string = message['xml_string']

                error = _xerces_validate_xml(xsd_string, xml_string)

                if error is None:
                    error = 'ok'

                response = error
            else:
                print "VALIDATE XSD"
                MUTEX = False
                try:
                    xsd_string = message['xsd_string'].encode('utf-8')
                except:
                    xsd_string = message['xsd_string']

                error = _xerces_validate_xsd(xsd_string)

                if error is None:
                    error = 'ok'

                response = error

            print response

            socket.send(str(response))
            MUTEX = True
            print "Sent response"
        except Exception, e:
            print e.message
            pass

    time.sleep(1)
