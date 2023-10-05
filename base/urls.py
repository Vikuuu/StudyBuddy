from django.urls import path
from . import views

urlpatterns = [
    #url for login and logout
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('register/', views.registerPage, name='register'),

    path('' , views.home , name="home"),

    #url for opening the page of the selected Topic Room dynamically
    path('room/<str:pk>/' , views.room , name="room"),

    path('profile/<str:pk>/', views.userProfile , name = "user-profile"),

    #url for opening the page of the Creating room Form
    path('create-room/' , views.createRoom , name='create-room'),

    #url for updating the rooms
    path('update-room/<str:pk>/' , views.updateRoom , name='update-room'),

    path('delete-room/<str:pk>/' , views.deleteRoom , name='delete-room'),

    path('delete-message/<str:pk>/' , views.deleteMessage , name='delete-message'),

    path('update-user/' , views.updateUser , name='update-user'),

    path('topics/' , views.topicsPage , name='topics'),

    path('activity/' , views.activityPage , name='activity'),
]