from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, Http404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from virtualTravel.forms import *
from virtualTravel.models import *
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from django.views.decorators.csrf import ensure_csrf_cookie
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from random import *
import re
import json
from virtualTravel.yelp import *

import urllib.request
import time

MAX_UPLOAD_SIZE = 5000000

def homepage(request):
    return redirect(reverse('homepage'))

# login_action: render login page
def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'virtualTravel/login.html', context)

    # Check post error
    if not 'username' in request.POST:
        context['name_error'] = "Miss input name"
        return render(request, 'virtualTravel/login.html', context)

    if not 'password' in request.POST:
        context['password_error'] = "Miss password"
        return render(request, 'virtualTravel/login.html', context)


    # Creates a bound form from the request POST parameters and makes the 
    info = {
        'username': request.POST['username'],
        'password': request.POST['password']
        }

    # If no username or no password, set error message
    if request.POST['username'] == "":
        context['name_error'] = "Miss input name"
        return render(request, 'virtualTravel/login.html', context)

    if request.POST['password'] == "":
        context['password_error'] = "Miss password"
        return render(request, 'virtualTravel/login.html', context)
        
    form = LoginForm(info)

    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'virtualTravel/login.html', context)

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('homepage'))

def logout_action(request):
    logout(request)
    return redirect(reverse('login'))

def register_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'virtualTravel/register.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.

    list = {'username', 'password', 'confirm_password', 'email'}

    for field in list:
        if field not in request.POST:
            print(field)
            error = field+'_error'
            print(error)
            context[error] = "Miss" + " " + field
            return render(request, 'virtualTravel/register.html', context)

    # Get registration from information
    info = {
        'username': request.POST['username'],
        'password': request.POST['password'],
        'confirm_password': request.POST['confirm_password'],
        'email':request.POST['email']
        }

    # Set the error message if mal input
    if (request.POST['username'] == ""):
        context['username_error'] = "Miss username"

    if (request.POST['password'] == ""):
        context['password_error'] = "Miss password"

    if (request.POST['confirm_password'] == ""):
        context['confirm_password_error'] = "Miss confirm_password"

    if (request.POST['email'] == ""):
        context['email_error'] = "Miss email address"

    try:
        user = User.objects.get(username = request.POST['username'])
        if user:
            context['profile_error'] = "Already registered"
    except:
        pass

    form = RegistrationForm(info)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'virtualTravel/register.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'], 
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'])
    new_user.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    # Create default profile for the user
    default_profile = Profile.objects.create(user=new_user,
                            bio='Hi, I am ' + new_user.username + '!')
    
    #initialize city pool
    for free_city in City.objects.filter(price=0):
        default_profile.city_pool.add(free_city)

    # redirect to login page
    login(request, new_user)
    return redirect(reverse('homepage')+"?new=true")

@login_required
def travel_select_action(request):
    profile = request.user.profile
    context = {}
    # The user is currently on a travel, redirect it to the travelling page
    if len(profile.current_travel.all()) > 0:
        return redirect(reverse('travel'))
    if 'new' in request.GET:
        context['new_user'] = True
    cities = list(profile.city_pool.all())
    context['cities']=cities
    return render(request, 'virtualTravel/travel_select.html', context)

