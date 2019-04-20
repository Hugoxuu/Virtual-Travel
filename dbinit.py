from virtualTravel.models import *
from django.contrib.auth.models import User

# Create super user "admin|1234"
User.objects.filter(is_superuser=True).delete()

User.objects.create_superuser('admin', 'admin@example.com', '1234')

# Add cities
Site.objects.all().delete()
Quiz.objects.all().delete()
City.objects.all().delete()

# Add cities
with open('CityInfo/Cities.txt','r') as cities:
	for city in cities:
		fields = city.split('\t')
		new_city = City.objects.create(name=fields[0],price=int(fields[1]), 
						picture_url=fields[3])
		with open('CityInfo/'+fields[0]+'.txt','r') as description_file:
			description = ""
			for line in description_file:
				description += line
		new_city.description = description
		new_city.save()

# Add sites
with open('SiteInfo/Sites.txt','r') as sities:
	for site in sities:
		fields = site.split('\t')
		new_site = Site.objects.create(name=fields[0],
			city=City.objects.get(name=fields[1]), 
			picture_url=fields[2])
		with open('SiteInfo/'+fields[0]+'.txt','r') as description_file:
			description = ""
			for line in description_file:
				description += line
		new_site.description = description
		new_site.save()

# Add quizzes
with open('CityInfo/QuizQs.txt','r') as quizQs:
	for quizQ in quizQs:
		fields = quizQ.split('\t')
		quiz_city = City.objects.get(name=fields[0])
		new_question = Quiz(quiz_text=fields[1],quiz_city=quiz_city,
							quiz_answer=int(fields[2]),
							quiz_option_1=fields[3],quiz_option_2=fields[4])
		
		try:
			new_question.quiz_option_3=fields[5]
		except: # doesn't have option3
			pass
		try:
			new_question.quiz_option_4=fields[6]
		except: # has option 3, but doesn't have option4
			pass
		finally:
			new_question.save()
