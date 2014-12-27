from django.db import models


class Book(models.Model):
    book_id = models.CharField(max_length=200, db_index=True, unique=True)
    author = models.CharField(max_length=30)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200)
    size = models.BigIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    path = models.CharField(max_length=500)


class BookImage(models.Model):
    src = models.CharField(max_length=500)
    path = models.CharField(max_length=500, null=True, blank=True)
    book = models.ForeignKey(Book)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
