#!/bin/bash

function valid_ip()
{
    local  ip=$1
    local  stat=1

    if [[ $ip =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
        OIFS=$IFS
        IFS='.'
        ip=($ip)
        IFS=$OIFS
        [[ ${ip[0]} -le 255 && ${ip[1]} -le 255 \
            && ${ip[2]} -le 255 && ${ip[3]} -le 255 ]]
        stat=$?
    fi
    return $stat
}

# Check if there is no argument
if [[ -z $* ]]; then
	echo '--------No argument found. Please provide the IP address of the server.--------'
	exit 1;
fi

if ! valid_ip $1; then
    echo "--------Invalid IP address entered. Please provide a correct IP address.--------"
    exit 1;
fi

if [[ ! -d "scripts" ]]; then
    echo "--------The path is not correct. Please launch the script from the main folder of the project.--------"
    exit 1
fi

PROC="$(pgrep mongod)"
if [[ -n $PROC ]]; then
	echo "--------MongoDB is already running. Kill the process.--------"
	sudo pkill -TERM mongod
fi

echo "--------Create data folder--------"
mkdir -p data/db

folder="/data/db"
pathdb=$(pwd)$folder

echo "--------Add the IP address to the mongodb configuration file.--------"
sudo sed -i "s/127.0.0.1/127.0.0.1,$1/" conf/mongodb.conf

echo "--------Add data folder path to the mongodb configuration file.--------"
sudo sed -i "s@dbPath: ../data/db@dbPath: $pathdb@" conf/mongodb.conf

echo "--------Change IP address to settings.py--------"
sudo sed -i "s@127.0.0.1@$1@g" mgi/settings.py

echo "--------Remove the start on boot for MongoDB.--------"
sudo sed -i "s@\"yes\"@\"no\"@" /etc/init/mongod.conf

echo "--------Start MongoDB: mongod --config conf/mongodb.conf & --------"
mongod --config conf/mongodb.conf &
count=0
until nc -zv localhost 27017;
do
    ((count++))
	sleep 1;
	if [ $count -ge 5 ]; then
	    echo "Error: MongoDB is not starting correctly."
	    exit 1
	fi
done

echo "--------Create admin user on mongodb: mongo < scripts/deployment/resources/bddAdmin.js--------"
mongo < scripts/deployment/resources/bddAdmin.js

echo "--------Connect to the database as admin and create database MGI: mongo --port 27017 -u admin -p admin --authenticationDatabase admin < scripts/deployment/resources/bddMGI.js --------"
mongo --port 27017 -u admin -p admin --authenticationDatabase admin < scripts/deployment/resources/bddMGI.js

echo "--------Migrate: python manage.py migrate--------"
python manage.py migrate
echo "--------Create superuser: python manage.py createsuperuser--------"
python manage.py createsuperuser

PROC="$(pgrep mongod)"
if [[ -n $PROC ]]; then
	echo "--------MongoDB is running. Kill the process.--------"
	sudo pkill -TERM mongod
fi

exit 0;