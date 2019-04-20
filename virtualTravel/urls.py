from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),

    path('', views.travel_select_action, name='homepage'),

    path('profile', views.profile_action, name = 'profile'),
    path('photo', views.get_photo, name='photo'),

    path('citystore', views.store_action, name = 'store'),
    path('travel',views.travel_action,name = 'travel'),
    path('buyCity', views.buyCity_action, name = 'buyCity'),
    path('searchCity', views.searchCity_action, name = 'searchCity'),
    path('show_grades',views.show_grades,name = 'show_grades'),
    path('refresh-map',views.refresh_map,name = 'refresh-map'),

    path('user_upload', views.user_upload, name = 'user_upload'),
    path('cityMap',views.cityMap,name = 'cityMap'),
    path('refresh_cityMap',views.refresh_cityMap,name = 'refresh_cityMap'),

    path('user_ranking', views.ranking_action, name = 'user_ranking'),
    path('food_search', views.food_search_action, name = 'food_search'),
    path('food_result', views.food_result_action, name = 'food_result'),
    path('foodPage', views.foodPage_action, name = 'foodPage'),
]
