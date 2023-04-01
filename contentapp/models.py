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
        on_delete=models.CASCADE,
        verbose_name='Статья',
        related_name='pictures'
    )

    class Meta:
        ordering = ['priority']
        verbose_name = 'Изображение'
        verbose_name_plural = 'Изображения'

    def __str__(self):
        return Path(self.picture.name).name