@login_required
def travel_action(request,context={}):
    profile = request.user.profile
    cities = list(profile.city_pool.all())
    errorlist = []

    if request.method  == 'GET':
        if "current_page" not in context:
            context['current_page'] = 'list-City-list'  

    # Create a 'Travel' if this page is entered by clicking 'Start Journey'
    if request.method == 'POST':
        if ('departure' in request.POST) and ('destination' in request.POST):
            if "current_page" not in context:
                context['current_page'] = 'list-City-list'
            departure = request.POST['departure']
            destination = request.POST['destination']

            # User is currently not on a travel 
            if len(profile.current_travel.all()) == 0:
                # Error Handling
                if departure == 'Choose...' or destination == 'Choose...':
                    errorlist.append('Please Select Departure and Destination.')
                
                # Generating routes for the travel
                route = []
                departure_id = -1
                destination_id = -1

                # Remove departure and destination cities from the city pool
                for city in cities:
                    if city.name == departure:
                        departure_id = city.id
                        cities.remove(city)

                if departure != destination:
                    # departure city is not destination city
                    for city in cities:
                        if city.name == destination:
                            destination_id = city.id
                            cities.remove(city)
                else:
                    destination_id = departure_id

                if departure_id != -1 and destination_id != -1:
                    # Randomly generate intermediate stops from the remaining city pool
                    num_of_stops = randint(1, 3) # 1 - 3 stops
                    if num_of_stops > len(cities): # corner case
                        num_of_stops = len(cities)
                    stops = sample(cities, num_of_stops)

                    # Transfer the route into String format
                    route_str = str(departure_id) + ' '
                    for city in stops:
                        route_str += str(city.id) + ' '
                    route_str += str(destination_id)

                    # Create the 'current travel' object from the generated route
                    if len(errorlist) == 0: 
                        current_travel = Travel(num_of_stops=len(route_str.split(' ')), current_stop=0, route=route_str,
                                                 date=timezone.now(), made_by=profile, current_user=profile)
                        current_travel.save()
                elif len(errorlist) == 0:
                    errorlist.append('Please Select a Valid City.')
    
    # rendering city content and quiz no matter GET or POST        
    if len(profile.current_travel.all()) == 0:
        context = {'cities':list(profile.city_pool.all()), 'errorlist': errorlist}
        return render(request, 'virtualTravel/travel_select.html', context)
    else:
        current_travel = profile.current_travel.all()[0]

    # There is at least one error
    if len(errorlist) > 0:
        context = {'cities':list(profile.city_pool.all()), 'errorlist': errorlist}
        return render(request, 'virtualTravel/travel_select.html', context)

    # check if travel finished
    if current_travel.current_stop >= current_travel.num_of_stops:
        cities = current_travel.route.split(" ")
        collected = []
        for city_id in cities:
            city = City.objects.get(id=city_id)
            if city not in profile.city_collection.all():
                collected.append(city.name)
                profile.city_collection.add(city)

        profile.current_travel.clear()
        profile.save() # save() needs to be called after clear()
        context = {'cities':list(profile.city_pool.all())}
        context["collected"]=collected
        context["gold"]=current_travel.gold_earned
        context["finished"]=True
        return render(request, 'virtualTravel/travel_select.html',context)
    
    route = routeParser(current_travel)
    context['route'] = route   

    # get quiz for current city
    current_city = route[current_travel.current_stop]
    context['current_city'] = current_city
    quiz_set=Quiz.objects.filter(quiz_city=current_city).all()
    current_quiz = quiz_set[randint(0,max(0,len(quiz_set))-1)]
    context['quiz'] = current_quiz
    if profile in current_quiz.quiz_users.all():
        context['quiz_answered'] = "true"


    current_city_sites=Site.objects.filter(city=current_city)
    context['current_city_sites']=current_city_sites
    first_site_id = current_city_sites[0].id
    context['first_site_id']=first_site_id
    
    return render(request, 'virtualTravel/traveling.html',context)

@login_required
def next_city_action(request):
    profile = request.user.profile
    current_travel = profile.current_travel.all()[0]
    current_travel.current_stop += 1
    current_travel.save()
    return redirect(reverse('travel'))

@login_required
def profile_action(request):
    context = {}
    profile = request.user.profile
    cities = list(profile.city_collection.all())

    if len(cities) >= 0:
        context['cities'] = cities
        context['percentage'] = 100 * float(len(cities)) / float(len(City.objects.all()))
    else:
        context['percentage'] = 0

    travels = Travel.objects.filter(made_by=request.user.profile, current_user=None)
    if len(travels) >= 0:
        context['travels'] = travels
        context['routes'] = []
        for travel in travels:
            context['routes'].append(routeParser(travel))

    # Update the user picture and bio
    if request.method == 'POST':
        if 'bio' in request.POST:
            profile.bio = request.POST['bio']
        if 'picture' in request.FILES:
            picture = request.FILES['picture']
            if not picture.content_type or not picture.content_type.startswith('image'):
                context['error'] = 'File type is not image'
            elif picture.size > MAX_UPLOAD_SIZE:
                context['error'] = 'File too big (max size is {0} bytes)'.format(MAX_UPLOAD_SIZE)
            else:
                profile.picture.delete()
                profile.content_type = picture.content_type
                profile.picture.save(picture.name, picture)
        profile.save()

    context['profile'] = profile
    context['form'] = ProfileForm(instance=profile)

    return render(request, 'virtualTravel/profile.html', context)

