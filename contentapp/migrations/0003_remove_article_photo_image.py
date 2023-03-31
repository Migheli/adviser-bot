# Generated by Django 4.1.7 on 2023-03-31 20:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contentapp', '0002_article_photo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='photo',
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(default=0, verbose_name='Приоритет')),
                ('picture', models.ImageField(upload_to='media', verbose_name='Фото')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='contentapp.article', verbose_name='Статья')),
            ],
            options={
                'verbose_name': 'Изображение',
                'verbose_name_plural': 'Изображения',
                'ordering': ['priority'],
            },
        ),
    ]
