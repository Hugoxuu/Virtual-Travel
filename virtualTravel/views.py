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

from random import *
import re
import json

from virtualTravel.yelp import *

# Create your views here.
def homepage(request):
    return redirect(reverse('homepage'))

def login_action(request):
    context = {}

    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'virtualTravel/login.html', context)

    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
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
    form = RegistrationForm(request.POST)
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
    return redirect(reverse('homepage'))

@login_required
def travel_select_action(request):
    profile = request.user.profile

    # The user is currently on a travel, redirect it to the travelling page
    if len(profile.current_travel.all()) > 0:
        return redirect(reverse('travel'))

    cities = list(profile.city_pool.all())
    context = {'cities':cities}
    return render(request, 'virtualTravel/travel_select.html', context)

@login_required
def travel_action(request):
    context = {}

    profile = request.user.profile
    cities = list(profile.city_pool.all())
    errorlist = []

    # Create a 'Travel' if this page is entered by clicking 'Start Journey'
    if request.method == 'POST':
        if 'departure' in request.POST:
            departure = request.POST['departure']
            destination = request.POST['destination']

            # User is currently not a travel
            if len(profile.current_travel.all()) == 0:
                # Error Handling
                if departure == 'Choose...' or destination == 'Choose...':
                    errorlist.append('Please Select Cities for Departure and Destination')

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

                # Randomly generate intermediate stops from the remaining city pool
                num_of_stops = randint(2, 4) # 2 - 4 stops
                if num_of_stops > len(cities): # corner case
                    num_of_stops = len(cities)
                stops = sample(cities, num_of_stops)

                # Transfer the route into String formate
                route_str = str(departure_id) + ' '
                for city in stops:
                    route_str += str(city.id) + ' '
                route_str += str(destination_id)

                # Create the 'current travel' object from the generated route
                current_travel = Travel(num_of_stops=len(route_str.split(' ')), current_stop=0, route=route_str,
                                         date=timezone.now(), made_by=profile, current_user=profile)
                current_travel.save()

        else:  # This travel page is servered upon user submitting quiz
            current_travel = profile.current_travel.all()[0]
            current_city_id = current_travel.route.split(' ')[current_travel.current_stop]
            current_city_name = City.objects.get(id=current_city_id).name
            quiz_set=Quiz.objects.filter(quiz_city=current_city_id).all()
            current_quiz = quiz_set[randint(0,max(0,len(quiz_set))-1)]

            if 'question' in request.POST: # checking quiz result
                if request.POST['question'] == str(current_quiz.quiz_answer):
                    context['result'] = 1
                    if not profile in current_quiz.quiz_users.all():
                        profile.gold+=100;
                        profile.save()
                        current_quiz.quiz_users.add(profile)
                        context['quiz_result'] = "Good. The answer for "+current_city_name+" is correct! Now you have "+(str)(profile.gold)+" gold. \
                        You have unlocked the next city. Enjoy it at Overview and City Exploration! "
                    else:
                        context['quiz_result'] = "Good. The answer for "+current_city_name+" is correct! But you had taken this quiz before. You cannot earn gold this time. Now you have unlocked the next city. Enjoy it at Overview and City Exploration!"
                else:
                    context['result'] = 0
                    context['quiz_result'] = "Sad. The answer for "+current_city_name+" is wrong! Now you have "+(str)(profile.gold)+" gold."

                # quiz completed move to next stop
                current_travel.current_stop += 1
                current_travel.save()
    
    # rendering city content and quiz no matter GET or POST        
    if len(profile.current_travel.all()) == 0:
        errorlist.append('This user has not started a travel.')
    else:
        current_travel = profile.current_travel.all()[0]

    # There is at least one error
    if len(errorlist) > 0:
        context = {'cities':list(profile.city_pool.all()), 'errorlist': errorlist}
        return render(request, 'virtualTravel/travel_select.html', context)

    # check if travel finished
    if current_travel.current_stop >= current_travel.num_of_stops:
        print("All cities have been visited. Travel archived.\n")
        profile.current_travel.clear()
        profile.save() # save() needs to be called after clear()
        context = {'cities':list(profile.city_pool.all())}
        return render(request, 'virtualTravel/travel_select.html',context)
    
    route = routeParser(current_travel)
    context['route'] = route   

    # get quiz for current city
    current_city = route[current_travel.current_stop]
    context['current_city'] = current_city
    quiz_set=Quiz.objects.filter(quiz_city=current_city).all()
    context['quiz'] = quiz_set[randint(0,max(0,len(quiz_set))-1)]
    context['current_page'] = 'list-City-list'
    
    return render(request, 'virtualTravel/traveling.html',context)

