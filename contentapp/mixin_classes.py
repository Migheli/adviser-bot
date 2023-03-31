from django.utils.html import format_html


class ImagePreviewMixin():

    def get_preview_image(self, obj):
        url = obj.photo.url
        height = '200'
        return format_html(
            '<img src="{}" width="{}" height={} />',
            url,
            'auto',
            height
        )
    get_preview_image.short_description = 'Предпросмотр'
