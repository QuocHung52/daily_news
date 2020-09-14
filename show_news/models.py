from django.db import models

# Create your models here.


class Articles(models.Model):
    page_name = models.CharField(max_length=250)
    url = models.CharField(max_length=250, unique=True)
    title = models.CharField(max_length=250, unique=True)
    image_content_url = models.CharField(max_length=250)
    author = models.CharField(max_length=250)
    published_time = models.CharField(max_length=250)

    def __str__(self):
        return self.url


class Source_Of_News(models.Model):
    page_name = models.CharField(max_length=100, unique=True)
    page_url = models.CharField(max_length=250)

    def __str__(self):
        return self.page_name


class Skip_List(models.Model):
    page_name = models.CharField(max_length=100)
    url = models.CharField(max_length=250)

    def __str__(self):
        return self.url
