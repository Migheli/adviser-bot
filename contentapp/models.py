from django.db import models

# Create your models here.


class Chapter(models.Model):
    name = models.CharField(
        'Название',
        max_length=50
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
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
	)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def __str__(self):
        return self.name
