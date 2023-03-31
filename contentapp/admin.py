from django.contrib import admin
from django.contrib import admin
from .models import Chapter, Article, Image
from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from adminsortable2.admin import SortableTabularInline
from adminsortable2.admin import SortableAdminBase
from contentapp.mixin_classes import ImagePreviewMixin


# Register your models here.


class ImagesSortableInline(SortableTabularInline, ImagePreviewMixin):

    model = Image
    fields = ['picture', 'get_preview_image']
    readonly_fields = ['get_preview_image']


@admin.register(Image)
class ImageAdmin(SortableAdminMixin, admin.ModelAdmin, ImagePreviewMixin):
    list_display = [
        'priority',
        'get_preview_image',
    ]
    readonly_fields = ['get_preview_image']

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):

    list_display = [
        'name'
    ]


@admin.register(Article)
class ArticleAdmin(SortableAdminBase, admin.ModelAdmin):

    inlines = [
        ImagesSortableInline,
    ]

 
 