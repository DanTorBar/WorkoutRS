# Generated by Django 5.1.3 on 2025-01-03 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Muscle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('idExercise', models.IntegerField(primary_key=True, serialize=False)),
                ('exerciseName', models.TextField(verbose_name='Exercise name')),
                ('exerciseCategory', models.CharField(max_length=200, null=True, verbose_name='Exercise Category')),
                ('video', models.URLField(null=True, verbose_name='Video')),
                ('instructions', models.TextField(null=True, verbose_name='Instructions')),
                ('tags', models.TextField(null=True, verbose_name='Tags')),
                ('priMuscles', models.ManyToManyField(related_name='primary', to='main.muscle', verbose_name='Primary Muscles')),
                ('secMuscles', models.ManyToManyField(related_name='secondary', to='main.muscle', verbose_name='Secondary Muscles')),
            ],
            options={
                'ordering': ('exerciseName',),
            },
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workoutName', models.TextField(verbose_name='Workout name')),
                ('workoutCategory', models.CharField(max_length=200, null=True, verbose_name='Workout Category')),
                ('level', models.CharField(max_length=30, null=True, verbose_name='Level')),
                ('gender', models.CharField(max_length=30, null=True, verbose_name='Gender')),
                ('bodyPart', models.CharField(max_length=100, null=True, verbose_name='Body Part')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('day1', models.ManyToManyField(blank=True, related_name='day1_routine', to='main.exercise')),
                ('day2', models.ManyToManyField(blank=True, related_name='day2_routine', to='main.exercise')),
                ('day3', models.ManyToManyField(blank=True, related_name='day3_routine', to='main.exercise')),
                ('day4', models.ManyToManyField(blank=True, related_name='day4_routine', to='main.exercise')),
                ('day5', models.ManyToManyField(blank=True, related_name='day5_routine', to='main.exercise')),
                ('day6', models.ManyToManyField(blank=True, related_name='day6_routine', to='main.exercise')),
                ('day7', models.ManyToManyField(blank=True, related_name='day7_routine', to='main.exercise')),
            ],
            options={
                'ordering': ['workoutName'],
            },
        ),
    ]
