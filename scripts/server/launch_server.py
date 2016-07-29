################################################################################
#
# File Name: launch_server.py
# Application: scripts
# Purpose: Python script to start a server
#
# Author: Xavier SCHMITT
#         xavier.schmitt@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

import sys, argparse, psutil, os, time
from subprocess import Popen

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

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
    parser = argparse.ArgumentParser(description="Launch Server Tool")
    required_arguments = parser.add_argument_group("required arguments")

    # add required arguments
    required_arguments.add_argument('-p',
                                    '--dir',
                                    help='Path to the django project folder',
                                    nargs=1,
                                    required=True)
    required_arguments.add_argument('-c',
                                    '--mconf',
                                    help='Path to mongoDB configuration file',
                                    nargs=1,
                                    required=True)

    # add optional arguments
    parser.add_argument('-d',
                        '--dport',
                        help='Django server port (8000 if not specified)',
                        nargs=1)
    parser.add_argument('-m',
                        '--mport',
                        help='MongoDB port (27017 if not specified)',
                        nargs=1)
    parser.add_argument('-y',
                        '--py',
                        help='Path to Python (not mandatory if path configured)',
                        nargs=1)
    parser.add_argument('-l',
                        '--ce',
                        help='Path to Celery (not mandatory if path configured)',
                        nargs=1)
    parser.add_argument('-g',
                        '--mo',
                        help='Path to MongoDB (not mandatory if path configured)',
                        nargs=1)

    # parse arguments
    args = parser.parse_args()

    # get required arguments
    dir = args.dir[0]
    mconf = args.mconf[0]

    # get optional arguments
    if args.dport:
        dport = args.dport[0]
    else:
        dport = '8000'

    if args.mport:
        mport = args.mport[0]
    else:
        mport = '27017'

    if args.py:
        py = args.py[0]
    else:
        py = 'python'

    if args.ce:
        ce = args.ce[0]
    else:
        ce = 'celery'

    if args.mo:
        mo = args.mo[0]
    else:
        mo = 'mongod'

    kill_proc = error = celery = python = mongo = False

    list_pid_mongo = get_list_pid(name="mongod")
    if len(list_pid_mongo) > 0:
        mongo = error = True
        print "Error: MongoDB is already running"

    list_pid_celery = get_list_pid(arg="celery")
    if len(list_pid_celery) > 0:
        celery = error = True
        print "Error: Celery is already running"

    list_pid_runserver = get_list_pid(arg="runserver")
    if len(list_pid_runserver) > 0:
        python = error = True
        print "Error: Python server is already running"

    if error:
        print "You have to stop all running processes before launching the yserver."
        if not query_yes_no("Would you like to stop all running processes ?"):
            print "Terminated"
            sys.exit()
        else:
            print "  --------------------Kill processes----------------------"
            if celery:
                os.chdir(dir)
                print "  ----------------------Stop celery----------------------"
                while os.system(ce+" multi stopwait worker -A mgi -l info -Ofair --purge"):
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

    # Launch server
    print "  ----------------------Start server----------------------"
    os.chdir(dir)

    print "  ----------------------Start mongo-----------------------"
    Popen([mo + " --config " + mconf + " --port " + mport + " --quiet", "&", "disown"], shell=True)
    while os.system(" nc -zv localhost " + mport):
        time.sleep(1)

    print "  ---------------------Start celery-----------------------"
    Popen([ce + " multi start -A mgi worker -l info -Ofair --purge", "&", "disown"], shell=True)
    while os.system(ce + " -A mgi status 2>/dev/null"):
        time.sleep(1)

    print "  ---------------------Start python-----------------------"
    Popen([py + " manage.py runserver --noreload 0.0.0.0:" + dport, "&", "disown"], shell=True)