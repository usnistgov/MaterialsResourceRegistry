#!/bin/bash

pylint -f parseable mgi/ api/ oai_pmh/ user_dashboard/ compose/ explore/ utils/XSDhash/ | tee pylint.out