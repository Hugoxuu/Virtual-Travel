from django.db import models
from django.contrib.auth.models import User

# City Model
class City(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=1000,
                                    default="No description Added")
    price = models.IntegerField()
    picture_url = models.CharField(max_length=500)

    def __str__(self):
        return 'City(id=' + str(self.id) + '), ' + self.name

# City Pictures
class Picture(models.Model):
    image = models.FileField()
    content_type = models.CharField(max_length=50)
    city = models.ForeignKey(City, on_delete=models.PROTECT)

    def __str__(self):
        return 'Picture(id=' + str(self.id) + ') of city ' + self.city.name


# City Sites
class Site(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=1000,
                                    default="No description Added")
    picture_url = models.CharField(max_length=500)
    
    city = models.ForeignKey(City,on_delete=models.PROTECT)
    def __str__(self):
        return 'Site(id=' + str(self.id) + '), ' + self.name

# User Profile
class Profile(models.Model):
    user  = models.OneToOneField(User, on_delete=models.PROTECT,related_name="profile")
    bio   = models.CharField(max_length=200,blank=True)
    picture = models.FileField(blank=True, null=True)
    content_type = models.CharField(max_length=50,blank=True)

    # Amount of gold that a user has
    gold = models.IntegerField(default=0)
    # Collection of cities that a user has access to (unlocked)
    city_pool = models.ManyToManyField(City, related_name="unlocked_user")
    # Collection of cities that a user has travelled to
    city_collection = models.ManyToManyField(City, related_name="collected_user", blank=True)

    def __str__(self):
        return 'Profile(id=' + str(self.id) + ') of User ' + self.user.username

# Travel History in User Profile
class Travel(models.Model):
    num_of_stops = models.IntegerField() # number of stops in this trip
    current_stop = models.IntegerField(default=0) # indicates where this user is currently at
    gold_earned = models.IntegerField(default=0)
    route = models.CharField(max_length=2000) # format: "city_id1 city_id2 city_id3"
    date = models.DateTimeField()
    made_by = models.ForeignKey(Profile,on_delete=models.CASCADE,related_name="past_travel")
    current_user = models.ForeignKey(Profile,on_delete=models.PROTECT,blank=True,null=True,unique=True,related_name="current_travel")
    
    def __str__(self):
        return 'Travel(id=' + str(self.id) + '), made by User: ' + self.made_by.user.username
                # + ', route: ' + self.route, + ', current stop: ' + str(self.current_stop)

# Quiz Question in City Model
class Quiz(models.Model):
    quiz_text = models.CharField(max_length=100)
    quiz_option_1 = models.CharField(max_length=50)
    quiz_option_2 = models.CharField(max_length=50)
    quiz_option_3 = models.CharField(max_length=50,blank=True)
    quiz_option_4 = models.CharField(max_length=50,blank=True)
    quiz_answer = models.IntegerField()
    quiz_city = models.ForeignKey(City,on_delete=models.PROTECT)
    # All users that have correctly answer this quiz
    quiz_users = models.ManyToManyField(Profile,blank=True)

    def __str__(self):
        return 'Quiz question(id=' + str(self.id) + ') of City ' + self.quiz_city.name



