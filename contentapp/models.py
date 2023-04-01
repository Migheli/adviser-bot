from django.db import models
from pathlib import Path

# Create your models here.


class Chapter(models.Model):
    name = models.CharField(
        'Название',
        max_length=50
    )

    description = models.TextField(
        'Описание',
        max_length=3000,
        blank=True
        )

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'

    def is_with_picture(self):
        return len(self.pictures.all()) >= 1 

    def is_with_file(self):
        return len(self.files.all()) >= 1    

    def is_multi_media(self):
        return self.is_with_picture and self.is_with_file

    def __str__(self):
        return self.name


class Article(models.Model):
    name = models.CharField(
        'Название',
        max_length=50
    )

    text = models.TextField(
        'Текст',
        max_length=3000
    )

    chapter = models.ForeignKey(
	    Chapter,
		verbose_name='Раздел',
		related_name='articles',
		blank=True,
        null=True,
		on_delete=models.SET_NULL,
	)


    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def is_with_picture(self):
        return len(self.pictures.all()) >= 1 

    def is_with_file(self):
        return len(self.files.all()) >= 1    

    def is_multi_media(self):
        return self.is_with_picture and self.is_with_file

    def __str__(self):
        return self.name


class Image(models.Model):
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name='Приоритет'
    )

    picture = models.ImageField('Фото', upload_to='media')
    
    article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        verbose_name='Статья',
        related_name='pictures',
        blank=True,
        null=True
    )

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        verbose_name='Раздел',
        related_name='pictures',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['priority']
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'


    def __str__(self):
        return Path(self.picture.name).name


class Attachment(models.Model):
    priority = models.PositiveIntegerField(
        default=0,
        verbose_name='Приоритет'
    )

    file = models.FileField('Фaйл-приложение', upload_to='media')
    
    article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        verbose_name='Статья',
        related_name='files',
        blank=True,
        null=True
    )

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.SET_NULL,
        verbose_name='Раздел',
        related_name='files',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['priority']
        verbose_name = 'Приложение'
        verbose_name_plural = 'Приложения'


    def __str__(self):
        return Path(self.file.name).name