# Generated by Django 2.2 on 2024-05-30 07:48

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articlecategory',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 30, 7, 48, 7, 438251, tzinfo=utc)),
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, upload_to='article/%Y%m%d/')),
                ('title', models.CharField(blank=True, max_length=20)),
                ('tags', models.CharField(blank=True, max_length=20)),
                ('sumary', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('total_views', models.PositiveSmallIntegerField(default=0)),
                ('comments_count', models.PositiveSmallIntegerField(default=0)),
                ('created', models.DateTimeField(default=datetime.datetime(2024, 5, 30, 7, 48, 7, 438251, tzinfo=utc))),
                ('update', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='article', to='home.ArticleCategory')),
            ],
        ),
    ]
