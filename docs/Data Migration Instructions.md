# Data Migration Instructions (1.3 to 1.4)

MDCS users can now migrate their data from version 1.3 to the version 1.4.

It is highly recommended that you backup your data before starting the migration process. This backup can be accomplished by creating a zip file of the data/db directory and db.sqlite3 file. 
Please make sure to stop the MongoDB server before creating the zip file. Also, please make sure to save the zip file in a different location. 
If something goes wrong you will be able to restore your data by extracting the zip file back into the MDCS directory.

Please follow the instructions below to first update your code to the latest development version and then check that everything is working properly after migrating the data. 

Here are the instructions to follow to update the MDCS from version 1.3 to version 1.4:

- **STOP THE SERVERS** (MongoDB, Django)

- **BACKUP THE DATA** Make a copy of data/db and db.sqlite3 and place them in a different location

- Update the code with 1.4

**Option 1:** Pull the latest code from git:
```
git pull 
```
**Option 2:** Manual installation: Download the new version of the MDCS, copy the data\db directory and db.sqlite3 file from MDCS 1.3 in the MDCS 1.4 folder

- Follow installation instructions to update your version of python with the new set of required packages.

- Restart the servers

```
mongod --config path/to/mongodb.conf
python manage.py runserver
```

- Migrate SQLite3 database

```
python manage.py migrate
```

- Migrate MongoDB database


```
python mgi/migrate.py -u <mongo_admin_user> -p <-mongo_admin_password>
```

Please replace <mongo_admin_user> and <mongo_admin_password> with your MongoDB admin user and MongoDB admin password.

For more information about the migration script options, please use:
```
python mgi/migrate.py -h
```
