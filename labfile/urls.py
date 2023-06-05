from django.urls import path
from .views import file, dashboard, user_admin, profile, add_file, view_file, file_mod, login, add_user, profile_mod

urlpatterns = [
    path('files/', file, name='file'),
    path('dashboard/', dashboard, name='dashboard'),
    path('users/', user_admin, name='user_admin'),
    path('profil/', profile, name='profile'),
    path('add_file/', add_file, name='add_file'),
    path('view_file/', view_file, name='view_file'),
    path('file_mod/', file_mod, name='file_mod'),
    path('', login, name='login'),
    path('add_user/', add_user, name='add_user'),
    path('profile_mod/', profile_mod, name='profile_mod'),



]