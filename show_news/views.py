from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Articles, Source_Of_News
from .helper import _get_content, _update_database, _get_news
from .extractors import *

# Create your views here.


def show_news(request):
    displayed_news = {}
    pages = Source_Of_News.objects.all()
    start_id_news = 0
    end_id_news = 4
    if 'view_older_news' in request.GET:
        start_id_news = int(request.GET['current_value'])
        end_id_news = start_id_news + 4

    for page in pages:
        if 'view_older_news' not in request.GET:
            _get_news(page.page_url, page.page_name)
        articles_objects = Articles.objects.filter(page_name=page.page_name).order_by('pk').reverse()[start_id_news:end_id_news]
        for item in articles_objects:
            if not item.image_content_url:
                news_extractor = Extractor(item.url)
                html = news_extractor.download_page()
                image_content_url = news_extractor.get_img_of_content_url(html)
                item.image_content_url = image_content_url
                item.save()

        displayed_news[page.page_name] = articles_objects

    context = {'displayed_news': displayed_news, 'mode': 'show_news', 'current_number_news': end_id_news}
    return render(request, 'show_news/daily_news.html', context)


def news_details(request, pk):
    item = Articles.objects.get(pk=pk)
    message = ''
    if not item.content:
        news_extractor = _get_content(item.url)
        message = news_extractor.messages
        _update_database(item, news_extractor)

    context = {'message': message, 'object': item}

    return render(request, 'show_news/news_details.html', context)


def search_news(request):
    search_query = request.GET.get('search_box')
    message = ''
    result = Articles.objects.filter(title__icontains=search_query)

    if not result:
        message = 'Cannot find \'' + search_query + '\' in today''s news'
        result = None

    context = {'result': result, 'message': message, 'mode': 'show_search_result', 'keyword': search_query}
    return render(request, 'show_news/daily_news.html', context)


def source_of_news(request):
    pages = Source_Of_News.objects.all()
    context = {'object': pages}

    if request.method == 'POST':
        if 'add' in request.POST:
            print('request.POST')
            url = request.POST['url']
            if "https://" not in url:
                message = 'The URL is not valid'
                return render(request, 'show_news/source_of_news.html', {
                    'object': pages, 'error_message': message})

            elif Source_Of_News.objects.filter(page_url=url):
                message = url + ' has already been in the database'
                return render(request, 'show_news/source_of_news.html', {
                    'object': pages, 'error_message': message})
            else:
                item = Source_Of_News()
                item.page_url = url
                item.page_name = url.split('.')[1].title()
                item.save()

            return redirect(request.path_info)
        if 'remove_page' in request.POST:
            page_to_remove = request.POST.getlist('item')
            for page in page_to_remove:
                data = Articles.objects.filter(page_name=page)
                data.delete()
                data = Source_Of_News.objects.filter(page_name=page)
                data.delete()
                return redirect(request.path_info)
    return render(request, 'show_news/source_of_news.html', context)


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
