################################################################################
#
# File Name: admin.py
# Application: admin_mdcs
# Purpose:   
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################
from django.contrib import admin
from django.contrib.auth.models import Permission

admin.site.register(Permission)