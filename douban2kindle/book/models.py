from django.db import models


class Book(models.Model):
    book_id = models.CharField(max_length=200)
    author = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    size = models.BigIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
