from django.urls import path
from . import views

app_name = 'show_news'

urlpatterns = [
    path('', views.show_news, name='show_news'),
    path('source/<str:source>', views.view_source, name='view_source'),
    path('details/<int:pk>', views.news_details, name='news_details'),
    path('settings/', views.settings, name='settings'),
    path('search/', views.search, name='search'),
]
