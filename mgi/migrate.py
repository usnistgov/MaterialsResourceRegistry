# IMPORTS
import os
from subprocess import check_output
import time
from pymongo import MongoClient
import sys
from bson.objectid import ObjectId
import argparse
import platform
import getpass

# PROCEDURE:
# - stop mongogod, stop runserver
# - save data/db and db.sqlite3 in a different location
# - Update the code
# - run mongod
# - run migration
# - runserver


class Migration:
    def __init__(self, warnings_enabled=True, backup_enabled=True):
        self.warnings_enabled = warnings_enabled
        self.backup_enabled = backup_enabled

    def _error(self, msg=''):
        print '\n*** MIGRATION FAILED ***'
        print msg
        sys.exit()

    def _build_cmd(self, cmd, path=''):
        """
        Build the command with path
        :param cmd:
        :param path:
        :return:
        """
        if len(path) > 0:
            if platform.system() == "Windows":
                cmd = os.path.join(path, '{}.exe'.format(cmd))
            else:
                cmd = os.path.join(path, cmd)

        return cmd

    def _get_user_validation(self, msg):
        print msg + '\nContinue? (y/N):'
        user_input = raw_input()
        if user_input.lower() == 'y' or user_input.lower() == 'yes':
            return True
        elif user_input.lower() == 'n' or user_input.lower() == 'no':
            return False
        else:
            return self._get_user_validation("Invalid input.")

    def _warn_user(self, msg):
        if self.warnings_enabled:
            return self._get_user_validation(msg)
        return True

    def _dump_database(self, mongo_admin_user, mongo_admin_password, mongo_path):
        if self.backup_enabled:
            if not self._warn_user('An additional backup of the MongoDB database will be created, so the script can '
                                   'restore data in the case of an unexpected error occurring during the migration. '
                                   'If you do not wish to create this backup, please run the script with the option '
                                   '--no-backup.'):
                self._error()
            from settings import BASE_DIR
            # generate time string
            time_str = time.strftime("%Y%m%d_%H%M%S")
            # backup directory name
            backup_dir_name = 'backup_{}'.format(time_str)
            # backup_directory_path
            BACKUPS_DIR = os.path.join(BASE_DIR, 'backups')
            backup_dir_path = os.path.join(BACKUPS_DIR, backup_dir_name)

            if not self._warn_user('A backup folder will be created at : {}'.format(backup_dir_path)):
                self._error()

            # create the backup directory if not present
            print "Create backup directory: " + backup_dir_path
            if not os.path.exists(backup_dir_path):
                os.makedirs(backup_dir_path)
            else:
                self._error('A backup directory with the same name already exists')

            cmd = self._build_cmd('mongodump', mongo_path)

            if not self._warn_user('A dump of the data will be crated using the following command : {}'.format(cmd)):
                self._error()

            print "Dumping the database..."

            try:
                output = check_output(
                        [
                            cmd,
                            '--out',
                            backup_dir_path,
                            '-u',
                            mongo_admin_user,
                            '-p',
                            mongo_admin_password
                        ]
                    )

                # Test that the dump created files
                if len(os.listdir(backup_dir_path)) == 0:
                    self._error('Dump failed')

                if not self._warn_user('Please check the console for any eventual undetected problem during the dump.'):
                    self._error()
            except Exception, e:
                self._error(e.message)

            return backup_dir_path
        else:
            return ''

    def _restore_dump(self, backup_dir_path, mongo_admin_user, mongo_admin_password, mongo_path):
        """
        Restore a dump
        :param backup_dir_path:
        :return:
        """
        if self.backup_enabled:
            print "*** RESTORE DUMP ***"

            cmd = self._build_cmd('mongorestore', mongo_path)

            output = check_output(
                [
                    cmd,
                    backup_dir_path,
                    '--drop',
                    '-u',
                    mongo_admin_user,
                    '-p',
                    mongo_admin_password
                ]
            )

    def _connect(self):
        """
        Connect to the database
        :return: database connection
        """
        from settings import MONGODB_URI, MGI_DB
        try:
            # Connect to mongodb
            print 'Attempt connection to database...'
            client = MongoClient(MONGODB_URI)
            print 'Connected to database with success.'
            try:
                # connect to the db 'mgi'
                print 'Attempt connection to collection...'
                db = client[MGI_DB]
                print 'Connected to collection with success.'
                return db
            except Exception, e:
                self._error('Unable to connect to the collection. ')
        except Exception, e:
            self._error('Unable to connect to MongoDB. '
                        'Please check that mongod is currently running and connected to the MDCS data.')

    def _check_duplicate_names(self, form_data_col):
        """
        Check the database for duplicated form data name
        :param form_data_col:
        :return:
        """
        # get list of users
        users = form_data_col.distinct('user')
        for user in users:
            cursor = form_data_col.find({'user': user})
            for result in cursor:
                name = result['name']
                duplicates = list(form_data_col.find({'user': user, 'name': name}))
                if len(duplicates) > 1:
                    return duplicates
        return []

    def _resolve_duplicate_names(self, form_data_col):
        duplicates = self._check_duplicate_names(form_data_col)
        while len(duplicates) > 0:
            print "Duplicate form names ({2}) have been found " \
                  "(user: {0}, form name: {1})".format(str(duplicates[0]['user']),
                                                       duplicates[0]['name'],
                                                       str(len(duplicates)))
            for idx in range(len(duplicates)):
                duplicate = duplicates[idx]
                duplicate_id = duplicate['_id']
                dup_form_name = '{0}_dup_{1}'.format(duplicate['name'], str(idx+1))
                payload = {'name': dup_form_name}
                print "Update form name (id: {0}): {1}".format(str(duplicate_id), dup_form_name)
                form_data_col.update({'_id': ObjectId(duplicate_id)}, {"$set": payload}, upsert=False)
            duplicates = self._check_duplicate_names(form_data_col)

    def _update_blob_metadata(self, db):
        from settings import BLOB_HOSTER
        if BLOB_HOSTER == 'GridFS':
            import gridfs
            fs = gridfs.GridFS(db)
            if len(fs.list()):
                print "Update BLOB metadata: default owner is superuser."
                files_col = db['fs.files']
                payload = {'metadata': {'iduser': '1'}}
                for blob in fs.find():
                    if 'iduser' not in blob.metadata:
                        files_col.update({'_id':ObjectId(blob._id)}, {"$set": payload}, upsert=False)

    def migrate(self, mongo_admin_user, mongo_admin_password, mongo_path, warnings=True, backup=True):
        """
        APPLIES CHANGES FROM 1.3 TO 1.4

        :return:
        """
        print '*** START MIGRATION ***'

        msg = 'You are about to run the NMRR Migration Tool. ' \
              'This will update the database from version 1.3 to work for version 1.4. ' \
              'Changes will be applied to the database such as additions/deletions/modifications ' \
              'of fields/collections/records.'

        if not self._warn_user(msg):
            self._error()

        # /!\ PROMPT TO CREATE A ZIP OF THE DATA FIRST
        msg = 'Please be sure that you made a copy of the data/db folder and of the db.sqlite3 file before starting.'

        if not self._warn_user(msg):
            self._error()

        # connect to the database
        db = self._connect()

        # TODO: /!\ CHECK IF THE RESULT OF THE DUMP LOOKS GOOD
        # Create a dump of the database
        backup_dir_path = self._dump_database(mongo_admin_user=mongo_admin_user,
                                              mongo_admin_password=mongo_admin_password,
                                              mongo_path=mongo_path)

        print '*** START MIGRATING DATA ***'
        try:
            if not self._warn_user('The changes on the database are about to be applied.'):
                self._error()

            # GET COLLECTIONS NEEDED FOR MIGRATION
            meta_schema_col = db['meta_schema']
            template_col = db['template']
            type_col = db['type']
            form_data_col = db['form_data']
            xml_data_col = db['xmldata']
            result_xslt_col = db['result_xslt']

            # METASCHEMA COLLECTION REMOVED:
            # NEED TO UPDATE THE CONTENT OF TEMPLATES/TYPES
            print "Updating templates/types with meta_schema collection..."

            # find all meta_schema of the collection
            cursor = meta_schema_col.find()

            # Browse meta_schema collection
            for result in cursor:
                # get the template/type id
                schema_id = result['schemaId']
                # get the content stored in meta_schema
                api_content = result['api_content']
                # create a payload to update the template/type
                payload = {'content': api_content}

                # get the template/type to update
                to_update = template_col.find_one({'_id': ObjectId(schema_id)})
                template_col.update({'_id': ObjectId(schema_id)}, {"$set": payload}, upsert=False)
                if to_update is None:
                    to_update = type_col.find_one({'_id': ObjectId(schema_id)})
                    if to_update is None:
                        # restore dump
                        self._restore_dump(backup_dir_path=backup_dir_path,
                                           mongo_admin_user=mongo_admin_user,
                                           mongo_admin_password=mongo_admin_password,
                                           mongo_path=mongo_path)
                        self._error('Trying to update the content of ' + schema_id + ' but it cannot be found')
                    else:
                        type_col.update({'_id': ObjectId(schema_id)}, {"$set": payload}, upsert=False)

            # XMLDATA CHANGES:
            print "Updating xml_data..."
            # find all meta_schema of the collection
            cursor = xml_data_col.find()
            # Browse xml_data collection
            for result in cursor:
                print "Adding status to all records (Active by default)..."
                #Get the status value inside the schema
                content = result['content']
                status = content.get('Resource', dict()).get('@status', None)
                if not status:
                    status = 'active'
                xml_data_col.update({'_id': result['_id']}, {"$set": {"status": status}}, upsert=False)
                print "Adding oai_datestamp to records..."
                # xml data has a publication date
                if 'publicationdate' in result:
                    publication_date = result['publicationdate']
                    # set oai_datestamp to publication date
                    payload = {'oai_datestamp': publication_date}
                    if 'lastmodificationdate' not in result:
                        payload.update({'lastmodificationdate': publication_date})
                    xml_data_col.update({'_id': result['_id']}, {"$set": payload}, upsert=False)
                else:
                    if 'lastmodificationdate' not in result:
                        # set last modification date to datetime.MIN
                        generation_time = result['_id'].generation_time
                        payload = {'lastmodificationdate': generation_time}
                        xml_data_col.update({'_id': result['_id']}, {"$set": payload}, upsert=False)

            # FORM DATA UNIQUE NAMES
            self._resolve_duplicate_names(form_data_col)

            # FORMDATA CHANGES:
            print "Adding isNewVersionOfRecord to all form data (False by default)..."
            form_data_col.update({}, {"$set": {"isNewVersionOfRecord": False}}, upsert=False, multi=True)

            #XSLT OAI-PMH
            print "Remove old full-oai_pmh result XSLT..."
            result_xslt_col.remove({'filename': 'nmrr-full-oai_pmh.xsl'})
            print "Remove old detail-oai_pmh result XSLT..."
            result_xslt_col.remove({'filename': 'nmrr-detail-oai_pmh.xsl'})

            

            #NEW REGISTRY TEMPLATES BY DEFAULT
            #################################
            
            # CLEAN THE DATABASE
            print "*** CLEAN THE DATABASE ***"
            # remove elements from Form_data (not used in 1.4)
            print "Removing elements from form_data collection..."
            form_data_col.update({}, {"$unset": {"elements": 1}}, multi=True)
            # drop form_element collection (not used in 1.4)
            print "Dropping form_element collection..."
            db.drop_collection('form_element')
            # drop xml_element collection (not used in 1.4)
            print "Dropping xml_element collection..."
            db.drop_collection('x_m_l_element')
            # drop meta_schema collection (not used in 1.4)
            print "Dropping meta_schema collection..."
            db.drop_collection('meta_schema')
        except Exception, e:
            self._restore_dump(backup_dir_path=backup_dir_path,
                               mongo_admin_user=mongo_admin_user,
                               mongo_admin_password=mongo_admin_password,
                               mongo_path=mongo_path)
            self._error(e.message)

        print "\n*** MIGRATION COMPLETE ***"
        print "You can now restart the server. " \
              "Do not delete any of the backup files before making sure everything is working fine."
        print "*** MIGRATION COMPLETE ***"


