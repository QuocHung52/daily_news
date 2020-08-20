from .models import Articles
from .content_extractor import *
from .extractors import *

list_of_exception = [
    'https://www.reuters.com/info/disclaimer',
    'https://www.reuters.com/article/us-reuters-editorial-leadership/reuters-editorial-leadership-idUSKBN1KE2SD',
    'https://www.reutersagency.com/en/about/brand-attribution-guidelines/',
    'https://bloxcms.com',
    'https://braiservices.newscyclecloud.com/cmo_bra-c-cmdb-01/subscriber/web/signin.html',
    'https://www.vox.com/2018/12/7/18113237/ethics-and-guidelines-at-vox-com',
]


def _get_content(url):
    news_extractor = Extractor(url)
    news_extractor.extract_content()
    return news_extractor


def _get_news(page_url, page_name):
    news_extractor = Extractor(page_url)
    number_of_articles, articles = news_extractor.extract_article()

    data = Articles.objects.filter(page_name=page_name).order_by('pk').reverse()[:100]
    current_title = [x.title for x in data]

    for url, title in articles.items():
        if url not in list_of_exception and not _is_duplicate(current_title, title):
            current_title.append(title)
            item = Articles()
            item.page_name = page_name
            item.url = url
            item.title = title
            item.save()


def _is_duplicate(data, value):
    return True if value in data else False


def _update_database(articles_object, news_extractor):
    articles_object.content = news_extractor.content
    for x in news_extractor.authors:
        articles_object.author = ''.join(x + ', ')
    if len(articles_object.author) > 3:
        if articles_object.author[-2] == ',':
            articles_object.author = articles_object.author[0:-2]

    articles_object.image_content_url = news_extractor.img_of_content_url
    articles_object.published_time = news_extractor.published_time
    articles_object.save()
