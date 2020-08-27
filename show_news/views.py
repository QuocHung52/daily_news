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
    end_id_news = 5
    if 'view_older_news' in request.GET:
        start_id_news = int(request.GET['current_value'])
        end_id_news = start_id_news + 5

    for page in pages:
        articles_objects = Articles.objects.filter(page_name=page.page_name).order_by('pk').reverse()[start_id_news:end_id_news]

        for item in articles_objects:
            if not item.image_content_url:
                image_extractor = Extractor(item.url)
                html = image_extractor.download_page()
                item.image_content_url = image_extractor.get_img_of_content_url(html)
                item.save(update_fields=['image_content_url'])
        displayed_news[page.page_name] = articles_objects

    context = {'displayed_news': displayed_news, 'mode': 'show_news', 'current_number_news': end_id_news}
    return render(request, 'show_news/daily_news.html', context)


def news_details(request, pk):
    item = Articles.objects.get(pk=pk)
    message = ''
    get_image_content_status = False if item.image_content_url else True
    if not item.content:
        news_extractor = _get_content(item.url, get_image_content_status)
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

            url = request.POST['url']
            if "https://" not in url:
                message = 'The URL is not valid'
                return render(request, 'show_news/source_of_news.html', {
                    'object': pages, 'message': message})
            else:
                try:
                    item = Source_Of_News.objects.create(
                        page_url=url,
                        page_name=url.split('.')[1].title()
                    )
                except Exception as e:
                    message = url + ' has already been in the database'
                    return render(request, 'show_news/source_of_news.html', {
                        'object': pages, 'message': message})

            number_of_articles = _get_news(page_url=url,
                                           page_name=url.split('.')[1].title(),
                                           get_image_content_status=False)

            message = 'Your newsfeed is updated with ' + str(number_of_articles) + ' new articles from ' + url

            return render(request, 'show_news/source_of_news.html', {
                'object': pages, 'message': message})
        if 'remove_page' in request.POST:
            page_to_remove = request.POST.getlist('item')
            for page in page_to_remove:
                data = Source_Of_News.objects.filter(page_name=page)
                data.delete()
                return redirect(request.path_info)
    return render(request, 'show_news/source_of_news.html', context)


def get_content(request):
    if request.method == 'POST':
        url = request.POST['url']
        message = ''
        # type_of_news = ''
        if not url:
            message = "You didn't input anything."
            return render(request, 'show_news/get_content.html', {
                'error_message': message})
        elif "https://" not in url:
            message = 'The URL is not valid'
            return render(request, 'show_news/get_content.html', {
                'error_message': message})

        else:
            news_object = _get_content(url)
            message = news_object.messages
            # type_of_news = get_type_of_news([news_object])

        return render(request, 'show_news/get_content.html', {
            'error_message': message, 'news_object': news_object})
    return render(request, 'show_news/get_content.html')
