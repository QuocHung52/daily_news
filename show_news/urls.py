from django.urls import path
from . import views

app_name = 'show_news'

urlpatterns = [
    path('', views.show_news, name='show_news'),
    path('details/<int:pk>', views.news_details, name='news_details'),
    path('source_of_news/', views.source_of_news, name='source_of_news'),
    path('search_news/', views.search_news, name='search_news'),
    path('get_content/', views.get_content, name='get_content'),
]
