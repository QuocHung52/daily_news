from django.shortcuts import render

# Create your views here.


def show_news(request):
    return render(request, 'show_news/daily_news.html')


def get_content(request):
    return render(request, 'show_news/get_content.html')
