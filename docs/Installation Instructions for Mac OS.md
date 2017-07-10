# Mac OS Installation Instructions

## Prerequisites

### Homebrew
See installation instructions at [Homebrew](http://brew.sh)


### Python
```
$ brew intall python
```

### (Optional) Virtual Environment
```
$ brew install pyenv pyenv-virtualenv
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
$ brew install redis
```
Please check out the following link if you got a problem during the brew install:
http://apple.stackexchange.com/questions/153790/how-to-fix-brew-after-osx-upgrade-to-yosemite

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
