#!/bin/bash
pylint --load-plugins pylint_django -f parseable admin_mdcs/ mgi/ api/ oai_pmh/ user_dashboard/ compose/ explore/ utils/ curate/ modules/ exporter/ testing/ | tee pylint.out