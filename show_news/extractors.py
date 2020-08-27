import requests
import bs4
import re
import logging
from .content_extractor import *
from urllib.parse import urljoin


class Extractor:
    """docstring for Extractor"""

    def __init__(self, url, parser=None):
        self.MIN_TITLE_LENGTH = 26
        self.LIMIT_TIME_TAG_TO_FIND = 3
        self.DATE_REGEX = r'(((\w{3})|([0-3]?\d))(\.|\/|,|\s|\-|_){0,2}([0-3]?\d)(\.|\/|,|\s|\-|_){0,2}(19|20)\d{2}(\.|\/|,|\s|\-|_){0,3})'
        self.DATE_REGEX_BACKWARD = r'(19|20)\d{2}(\.|\/|,|\s|\-|_){0,3}(\.|\/|,|\s|\-|_){0,2}([0-3]?\d)(\.|\/|,|\s|\-|_){0,2}((\w{3})|([0-3]?\d))'
        self.TIME_REGEX = r'((\d{1,2})(:|\.)(\d{2})(\s)?(([aA]|[pP])([mM]))?((\s)?(\w{3})?))?'
        self.REQUEST_TIMEOUT = 1

        self.url = url
        self.html = None
        if not parser:
            self.parser = 'lxml'
        self.title = ''
        self.content = ''
        self.published_time = ''
        self.img_of_content_url = ''
        self.authors = []
        self.articles = {}
        self.messages = []

    def extract_content(self, get_image_content_status=True):
        url = self.url
        html = self.download_page()
        if not html:
            self.messages = 'Cannot get response from ' + self.url
            return
        self.html = html

        title = self.get_title(html)
        if not title:
            logging.warning('Cannot get title from article')
        self.title = title

        authors = self.get_authors(html)
        if not authors:
            logging.warning('Cannot get authors from article')
        self.authors = authors

        published_time = self.get_published_time(html)
        if not published_time:
            logging.warning('Cannot get publised date from article')
        self.published_time = published_time

        if get_image_content_status:
            img_of_content_url = self.get_img_of_content_url(html)
            if not img_of_content_url:
                logging.warning('Cannot get main image url from article')
            self.img_of_content_url = img_of_content_url

        content = self.get_content(html)
        if not content:
            logging.warning('Cannot get content from article')
        self.content = content

    def download_page(self):
        url = self.url
        response = self.get_response(url)
        if not response:
            logging.warning('Cannot get response from %s' % url)
            return ''

        html = bs4.BeautifulSoup(response.content, self.parser)
        return html

    def get_response(self, url):
        """HTTP response code"""
        try:
            response = requests.get(url, timeout=self.REQUEST_TIMEOUT)
        except requests.exceptions.RequestException as err:
            logging.exception(err)
            return ''
        return response

    def get_title(self, html):
        title = []
        # Find with meta tag
        value = re.compile(r'[tT]itle')
        for attr in ['property', 'name']:
            matched_tag = html.find_all('meta', attrs={attr: value})
            for tag in matched_tag:
                title.append(tag.attrs['content'])

        if not title:
            title_tag = html.find('title')
            title = title_tag.text.strip()

        def unique_check(title_list):
            seen = set()
            seen_add = seen.add
            return [x.title() for x in title_list if not (x in seen or seen_add(x))]

        return unique_check(title)[0]

    def get_authors(self, html):
        authors = []
        matched_tag = []

        # Find with meta tag
        value = re.compile(r'author')
        for attr in ['property', 'name']:
            matched_tag = html.find_all('meta', attrs={attr: value})
            for tag in matched_tag:
                authors.append(tag.attrs['content'])

        # Try harder
        if not authors:
            attrs = ['rel', 'class', 'href', 'name', 'id', 'itemprop']
            value = re.compile('[\w|\-|\/|\.]?([aA]uthor)|([eE]ditor)[\w|\-|\/|\.]?')
            matched_tag = []

            for attr in attrs:
                scanned_tag = html.find_all('a', attrs={attr: value})
                matched_tag.extend(scanned_tag)

            if matched_tag:
                for tag in matched_tag:
                    text_inside = tag.text.strip()
                    text_inside = re.sub(' [ \t]+', ' ', text_inside)

                    # Remove words like "By", "From" and delimiters: "-","," from author names
                    if 0 < len(text_inside) < 100:
                        names = re.sub('([bB][yY])|([fF][rR][oO][mM])[\s\:]', '', text_inside)
                        names = re.split('[\-\,]', names)
                        authors.extend(names)

            else:
                authors = ''

        def unique_check(author_list):
            seen = set()
            seen_add = seen.add
            return [x.title() for x in author_list if not (x in seen or seen_add(x))]

        def valid_check_author(author_list):
            authors = ''
            for author in author_list:
                if re.search(r'(\d)|([hH]ttp)', author):
                    author_list.remove(author)
            author_list = unique_check(author_list)

            for x in author_list:
                authors = ''.join(x + ', ')
            if len(authors) > 3:
                if authors[-2] == ',':
                    authors = authors[0:-2]
            return authors

        return valid_check_author(authors)

    def get_img_of_content_url(self, html):
        if not html:
            return ''
        value = 'og:image'
        img_of_content_url = ''
        for attr in ['property', 'name']:
            matched_tag = html.find('meta', attrs={attr: value})
            if matched_tag:
                img_of_content_url = matched_tag.attrs['content']
                break
        if not img_of_content_url:
            value = re.compile(r'img_src|image_src')
            matched_tag = html.find('link', attrs={'rel': value})
            if matched_tag:
                img_of_content_url = matched_tag.attrs['href']
        if img_of_content_url:
            return urljoin(self.url, img_of_content_url)
        return ''

    def get_published_time(self, html):
        # Find time started with date or month: Ex: 24-12-2020
        DATE_AND_TIME = self.DATE_REGEX + self.TIME_REGEX
        # Find time started with year: Ex: 2020-12-24
        DATE_AND_TIME_BACKWARD = self.DATE_REGEX_BACKWARD + self.TIME_REGEX

        def extract_time(time_tag):
            date_time_match = re.search(DATE_AND_TIME, time_tag.decode())

            if date_time_match:
                return date_time_match.group(0).strip()

            # try to look backward
            else:
                date_time_match = re.search(DATE_AND_TIME_BACKWARD, time_tag.decode())
                if date_time_match:
                    return date_time_match.group(0).strip()
            return ''

        # Get published time by searching in the tag name "time"
        time_tag = html.find_all('time')
        for tag in time_tag:
            published_time = extract_time(tag)
            if published_time:
                return published_time

        # Get published time by searching in the tag name "meta"
        attrs = ['property', 'itemprop', 'name']
        pattern = re.compile('[pP]ublish')
        for attr in attrs:
            time_tag = html.find_all('meta', attrs={attr: pattern})
            for tag in time_tag:
                published_time = extract_time(tag)
                if published_time:
                    return published_time

        return ''

    def get_content(self, html):
        cleaned_html = self.clean_tags(html)

        body = cleaned_html.find('body')
        extractor = Content_Extractor.create(body)
        content = extractor.extract()
        return content

    def clean_tags(self, html):
        # Unwarp tags
        merging_tags = ['p', 'br', 'li', 'table', 'tbody', 'tr', 'td', 'theader', 'tfoot']
        tags = html.find_all(merging_tags)
        for tag in tags:
            tag.unwrap()

        # Remove tags:
        remove_tag = ['head', 'script', 'link', 'style', 'form', 'option', 'header', 'footer', 'nav', 'noscript', 'aside']
        tags = html.find_all(remove_tag)
        for tag in tags:
            tag.decompose()

        # Remove hidden tags:
        for hidden in html.find_all(style=re.compile(r'display:\s*none')):
            hidden.decompose()

        return html

    def extract_article(self):
        url = self.url
        html = self.download_page()
        if not html:
            return
        self.html = html

        if url[-1] == '/':
            url = url[:-1]

        article_tags = self.get_article_tags(html, url)

        if not article_tags:
            logging.warning('Cannot get any news from %s' % url)
            return ''

        articles = {}
        article_url = []
        article_title = []
        number_of_articles = len(article_tags)
        for tag in article_tags:
            article_url = urljoin(self.url, tag['href'])
            article_title = tag.text.strip()
            articles[article_url] = article_title

        return number_of_articles, articles

    def get_article_tags(self, html, url):
        article_tags = []
        tags = html.find_all("a")
        for tree in tags:
            if 'href' in tree.attrs and tree.string:
                if len(tree.string.strip()) > self.MIN_TITLE_LENGTH:
                    article_tags.append(tree)

        return article_tags
