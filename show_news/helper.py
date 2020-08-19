from .models import Articles
from .content_extractor import *
from .extractors import *


def _get_content(url):
    news_extractor = Extractor(url)
    news_extractor.extract_content()
    return news_extractor


def _update_database(articles_object, news_extractor):
    articles_object.content = news_extractor.content
    articles_object.url = news_extractor.url
    articles_object.title = news_extractor.title
    for x in news_extractor.authors:
        articles_object.author = ''.join(x + ', ')
    if len(articles_object.author) > 3:
        if articles_object.author[-2] == ',':
            articles_object.author = articles_object.author[0:-2]

    articles_object.image_content_url = news_extractor.img_of_content_url
    articles_object.published_time = news_extractor.published_time
    articles_object.save()
