from django.shortcuts import render
from .models import Articles
from .helper import _get_content, _update_database
from .extractors import *

# Create your views here.


def show_news(request):
    return render(request, 'show_news/daily_news.html')


def get_content(request):
    if request.method == 'POST':
        url = request.POST['url']
        message = ''
        news_object = None
        type_of_news = ''
        if not url:
            message = "You didn't input anything."
            return render(request, 'show_news/get_content.html', {
                'error_message': message})
        if "https://" not in url:
            message = 'The URL is not valid'
            return render(request, 'show_news/get_content.html', {
                'error_message': message})

        if Articles.objects.filter(url=url).exists():
            news_object = Articles.objects.get(url=url)
            if news_object.content:
                message = ''
            else:
                news_extractor = _get_content(url)
                message = news_extractor.messages
                _update_database(news_object, news_extractor)

        else:
            news_extractor = _get_content(url)
            message = news_extractor.messages

            news_object = Articles()
            _update_database(news_object, news_extractor)
            # type_of_news = get_type_of_news([news_object.title])

        return render(request, 'show_news/get_content.html', {
            'error_message': message, 'news_object': news_object})
    return render(request, 'show_news/get_content.html')
