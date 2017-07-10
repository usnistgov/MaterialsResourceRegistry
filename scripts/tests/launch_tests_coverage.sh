#!/bin/bash
coverage run --source=mgi,api,oai_pmh,user_dashboard,compose,explore,utils/XSDhash,utils/XSDParser,admin_mdcs/ ./manage.py test mgi/ api/ oai_pmh/ user_dashboard/ compose/ explore/ utils/XSDhash/ utils/XSDParser/ admin_mdcs/ --liveserver=localhost:8082 --no-selenium

