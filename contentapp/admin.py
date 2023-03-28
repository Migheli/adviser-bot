from django.contrib import admin

from .models import Chapter, Article
# Register your models here.


@admin.register(Chapter)
class RestaurantAdmin(admin.ModelAdmin):

    list_display = [
        'name'
    ]


@admin.register(Article)
class RestaurantAdmin(admin.ModelAdmin):

    list_display = [
        'name',
        'text',
        'chapter',
    ]
 
 