@login_required
def profile_action(request):
    context = {}

    profile = request.user.profile

    cities = list(profile.city_pool.all())

    if len(cities) >= 0:
        context['cities'] = cities
        context['percentage'] = 100 * float(len(cities)) / float(len(City.objects.all()))
    else:
        context['percentage'] = 0

    travels = Travel.objects.filter(made_by=request.user.profile)
    if len(travels) >= 0:
        context['travels'] = travels
        context['routes'] = []
        for travel in travels:
            context['routes'].append(routeParser(travel))

    # Update the user picture and bio
    if request.method == 'POST':
        profile.bio = request.POST['bio']
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if 'picture' in request.FILES:
            profile.picture.delete()
            picture = request.FILES['picture']
            profile.content_type = picture.content_type
            profile.picture.save(picture.name, picture)
        profile.save()

    context['profile'] = profile
    context['form'] = ProfileForm(instance=profile)

    return render(request, 'virtualTravel/profile.html', context)

@login_required
def store_action(request):
    context = {}
    if request.method == 'GET':
        citys = City.objects.filter(price__gt = 0)
        context['citys'] = citys
        myPorfile = request.user.profile
        gold = myPorfile.gold
        context['mygold'] = gold
        city_pool = myPorfile.city_pool.all()
        context['city_pool'] = city_pool

        return render(request, 'virtualTravel/citystore.html', context)


@login_required
def show_grades(request):
    print("enter show_grades")
    context = {}
    if request.method == 'GET':
        return render(request, 'virtualTravel/traveling.html', context)

    user_profile=request.user.profile
    if len(user_profile.current_travel.all())!=0:
        current_travel=user_profile.current_travel.all()[0]

    print("num_of_stops is "+(str)(current_travel.num_of_stops)) 
    print("route is "+current_travel.route)     
    if current_travel.current_stop>=current_travel.num_of_stops:
        user_profile.current_travel.clear()
    else:
        current_travel.current_stop+=1 
        current_travel.save() 
        print("current_stop is "+(str)(current_travel.current_stop)) 
        current_city=current_travel.route.split()[current_travel.current_stop-1]
        current_city_id=re.findall(r"\d+\.?\d*",current_city)[0]
        print("current city is "+current_city_id)
        quiz = Quiz.objects.get(quiz_city=current_city_id)
        print("quiz is "+quiz.quiz_text)
        print("option 1 is "+quiz.quiz_option_1)
        res = quiz.quiz_answer    
        
        print(request.POST)

        if 'question' in request.POST:
            if request.POST['question'] == str(res):
                context['result'] = 1
                context['quiz_result'] = "Good. The answer for City id="+current_city_id+" is correct!"
            else:
                context['result'] = 0
                context['quiz_result'] = "Sad. The answer for City id="+current_city_id+" is wrong!"

        context['quiz'] = quiz;

    return render(request, 'virtualTravel/traveling.html', context)
    
def searchCity_action(request):
    if request.method == 'GET':
        return store_action(request)
    myPorfile = request.user.profile
    context = {}
    if 'search' in request.POST:
        city_name = request.POST['search']

        city = City.objects.filter(name__contains = city_name)
        context['citys'] = city
        gold = myPorfile.gold
        context['mygold'] = gold
        city_pool = myPorfile.city_pool.all()
        context['city_pool'] = city_pool

    return render(request, 'virtualTravel/citystore.html', context)


def buyCity_action(request):
     context = {}
     myPorfile = request.user.profile
     if request.method == 'GET':
        citys = City.objects.filter(price__gt = 0)
        context['citys'] = citys
        gold = myPorfile.gold
        context['mygold'] = gold
        city_pool = myPorfile.city_pool.all()
        context['city_pool'] = city_pool
        return render(request, 'virtualTravel/citystore.html', context)

     if 'city_name' in request.POST:
        # compute the balance
        print(request.POST['city_name'])
        city = City.objects.get(name = request.POST['city_name'])
        print(city.price)

        if myPorfile.gold < city.price:
            print("less")
            print(myPorfile.gold)
        else:
            myPorfile.gold -= city.price
            print(myPorfile.gold)
            myPorfile.city_pool.add(city)
            myPorfile.save()
     citys = City.objects.filter(price__gt = 0)
     context['citys'] = citys
     gold = myPorfile.gold
     context['mygold'] = gold
     city_pool = myPorfile.city_pool.all()
     context['city_pool'] = city_pool

     return render(request, 'virtualTravel/citystore.html', context)
    
    
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

def cityMap(request):
    context = {}
    return render(request, 'virtualTravel/cityMap.html', context)

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
        city = City.objects.get(id=int(city_id))
        route.append(city)
    return route

