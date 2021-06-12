from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^stock_list$', views.stock_list, name='stock_list'),
    url(r'^update$', views.update, name='update')
]
