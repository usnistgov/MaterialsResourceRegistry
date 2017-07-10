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
	echo 'No argument found. Please provide the IP address of the server.'
	exit 1;
fi

if ! valid_ip $1; then
    echo "Invalid IP address entered. Please provide a correct IP address."
    exit 1;
fi

if [[ ! -d "mgi" ]]; then
    echo "The path is not correct. Please launch the script from the main folder of the project."
    exit 1
fi

path="$(pwd)"
folder="/data/db"
pathdb=$path$folder

echo "--------Stop server--------"
./scripts/server/stop_server_unix.sh -p $path

echo "--------Update project files--------"
git checkout -- .
git pull origin

echo "--------Change IP address to settings.py --------"
sudo sed -i "s@127.0.0.1@$1@g" mgi/settings.py

echo "--------Add the IP address to the mongodb configuration file.--------"
sudo sed -i "s/127.0.0.1/127.0.0.1,$1/" conf/mongodb.conf

echo "--------Add data folder path to the mongodb configuration file.--------"
sudo sed -i "s@dbPath: ../data/db@dbPath: $pathdb@" conf/mongodb.conf

echo "--------Start server--------"
./scripts/server/launch_server_unix.sh -p $path -c conf/mongodb.conf

exit 0;