def user_upload(request):
    context = {}

    # Check user city pool
    user_profile=request.user.profile
    user_city_pool=user_profile.city_pool
    print("user city pool is: ")
    for city in user_city_pool.all():
        print(city.name)
    print(" ")
    cities = list(user_city_pool.all())
    context = {'city_pool':cities}
    
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['quiz_form'] = UserUploadForm_quiz()
        context['site_form'] = UserUploadForm_site()
        return render(request, 'virtualTravel/user_upload.html', context)

    # ************************** upload quiz ************************************
    if 'quiz_city_name' in request.POST:
        print("upload quiz")
        upload_city_name=request.POST['quiz_city_name'].strip()
        print("in request.POST quiz_city_name is "+upload_city_name+'a')
        print(upload_city_name=='Chicago')
        try:
            find_city = City.objects.get(name = upload_city_name)
        except:
            context['quiz_message']="This city is not supported."
            return render(request, 'virtualTravel/user_upload.html', context)
        print("find_city is "+find_city.name)

        # Check whether input city is valid
        if not find_city in user_city_pool.all():
            context['quiz_message']="You have no access to this city since it's not in your city pool."
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

        print('city name is '+new_quiz.quiz_city.name+', answer is '+new_quiz.quiz_answer)
        context['quiz_message']="uploading quiz succeed!"
    # *****************************************************************************


    # ************************** upload site ************************************
    if 'city_name' in request.POST:
        print("upload site")
        upload_site_name=request.POST['name'].strip()
        upload_site_city=request.POST['city_name'].strip()
        print("in request.POST site_city_name is "+upload_site_name+'a')
        print(upload_site_name=='greenfield')

        # user can only upload picture to new site
        print("now have sites: ")
        for site in Site.objects.all():
            print(site.name)
            if site.name == upload_site_name:
                print("this site already exists")
                context['site_message']="This site exists already. Please upload a new site."
                return render(request, 'virtualTravel/user_upload.html', context)
        print(" ")

        try:
            find_site_city = City.objects.get(name = upload_site_city)
        except:
            context['site_message']="This city is not supported."
            return render(request, 'virtualTravel/user_upload.html', context)
        print("find_site_city is "+find_site_city.name)

        # Check whether input city is valid
        if not find_site_city in user_city_pool.all():
            context['site_message']="You have no access to this city since it's not in your city pool."
            return render(request, 'virtualTravel/user_upload.html', context)

        # Get the input site data and save the site in database
        new_site = Site(name=upload_site_name,
                        description=request.POST['description'], 
                        picture_url=request.POST['site_picture_url'],
                        city=find_site_city)
        new_site.save()

        print('site name is '+new_site.name)
        context['site_message']="uploading site '"+new_site.name+"' succeed!"
    # *****************************************************************************
    print(context)
    return render(request, 'virtualTravel/user_upload.html', context)


def ranking_action(request):
    context={}
    return render(request, 'virtualTravel/ranking.html', context)

def foodPage_action(request):
    if request.method == 'GET':
        context = {}
        user_profile = request.user.profile
        current_travel = user_profile.current_travel.all()[0]
        routes = current_travel.route.split(" ")
        current_city_id = int(routes[current_travel.current_stop])
        current_city = City.objects.get(id=current_city_id)
        context['current_city'] = current_city
        print(current_city.name)
        return render(request, 'virtualTravel/food.html', context)


def food_search_action(request):
    if request.method == 'POST':
        user_profile = request.user.profile
        current_travel = user_profile.current_travel.all()[0]
        routes = current_travel.route.split(" ")
        current_city_id = int(routes[current_travel.current_stop])
        current_city = City.objects.get(id=current_city_id)
        arr= request.POST.getlist('food_preference')
        print('food_preference')
        print(arr)
        filters= ','.join(arr)
        print (filters)
        # request.session['search'] = request.POST['search']
        request.session['location_input'] = current_city.name
        request.session['search_results'] = query_api(filters, request.session['location_input'])
        return redirect(reverse('food_result'))
    else:
        return redirect(reverse('travel'))

def food_result_action(request):
    search_results = request.session['search_results']
    # random=randint(1,20)
    # print(random)
    # search_results=search_results['businesses'][0]
    # print(search_results)
    context = {
        'places_list': search_results
    }
    user_profile = request.user.profile
    current_travel = user_profile.current_travel.all()[0]
    routes = current_travel.route.split(" ")
    current_city_id = int(routes[current_travel.current_stop])
    current_city = City.objects.get(id=current_city_id)
    context['current_city'] = current_city
    context['current_page'] = 'list-Food-list'

    # print(search_results)
    return render(request, 'virtualTravel/traveling.html', context)



