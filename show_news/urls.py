from django.urls import path
from . import views

app_name = 'show_news'

urlpatterns = [
    path('', views.show_news, name='show_news'),
    path('get_content/', views.get_content, name='get_content'),
]
