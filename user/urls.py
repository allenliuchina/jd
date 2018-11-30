from django.urls import path, re_path

from . import views

app_name = 'user'
urlpatterns = [
    path('user/', views.user, name='user'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('order/<int:page>', views.order, name='order'),
    path('logout/', views.log_out, name='logout'),
    path('address/', views.address, name='address'),
    path('activate/<token>/', views.activate, name='activate'),
]
