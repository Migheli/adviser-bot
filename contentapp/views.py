from django.shortcuts import render
from .models import Chapter
from django.http import JsonResponse


# Create your views here.
def get_main_menu_data(request):
    chapters = Chapter.objects.all()

    dumped_chapters = []
    for chapter in chapters:
        dumped_chapter = {
            'name': chapter.name,
        }
        dumped_chapters.append(dumped_chapter)
    return JsonResponse(dumped_chapters, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })
