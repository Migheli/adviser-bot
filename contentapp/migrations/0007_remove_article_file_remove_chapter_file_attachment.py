# Generated by Django 4.1.7 on 2023-04-01 18:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contentapp', '0006_image_chapter_alter_image_article'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='file',
        ),
        migrations.RemoveField(
            model_name='chapter',
            name='file',
        ),
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(default=0, verbose_name='Приоритет')),
                ('file', models.FileField(upload_to='media', verbose_name='Фaйл-приложение')),
                ('article', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='contentapp.article', verbose_name='Статья')),
                ('chapter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='contentapp.chapter', verbose_name='Раздел')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
                'ordering': ['priority'],
            },
        ),
    ]
