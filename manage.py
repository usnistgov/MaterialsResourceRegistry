#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    if str(sys.argv[0]).endswith('manage.py'):
        if 'runserver' in sys.argv or 'migrate' in sys.argv or 'createsuperuser' in sys.argv:
            if 'test' in sys.argv:
                os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mgi.settings_test")
            else:
                os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mgi.settings")
        else:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mgi.settings_test")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mgi.settings_test")

    print 'loading settings at...:' + os.environ.get("DJANGO_SETTINGS_MODULE")

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
