#!/bin/bash

pylint -f parseable admin_mdcs/ mgi/ api/ oai_pmh/ user_dashboard/ compose/ explore/ utils/XSDhash/ curate/ modules/ exporter/ utils/ testing/ admin_mdcs/ | tee pylint.out