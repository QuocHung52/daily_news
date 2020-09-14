from show_news.models import Articles, Source_Of_News
from django.core.management.base import BaseCommand
from show_news.helper import _get_content, _get_news


class Command(BaseCommand):
    help = "update database"
    # define logic of command

    def handle(self, *args, **options):
        pages = Source_Of_News.objects.all()
        number_of_articles = 0
        for page in pages:
            number_of_articles += _get_news(page.page_url, page.page_name)
        self.stdout.write('Update completed with ' +
                          str(number_of_articles) + ' new articles')
