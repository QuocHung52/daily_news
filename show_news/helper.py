from show_news.models import Articles, Skip_List
from .content_extractor import *
from .extractors import *


def _get_content(url, get_image_content_status=True):
    news_extractor = Extractor(url)
    news_extractor.extract_content(get_image_content_status)
    return news_extractor


def _update_database(articles_object, news_extractor):
    articles_object.content = news_extractor.content
    articles_object.author = news_extractor.authors
    if not articles_object.image_content_url:
        articles_object.image_content_url = news_extractor.img_of_content_url

    articles_object.published_time = news_extractor.published_time
    articles_object.save()


def _get_news(page_url, page_name, get_image_content_status=True):
    news_extractor = Extractor(page_url)
    number_of_articles, articles = news_extractor.extract_article()

    for url in reversed(list(articles.keys())):
        title = articles[url]
        if not Skip_List.objects.filter(url=url).exists() and not Articles.objects.filter(url=url).exists():
            if not get_image_content_status:
                image_content_url = ''
            else:
                image_extractor = Extractor(url)
                html = image_extractor.download_page()
                image_content_url = image_extractor.get_img_of_content_url(html)
            try:
                Articles.objects.create(
                    page_name=page_name,
                    url=url,
                    title=title,
                    image_content_url=image_content_url
                )
            except:
                pass
        else:
            number_of_articles -= 1
    return number_of_articles
