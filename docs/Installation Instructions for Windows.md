# Windows Installation Instructions

## Prerequisites

### Python
- Download python 2.7 for windows 32bits from https://www.python.org/download/
- Add to PATH:

C:\Python27\
C:\Python27\Scripts

### Pip
We need pip to do the installation of the required dependencies.  pip requires setuptools and it has to be installed first, before pip can run: http://www.pip-installer.org/en/latest/installing.html 
```
$ python get-pip.py 
```

### (Optional) Virtual Environment
- In a command prompt:
```
$ pip install virtualenvwrapper-win
```
- Add environment variable
WORKON_HOME=%USERPROFILE%\Develop\Envs
- In a command prompt:
```
$ mkdir %WORKON_HOME%
$ cd %WORKON_HOME%
$ mkvirtualenv mgi
```
- To use the environment (the prompt will become mgi. You should always see the mgi prompt when installing new packages):
```
$ workon mgi
```

### MongoDB
- Download from https://www.mongodb.com/download-center#community
- Follow the instructions provided by MongoDB to install it

### Redis Server
- Download from https://github.com/MSOpenTech/redis/releases
- Run the msi


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
