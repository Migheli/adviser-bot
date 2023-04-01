from django.contrib import admin
from django.contrib import admin
from .models import Chapter, Article, Image, Attachment
from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin
from adminsortable2.admin import SortableTabularInline
from adminsortable2.admin import SortableAdminBase
from contentapp.mixin_classes import ImagePreviewMixin


# Register your models here.


class AttachmentSortableInline(SortableTabularInline):

    model = Attachment
    fields = ['file']


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
class ChapterAdmin(SortableAdminBase, admin.ModelAdmin):

    inlines = [
        ImagesSortableInline,
        AttachmentSortableInline
    ]


@admin.register(Article)
class ArticleAdmin(SortableAdminBase, admin.ModelAdmin):

    inlines = [
        ImagesSortableInline,
        AttachmentSortableInline
    ]


@admin.register(Attachment)
class AttachmentAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ['file']    
 