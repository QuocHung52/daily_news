from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Articles, Source_Of_News
from .helper import _get_content, _get_news
from .extractors import *
import time
# Create your views here.

ARTICLE_PER_PAGE = 6


def show_news(request):
    displayed_news = {}
    all_sources = Source_Of_News.objects.all()
    page = 1
    start_id, end_id = 0, ARTICLE_PER_PAGE
    if 'view-more' in request.GET:
        page = int(request.GET['page']) + 1
        start_id = page*ARTICLE_PER_PAGE
        end_id = start_id + ARTICLE_PER_PAGE

    for source in all_sources:
        articles_objects = Articles.objects.filter(page_name=source.page_name).order_by(
            'pk').reverse()[start_id:end_id]

        displayed_news[source.page_name] = articles_objects

    context = {'displayed_news': displayed_news, 'page': page}
    return render(request, 'show_news/daily_news.html', context)


def view_source(request, source):
    NEWS_PER_PAGE = ARTICLE_PER_PAGE*2
    all_sources = Source_Of_News.objects.all()
    page = 1
    start_id, end_id = 0, NEWS_PER_PAGE
    if 'view-more' in request.GET:
        page = int(request.GET['page']) + 1
        start_id = page*NEWS_PER_PAGE
        end_id = start_id + NEWS_PER_PAGE

    articles_objects = Articles.objects.filter(
        page_name=source).order_by('pk').reverse()[start_id:end_id]

    context = {'displayed_news': articles_objects,
               'page': page, 'page_name': source, 'all_sources': all_sources}
    return render(request, 'show_news/source.html', context)


def news_details(request, pk):
    all_sources = Source_Of_News.objects.all()
    item = Articles.objects.get(pk=pk)
    related_news = Articles.objects.filter(page_name=item.page_name).filter(
        pk__lt=pk).order_by('pk').reverse()[0:4]

    news_extractor = _get_content(item.url)
    try:
        item.title = news_extractor.title
        item.image_content_url = news_extractor.img_of_content_url
        item.author = news_extractor.authors
        item.published_time = news_extractor.published_time
        item.save()
    except:
        pass

    message = news_extractor.messages

    context = {'message': message,
               'object': item,
               'content': news_extractor.content,
               'related_news': related_news,
               'all_sources': all_sources}

    return render(request, 'show_news/news_details.html', context)


def search(request):
    search_query = request.GET.get('search_box')
    all_sources = Source_Of_News.objects.all()
    result = Articles.objects.filter(title__icontains=search_query)
    message = 'Result for \"' + search_query + '\"'

    if not result:
        message = 'No result for \"' + search_query
        result = None

    context = {'result': result,
               'message': message,
               'all_sources': all_sources}

    return render(request, 'show_news/search.html', context)


def settings(request):
    pages = Source_Of_News.objects.all()
    context = {'object': pages}

    if request.method == 'POST':
        if 'add' in request.POST:
            url = request.POST['url']
            if len(pages) > 3:
                message = "Cannot add more sources due to the limitation of the databse. I am sorry!"
                return render(request, 'show_news/settings.html', {
                    'object': pages, 'message': message})
            if "https://" not in url:
                message = 'The URL is not valid. Perhaps you mean ' + 'https://www.' + url
                return render(request, 'show_news/settings.html', {
                    'object': pages, 'message': message})
            else:
                number_of_articles = _get_news(page_url=url,
                                               page_name=url.split(
                                                   '.')[1].title(),
                                               get_image_content_status=False)
                if not number_of_articles:
                    message = 'Cannot get content from ' + url
                else:
                    try:
                        item = Source_Of_News.objects.create(
                            page_url=url,
                            page_name=url.split('.')[1].title()
                        )
                    except Exception as e:
                        message = url + ' has already been in the database'
                        return render(request, 'show_news/settings.html', {
                            'object': pages, 'message': message})

                    message = 'Your newsfeed is updated with ' + \
                        str(number_of_articles) + ' new articles from ' + url
            pages = Source_Of_News.objects.all()
            return render(request, 'show_news/settings.html', {
                'object': pages, 'message': message})
        if 'remove_page' in request.POST:
            page_to_remove = request.POST.getlist('item')
            print(page_to_remove, request.POST)
            for page in page_to_remove:
                data = Source_Of_News.objects.filter(page_name=page)
                data.delete()
                data = Articles.objects.filter(page_name=page)
                data.delete()
            return redirect(request.path_info)
    return render(request, 'show_news/settings.html', context)
