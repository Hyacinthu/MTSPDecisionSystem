from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'unlogged_homepage'),
    path('login/', views.login, name = 'login'),
    path('register/', views.register, name = 'register'),
    path('home/', views.home, name = 'home'),
    path('home/mtsp/', views.create_mtsp, name = 'create_mtsp'),
    path('home/history/', views.history, name= 'history'),
    path('home/self/', views.self, name = 'self'),
    path('home/logout/', views.logout, name = 'logout'),
    path('home/load_cities/', views.load_cities, name = 'load_cities'),
    path('home/show_result/', views.show_result, name = 'show_result'),
    path('home/help/', views.help, name = 'help'),
    path('home/history_if_no_history/', views.no_history, name = 'no_history'),
]
