from django.urls import path, re_path
from . import views
from django.views.static import serve
import os
from django.conf import settings

app_name = 'good'
urlpatterns = [
    path('list/<int:id>/<int:num>/', views.good_list, name='list'),
    path('', views.index, name='index'),
    path('detail/<int:id>/', views.detail, name='detail'),
    # path('test/', views.test, name='test')
    # re_path(r'^image/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'image')})

]