# Get city store page.
@login_required
def store_action(request):
    context = {}
    if request.method == 'GET':
        # Filter city that price large than 0
        citys = City.objects.filter(price__gt=0)
        context['citys'] = citys
        myProfile = request.user.profile
        gold = myProfile.gold
        context['mygold'] = gold
        city_pool = myProfile.city_pool.all()
        context['city_pool'] = city_pool

        return render(request, 'virtualTravel/citystore.html', context)

# Search city to buy.
@login_required  
def searchCity_action(request):
    # If get request
    if request.method == 'GET':
        return store_action(request)
    # If post request
    myProfile = request.user.profile
    context = {}
    if 'search' in request.POST:
        city_name = request.POST['search']
        # rough search
        city = City.objects.filter(name__contains = city_name, price__gt = 0)
        context['citys'] = city
        gold = myProfile.gold
        context['mygold'] = gold
        city_pool = myProfile.city_pool.all()
        context['city_pool'] = city_pool

    return render(request, 'virtualTravel/citystore.html', context)

# Buy cities
@login_required
@transaction.atomic
def buyCity_action(request):
     context = {}
     myProfile = request.user.profile
     # If method is get, show cities gold large than 0
     if request.method == 'GET':
        citys = City.objects.filter(price__gt = 0)
        context['citys'] = citys
        gold = myProfile.gold
        context['mygold'] = gold
        city_pool = myProfile.city_pool.all()
        context['city_pool'] = city_pool
        return render(request, 'virtualTravel/citystore.html', context)

    # post method 
     if 'city_name' in request.POST:
        try:
            city = City.objects.get(name = request.POST['city_name'])

            if city not in myProfile.city_pool.all():
                if myProfile.gold < city.price:
                    pass
                else:
                    # Compute the balance if user buy the city
                    goldChange(myProfile, -city.price)
                    myProfile.city_pool.add(city)
                    myProfile.save()
        except:
            pass

     citys = City.objects.filter(price__gt = 0)
     context['citys'] = citys
     gold = myProfile.gold
     context['mygold'] = gold
     city_pool = myProfile.city_pool.all()
     context['city_pool'] = city_pool

     return render(request, 'virtualTravel/citystore.html', context)
    
@login_required   
def refresh_map(request):
    user_profile = request.user.profile
    if len(user_profile.current_travel.all()) == 0:
        return HttpResponse("No current travel",content_type="text/plain")

    current_travel = user_profile.current_travel.all()[0]
    stops = current_travel.route.split(" ")
    
    response_list = []

    for i in range(0,current_travel.current_stop+1):
        response_list.append(City.objects.get(id=stops[i]))

    response_text = serializers.serialize('json',response_list)

    return HttpResponse(response_text,content_type='application/json')

@login_required
def refresh_cityMap(request):
    user_profile = request.user.profile
    if len(user_profile.current_travel.all()) == 0:
        return HttpResponse("No current travel",content_type="text/plain")

    current_travel = user_profile.current_travel.all()[0]
    routes = current_travel.route.split(" ")
    current_city_id = int(routes[current_travel.current_stop])
    current_city = City.objects.get(id=current_city_id)

    # response_list: [current_city, site1, site2, site3, ...]
    response_list = [current_city] # need the current city to initialize the map location
    sites = Site.objects.filter(city=current_city)
    for site in sites:
        response_list.append(site)

    response_text = serializers.serialize('json',response_list)

    return HttpResponse(response_text,content_type='application/json')

@login_required
def cityMap(request):
    context = {}
    return render(request, 'virtualTravel/cityMap.html', context)

@login_required
def get_photo(request):
    profile = get_object_or_404(Profile, user=request.user)
    # someone could have deleted the picture leaving the DB with a bad references.
    if not profile.picture:
        raise Http404
    return HttpResponse(profile.picture, content_type=profile.content_type) 

