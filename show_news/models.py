from django.db import models

# Create your models here.


class Articles(models.Model):
    page_name = models.CharField(max_length=250, default='')
    url = models.CharField(max_length=250, default='')
    title = models.CharField(max_length=250, default='')
    image_content_url = models.CharField(max_length=250, default='')
    author = models.CharField(max_length=250, default='')
    published_time = models.CharField(max_length=250, default='')
    content = models.TextField()

    def __str__(self):
        return self.url
