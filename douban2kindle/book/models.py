from django.db import models


class Book(models.Model):
    book_id = models.CharField(max_length=200, db_index=True, unique=True)
    author = models.CharField(max_length=30)
    title = models.CharField(max_length=200, db_index=True)
    subtitle = models.CharField(max_length=200, null=True, blank=True)
    size = models.BigIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    path = models.CharField(max_length=500, null=True, blank=True)
    cover = models.CharField(max_length=500, null=True, blank=True)


class BookImage(models.Model):
    src = models.CharField(max_length=500, db_index=True)
    path = models.CharField(max_length=500, null=True, blank=True)
    book = models.ForeignKey(Book, related_name='images')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