# helpers 
def routeParser(travel):
    route = []
    for city_id in travel.route.split(' '):
        try:
            city = City.objects.get(id=int(city_id))
        except:
            city = City.objects.get(id=1)
        route.append(city)
    return route

@login_required
def user_upload(request):
    context = {}

    # Check user city pool
    user_profile=request.user.profile
    user_city_pool=user_profile.city_pool
    cities = list(user_city_pool.all())
    context = {'city_pool':cities}
    
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['quiz_form'] = UserUploadForm_quiz()
        context['site_form'] = UserUploadForm_site()
        return render(request, 'virtualTravel/user_upload.html', context)

    # ************************** Upload quiz ******************************** #
    if 'quiz_city_name' in request.POST:
        upload_city_name=request.POST['quiz_city_name'].strip()

        # Malformed Input Handling
        if 'quiz_city_name' == 'Choose...':
            context['quiz_message']="Please select a city for the quiz."
            return render(request, 'virtualTravel/user_upload.html', context)
        if 'quiz_answer' not in request.POST:
            context['quiz_message']="Please select an answer for the quiz."
            return render(request, 'virtualTravel/user_upload.html', context)

        try:
            quiz_answer_int = int(request.POST['quiz_answer'])
            if quiz_answer_int < 1 or quiz_answer_int > 4:
                context['quiz_message']="Please select a valid answer for the quiz."
                return render(request, 'virtualTravel/user_upload.html', context)
        except:
            context['quiz_message']="Please choose a valid answer for the quiz."
            return render(request, 'virtualTravel/user_upload.html', context)

        try:
            find_city = City.objects.get(name = upload_city_name)
        except:
            context['quiz_message']="Please select a valid city."
            return render(request, 'virtualTravel/user_upload.html', context)

        # Check whether input city is valid
        if not find_city in user_city_pool.all():
            context['quiz_message']="Please select a valid city."
            return render(request, 'virtualTravel/user_upload.html', context)

        # check whether all parameters exist
        if not "quiz_text" in request.POST:
            context['quiz_message']='Missing quiz question!'
            return render(request, 'virtualTravel/user_upload.html', context)
        if not "quiz_option_1" in request.POST:
            context['quiz_message']='Missing quiz option 1!'
            return render(request, 'virtualTravel/user_upload.html', context)
        if not "quiz_option_2" in request.POST:
            context['quiz_message']='Missing quiz option 2!'
            return render(request, 'virtualTravel/user_upload.html', context)
        if not "quiz_option_3" in request.POST:
            context['quiz_message']='Missing quiz option 3!'
            return render(request, 'virtualTravel/user_upload.html', context)
        if not "quiz_option_4" in request.POST:
            context['quiz_message']='Missing quiz option 4!'
            return render(request, 'virtualTravel/user_upload.html', context)

        # Get the input data and save the quiz in database
        new_quiz = Quiz(quiz_city=find_city,
                        quiz_text=request.POST['quiz_text'], 
                        quiz_option_1=request.POST['quiz_option_1'],
                        quiz_option_2=request.POST['quiz_option_2'],
                        quiz_option_3=request.POST['quiz_option_3'],
                        quiz_option_4=request.POST['quiz_option_4'],
                        quiz_answer=request.POST['quiz_answer'])
        new_quiz.save()

        context['quiz_message']='Upload Quiz Successful! You earned 50 gold!'
        context['success'] = True
        goldChange(user_profile, 50) # add 50 gold to the user account

    # *********************************************************************** #


    # ************************** Upload site ******************************** #
    elif 'city_name' not in request.POST:
        context['site_message']="Missing city name!"
    else:
        if 'name' not in request.POST:
            context['site_message']="Missing site name!"
            return render(request, 'virtualTravel/user_upload.html', context)
        if 'description' not in request.POST:
            context['site_message']="Missing site description!"
            return render(request, 'virtualTravel/user_upload.html', context)
        if 'site_picture_url' not in request.POST:
            context['site_message']="Missing site picture url!"
            return render(request, 'virtualTravel/user_upload.html', context)
        upload_site_name=request.POST['name'].strip()
        upload_site_city=request.POST['city_name'].strip()

        # user can only upload picture to new site
        for site in Site.objects.all():
            if site.name == upload_site_name:
                context['site_message']="This site exists already. Please upload a new site."
                return render(request, 'virtualTravel/user_upload.html', context)

        try:
            find_site_city = City.objects.get(name = upload_site_city)
        except:
            context['site_message']="Please select a valid city."
            return render(request, 'virtualTravel/user_upload.html', context)

        # Check whether input city is valid
        if not find_site_city in user_city_pool.all():
            context['site_message']="Please select a valid city."
            return render(request, 'virtualTravel/user_upload.html', context)

        # Check url is active
        if not checkurl(request.POST['site_picture_url']):
            context['site_message'] = "Upload failed. Invalid image url."
            return render(request, 'virtualTravel/user_upload.html', context)


        # Get the input site data and save the site in database 
        new_site = Site(name=upload_site_name,
                        description=request.POST['description'], 
                        picture_url=request.POST['site_picture_url'],
                        city=find_site_city)
        new_site.save()

        context['site_message']="Upload site '"+new_site.name+"' Successful! You earned 50 gold!"
        goldChange(user_profile, 50) # add 50 gold to the user account
        context['success'] = True
    # *********************************************************************** #
    
    return render(request, 'virtualTravel/user_upload.html', context)