def _get_mongo_connection_info():
        print '\nPlease provide admin user and password to connect to MongoDB.'
        mongo_user = getpass.getpass('User:')
        mongo_password = getpass.getpass('Password:')
        return mongo_user, mongo_password


def main(argv):
    parser = argparse.ArgumentParser(description="Curator Data Migration Tool")

    # add optional arguments
    parser.add_argument('-path',
                        '--mongo-path',
                        help='Path to MongoDB bin folder (if not in PATH)',
                        nargs=1)
    parser.add_argument('-y',
                        '--yes-to-all',
                        help='Does not show warnings',
                        action='store_true')
    parser.add_argument('-n',
                        '--no-backup',
                        help='Does not create a backup of the database before starting the migration',
                        action='store_true')
    parser.add_argument('-u',
                        '--mongo-admin-user',
                        help='Username of MongoDB Admin for backup',
                        nargs=1)
    parser.add_argument('-p',
                        '--mongo-admin-password',
                        help='Password of MongoDB Admin for backup',
                        nargs=1)

    # parse arguments
    args = parser.parse_args()

    if args.mongo_path:
        mongo_path = args.mongo_path[0]
    else:
        mongo_path = ''

    if args.yes_to_all:
        warnings_enabled = False
    else:
        warnings_enabled = True

    if args.no_backup:
        backup_enabled = False
        mongo_admin_user = ""
        mongo_admin_password = ""
        if args.mongo_admin_user or args.mongo_admin_password:
            print "WARNING: You chose to use the --no-backup option. The provided mongodb information will not be used."
    else:
        backup_enabled = True
        if not args.mongo_admin_user or not args.mongo_admin_password:
            mongo_admin_user, mongo_admin_password = _get_mongo_connection_info()
        else:
            mongo_admin_user = args.mongo_admin_user[0]
            mongo_admin_password = args.mongo_admin_password[0]

    # Start migration
    migration = Migration(warnings_enabled=warnings_enabled, backup_enabled=backup_enabled)
    migration.migrate(mongo_admin_user=mongo_admin_user,
                      mongo_admin_password=mongo_admin_password,
                      mongo_path=mongo_path)

if __name__ == "__main__":
    main(sys.argv[1:])
