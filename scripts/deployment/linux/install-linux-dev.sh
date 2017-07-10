#!/bin/bash
#sudo apt-get install git
#git clone $address

if [[ ! -d "docs" ]]; then
    echo "--------The path is not correct. Please launch the script from the main folder of the project.--------"
    exit 1
fi

sudo apt-get update

echo "--------Install needed packages: sudo apt-get install libxml2-dev libxslt1-dev python2.7-dev zlib1g-dev --------"
sudo apt-get install libxml2-dev libxslt1-dev python2.7-dev zlib1g-dev

echo "--------Install pip: curl https://bootstrap.pypa.io/get-pip.py > get-pip.py --------"
curl https://bootstrap.pypa.io/get-pip.py > get-pip.py

echo "--------Install pip: python get-pip.py --------"
sudo python get-pip.py
sudo rm get-pip.py

echo "--------Install mongoDB --------"
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
echo "deb http://repo.mongodb.org/apt/ubuntu "$(lsb_release -sc)"/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
sudo apt-get update
sudo apt-get install mongodb-org

PROC="$(pgrep mongod)"
if [[ -n $PROC ]]; then
	echo "--------MongoDB is already running. Kill the process. --------"
	sudo pkill -TERM mongod
fi

echo "--------Install Redis Server: sudo apt-get install redis-server --------"
sudo apt-get install redis-server

echo "--------Install all required packages: sudo pip install -r docs/requirements.txt --------"
sudo pip install -r docs/requirements.txt

exit 0;