# check upload url is correct
def checkurl(url):
    # Try to open the url
    if not re.match(r'((http|https):\/\/([\w.]+\/?)\S*/)',url, re.M|re.I):
        return False
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/49.0.2')]
    try :
        opener.open(url)    
        return re.match( r'(.+?.(?:bmp|jpg|png|gif|jpeg))', url, re.M|re.I)
    except urllib.error.HTTPError:
        time.sleep(2)
        return False
    except urllib.error.URLError:
        time.sleep(2)
        return False

# Show the food page
@login_required
def foodPage_action(request):
    if request.method == 'GET':
        context['current_page'] = 'list-Food-list'
        return travel_action(request, context)


# Search the food
@login_required
def food_search_action(request):
    if request.method == 'POST':
        user_profile = request.user.profile
        current_travel = user_profile.current_travel.all()[0]
        routes = current_travel.route.split(" ")
        current_city_id = int(routes[current_travel.current_stop])
        current_city = City.objects.get(id=current_city_id)
        arr= request.POST.getlist('food_preference')
        filters= ','.join(arr)
        request.session['location_input'] = current_city.name
        request.session['search_results'] = query_api(filters, request.session['location_input'])
        return redirect(reverse('food_result'))
    else:
        context['current_page'] = 'list-Food-list'
        return travel_action(request, context)

# Show the food search result        
@login_required
def food_result_action(request):
    search_results = request.session['search_results']
    context = {
        'places_list': search_results
    }
    context['current_page'] = 'list-Food-list'
    return travel_action(request, context)

@transaction.atomic
def check_quiz(request,id,choice):
    profile = request.user.profile
    current_quiz = Quiz.objects.get(id=id)
    current_travel = profile.current_travel.all()[0]

    gold = ""
    if choice == current_quiz.quiz_answer :
        if not profile in current_quiz.quiz_users.all():
            goldChange(profile, 100)
            current_travel.gold_earned += 100
            profile.save()
            current_travel.save()
            current_quiz.quiz_users.add(profile)
            gold = " You've been awarded 100 gold."
        response = '<div class="alert alert-success" role="alert"> \
                    <button type="button" class="close" data-dismiss="alert">&times;</button>\
                    <strong>Well done!</strong> The answer is Correct!' + gold +'</div>'
    else:
        response = '<div class="alert alert-danger" role="alert">\
                <button type="button" class="close" data-dismiss="alert">&times;</button>\
                <strong>Oops!</strong> The answer is wrong!</div>'
    return HttpResponse(response,content_type='text/plain')

def check_last_city(request):
    profile = request.user.profile
    current_travel = profile.current_travel.all()[0]
    if current_travel.current_stop + 1 == current_travel.num_of_stops:
        return HttpResponse("true",content_type='text/plain')

    else:
        return HttpResponse("false",content_type='text/plain')

@transaction.atomic
def goldChange(profile, change):
    profile.gold += change
    profile.save()

