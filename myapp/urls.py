from django.contrib import admin
from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='index'),
    path('signup',views.signup,name='signup'),
    path('home',views.home,name='home'),
    path('signin',views.signin,name="signin"),
    path('activate/<uidb64>/<token>',views.activate,name="activate")
]