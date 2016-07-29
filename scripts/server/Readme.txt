How to use launch_server_unix.sh:

If you need help for the command line, you can always use -h or --help like that:
./launch_server_unix.sh -h

Path to MongoDB configuration file and to Django project are mandatory.
For example, in a terminal you can run the command:
 
./launch_server_unix.sh -p ~/workspace/mgi-mdcs -c /etc/mongodb.conf

MongoDB and Django ports are not mandatory. If you don't specified them, Django will run on port 8000 and MongoDB on port 27017
If you need to change them, for example, in a terminal you can run:

./launch_server_unix.sh -p ~/workspace/mgi-mdcs -c /etc/mongodb.conf -m 27018 -d 8001

For the others options, if your path is already set up, you don't need them. If you want to use a different version of the lib specified in your path, or if there is no lib configured in your path, you can speficied a path for each lib you want to use. For example, in a terminal, you can run:

 ./launch_server_unix.sh -p ~/workspace/mgi-mdcs -c /etc/mongodb.conf -y /usr/bin/python -l /usr/bin/celery -g /usr/bin/mongo

If your path is not configured, but don't know the path to the application, you can use the command 'which'.

You can use -r or --nocelery if you don't intend to use celery. Celery is used by the software to send emails (user account, publish, and so on) and for automatic harvesting with OAI_PMH.

You can use -k --killall if you want to automatically kill all running processes before launching the server.
