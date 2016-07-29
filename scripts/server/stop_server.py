################################################################################
#
# File Name: stop_server.py
# Application: scripts
# Purpose: Python script to start a server
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

import os, psutil, argparse, time

def get_list_pid(name=None, arg=None):
    list_pid = []
    for proc in psutil.process_iter():
        try:
            if name is not None and proc.name() == name:
                list_pid.append(proc.pid)
            elif arg is not None and arg in proc.cmdline():
                list_pid.append(proc.pid)
        except:
            pass
    return list_pid

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Stop Server Tool")
    required_arguments = parser.add_argument_group("required arguments")

    # add required arguments
    required_arguments.add_argument('-p',
                                    '--dir',
                                    help='Path to the django project folder',
                                    nargs=1,
                                    required=True)
    parser.add_argument('-l',
                        '--ce',
                        help='Path to Celery (not mandatory if path configured)',
                        nargs=1)

    # parse arguments
    args = parser.parse_args()

    # get required arguments
    dir = args.dir[0]

    # get optional arguments
    if args.ce:
        ce = args.ce[0]
    else:
        ce = 'celery'

    celery = python = mongo = False

    list_pid_mongo = get_list_pid(name="mongod")
    if len(list_pid_mongo) > 0:
        mongo = True

    list_pid_celery = get_list_pid(arg="celery")
    if len(list_pid_celery) > 0:
        celery = True

    list_pid_runserver = get_list_pid(arg="runserver")
    if len(list_pid_runserver) > 0:
        python = error = True

    print "  --------------------Kill processes----------------------"
    if celery:
        os.chdir(dir)
        print "  ----------------------Stop celery----------------------"
        while os.system(ce + " multi stopwait worker -A mgi -l info -Ofair --purge"):
            time.sleep(1)
        print "  -------------------------------------------------------"
    if python:
        print "  ------------------Stop django server-------------------"
        for pid in list_pid_runserver:
            print "Kill process: " + str(pid)
            psutil.Process(pid).kill()
    if mongo:
        print "  ----------------------Kill mongo-----------------------"
        for pid in list_pid_mongo:
            print "Kill process: " + str(pid)
            psutil.Process(pid).kill()