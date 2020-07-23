# Generated by Django 2.2.12 on 2020-07-23 10:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_players', models.IntegerField()),
                ('intoxication_level', models.IntegerField()),
                ('number_of_bonus_words', models.IntegerField()),
                ('game_data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.CharField(max_length=160, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=240)),
                ('overview', models.TextField(blank=True, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('release_date', models.DateTimeField(blank=True, null=True)),
                ('cover', models.TextField(blank=True, null=True)),
                ('subtitles_file', models.FileField(blank=True, null=True, upload_to='subtitles/')),
                ('additional_data', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField()),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Game')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_key', models.CharField(max_length=160)),
                ('ratings', models.ManyToManyField(through='api.Rating', to='api.Game')),
            ],
        ),
        migrations.AddField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.User'),
        ),
        migrations.AddField(
            model_name='game',
            name='movie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Movie'),
        ),
        migrations.AddField(
            model_name='game',
            name='ratings',
            field=models.ManyToManyField(through='api.Rating', to='api.User'),
        ),
    ]