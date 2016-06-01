################################################################################
#
# File Name: views.py
# Application: mgi
# Description: Django views used to render pages for the system.
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

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import logout
from django.template import RequestContext, loader
from django.shortcuts import redirect
from mgi.models import Template, Request, Message, TermsOfUse, PrivacyPolicy, Help
from admin_mdcs.forms import RequestAccountForm, ContactForm
from django.contrib.auth.models import User
from django.contrib import messages


################################################################################
#
# Function Name: home(request)
# Inputs:        request - 
# Outputs:       Materials Data Curation System homepage
# Exceptions:    None
# Description:   renders the main home page from template (index.html)
#
################################################################################
def home(request):
    template = loader.get_template('index.html')

    context = RequestContext(request, {
        'templates': Template.objects(user=None).order_by('-id')[:7]
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: all_options(request)
# Inputs:        request - 
# Outputs:       All Options Page
# Exceptions:    None
# Description:   Page that allows to access every features of the System   
#
################################################################################
def all_options(request):
    template = loader.get_template('all-options.html')
    context = RequestContext(request, {
        '': '',
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: browse_all(request)
# Inputs:        request - 
# Outputs:       Browse All Page
# Exceptions:    None
# Description:   Page that allows to access the list of all existing templates
#
################################################################################
def browse_all(request):
    template = loader.get_template('browse-all.html')

    context = RequestContext(request, {
        'templates': Template.objects(user=None).order_by('title')
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: request_new_account(request)
# Inputs:        request - 
# Outputs:       Request New Account Page
# Exceptions:    None
# Description:   Page that allows to request a user account
#
################################################################################
def request_new_account(request):
    if request.method == 'POST':
        form = RequestAccountForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=request.POST["username"])
                message = "This username already exists. Please choose another username."
                return render(request, 'request_new_account.html', {'form':form, 'action_result':message})
            except:
                Request(username=request.POST["username"], password=request.POST["password1"],first_name=request.POST["firstname"], last_name=request.POST["lastname"], email=request.POST["email"]).save()
                messages.add_message(request, messages.INFO, 'User Account Request sent to the administrator.')
                return redirect('/')
                
    else:
        form = RequestAccountForm()
    
    return render(request, 'request_new_account.html', {'form':form})


################################################################################
#
# Function Name: logout_view(request)
# Inputs:        request - 
# Outputs:       Login Page
# Exceptions:    None
# Description:   Page that redirects to login page
#                
#
################################################################################
def logout_view(request):
    logout(request)
    request.session['next'] = '/'
    return redirect('/login')


################################################################################
#
# Function Name: contact(request)
# Inputs:        request - 
# Outputs:       
# Exceptions:    None
# Description:   
#                
#
################################################################################
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            Message(name=request.POST['name'], email=request.POST['email'], content=request.POST['message']).save()
            messages.add_message(request, messages.INFO, 'Your message was sent to the administrator.')
            return redirect('/')
    else:
        form = ContactForm()
    
    return render(request, 'contact.html', {'form':form})


################################################################################
#
# Function Name: privacy_policy(request)
# Inputs:        request - 
# Outputs:       Privacy Policy Page
# Exceptions:    None
# Description:   Page that provides privacy policy     
#
################################################################################
def privacy_policy(request):
    template = loader.get_template('privacy-policy.html')
    policy = None
    if len(PrivacyPolicy.objects) != 0:
        policy = PrivacyPolicy.objects[0] 

    context = RequestContext(request, { 
        'policy': policy
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: terms_of_use(request)
# Inputs:        request - 
# Outputs:       Terms of Use page
# Exceptions:    None
# Description:   Page that provides terms of use
#
################################################################################
def terms_of_use(request):
    template = loader.get_template('terms-of-use.html')
    terms = None
    if len(TermsOfUse.objects) != 0:
        terms = TermsOfUse.objects[0] 

    context = RequestContext(request, { 
        'terms': terms
    })
    return HttpResponse(template.render(context))


################################################################################
#
# Function Name: help(request)
# Inputs:        request - 
# Outputs:       Help Page
# Exceptions:    None
# Description:   Page that provides FAQ
#
################################################################################
def help(request):
    template = loader.get_template('help.html')
    help = None
    if len(Help.objects) != 0:
        help = Help.objects[0] 

    context = RequestContext(request, { 
        'help': help
    })
    return HttpResponse(template.render(context))
