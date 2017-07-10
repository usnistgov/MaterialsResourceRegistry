#!/bin/bash
PROJ='mgi'
PYTHON='python'
CELERY='celery'

usage()
{
	echo "  ---------------------------------------------------------------------"
	echo " | stop_server_unix [options]                                          |"
	echo " |                                                                     |"
	echo " |       Options:                                                      |"
	echo " |                                                                     |"
    echo " |  -p  | --dir   : path to the django project (mandatory)             |"
	echo " |  -l  | --ce    : path to celery (not mandatory if path configured)  |"
	echo " |  -h  | --help  : help                                               |"
	echo " |                                                                     |"
	echo "  ---------------------------------------------------------------------"
	exit -1;
}

# Check if there is -h or --help argument
for arg do
	case $arg in
		-h|--help)
	    	usage
		;;
	esac
done

# Check the other arguments
while [ $# -gt 1 ]
do
	key=$1
	case $key in
	    -p|--dir)
	    PATH_TO_PROJECT=$2
	    shift # past argument
	    ;;
	    -l|--ce)
	    CELERY=$2
	    shift # past argument
	    ;;
	esac
shift # past argument or value
done

if [[ -z $PATH_TO_PROJECT ]]; then
	  echo 'Path to django project folder is mandatory. Use --help if needed'
	  exit -1;
fi

# Launch server
cd $PATH_TO_PROJECT

#STOP
echo "  ----------------------Stop celery----------------------"
until $CELERY multi stopwait worker -A $PROJ -l info -Ofair --purge;
do
	sleep 1;
done
echo "  ------------------Stop django server-------------------"
sudo pkill -TERM -f runserver
echo "  ----------------------Stop mongo-----------------------"
sudo pkill -TERM mongod

exit 0;