# UNIX Installation Instructions

## Prerequisites


### Python
```
$ sudo apt-get install build-essential
$ wget http://www.python.org/ftp/python/2.7.2/Python-2.7.2.tgz
$ tar xzf Python-2.7.2.tgz
$ cd python-2.7.2
$ ./configure
$ make altinstall prefix=~/usr/local exec-prefix=~/usr/local
$ alias python='~/usr/local/bin/python2.7'
```

### pip
```
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
alias pip=~/usr/local/bin/pip
```
Any installed package via pip will now go under your '~/usr/local/lib/python2.7/site-packages' directory.

### (Optional) Virtual Environment
Please follow the [instructions](https://github.com/yyuu/pyenv#installation) to install pyenv
```
$ pyenv install 2.7.2
$ pyenv virtualenv 2.7.2 curator
$ pyenv activate curator
```
Find more details at [pyenv](https://github.com/yyuu/pyenv)

### MongoDB
- Download from https://www.mongodb.com/download-center#community
- Follow the instructions provided by MongoDB to install it

### Redis Server
```
sudo apt-get install redis-server
```

## Setup

### Configure MongoDB
Please follow general instructions provided in the file called "MongoDB Configuration".

### Install required python packages
If you are using a virtual environment, make sure it is activated before starting the installation. 
```
$ pip install -r docs\requirements.txt
```
Install django-mongoengine from GitHub (https://github.com/MongoEngine/django-mongoengine ):
```
git clone https://github.com/MongoEngine/django-mongoengine.git
cd django-mongoengine
python setup.py install
```

#### For lxml
If you get the error “clang error: linker command failed”, then run the following command instead (See http://lxml.de/installation.html):
```
STATIC_DEPS=true pip install lxml==<version>
```

## Run the software for the first time
- Run mongodb (if not already running):
```
$ mongod --config /path/to/source/conf/mongodb.conf
```
- Setup the database:
```bash
$ python manage.py migrate
$ python manage.py createsuperuser
# Answer yes to:
# You just installed Django's auth system, which means you don't have any superusers defined.
# Would you like to create one now? (yes/no): yes
```

## Run the software
- Make sure Redis Server is running.
- Run mongodb (if not already running):
```
$ mongod --config /path/to/source/conf/mongodb.conf
```
- Run celery:
```
$ celery -A mgi worker -l info -Ofair --purge
```
- Run the software:
```
$ cd path/to/source
$ python manage.py runserver --noreload
```
- (Optional) Allow remote access:
```
$ python manage.py runserver 0.0.0.0:<port> --noreload
```

## Access
For the Homepage, Go to:  http://127.0.0.1:8000/

For the Admin Dashboard, Go to:  http://127.0.0.1:8000/admin/ 
