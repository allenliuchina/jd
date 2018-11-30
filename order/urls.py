from django.urls import path
from order import views

app_name = 'order'
urlpatterns = [
    path('', views.before_commit, name='commit'),
    path('commit/', views.commit_order, name='create'),
    path('pay/', views.pay_order, name='pay'),
    path('pay_check/', views.pay_check, name='pay_check'),
    path('cancel/<int:id>/', views.cancel, name='cancel'),
    path('fast_buy/<int:id>/<int:count>/', views.fast_buy, name='fast_buy'),
    path('commit/<int:id>/<int:count>',views.fast_commit,name='fast_commit')
]
