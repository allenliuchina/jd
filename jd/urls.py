"""jd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from .settings import BASE_DIR
import os
from good.views import Search
from django.conf import settings

urlpatterns = [
    path('', include('good.urls')),
    path('search/', Search()),
    path('admin/', admin.site.urls),
    path('user/', include('user.urls')),
    path('cart/', include('cart.urls')),
    path('order/', include('order.urls')),
    re_path(r'image/(?P<path>.*)$', serve, {'document_root': os.path.join(BASE_DIR, 'image')})

]
# if not settings.DEBUG or settings.ALLOWED_HOSTS:
#     urlpatterns += [re_path(r'static/(?P<path>.*)$', serve, {'document_root': os.path.join(BASE_DIR, 'static')}), ]
