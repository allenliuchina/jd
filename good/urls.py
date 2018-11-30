from django.urls import path, re_path
from . import views
from jd.settings import BASE_DIR
from django.views.static import serve
import os

app_name = 'good'
urlpatterns = [
    path('list/<int:id>/<int:num>/', views.list, name='list'),
    path('', views.index, name='index'),
    path('detail/<int:id>/', views.detail, name='detail'),
    # re_path(r'^image/(?P<path>.*)$', serve, {'document_root': os.path.join(BASE_DIR, 'image')})

]

