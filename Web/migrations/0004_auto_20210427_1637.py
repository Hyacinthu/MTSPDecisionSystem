# Generated by Django 3.1.7 on 2021-04-27 08:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Web', '0003_auto_20210425_1649'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='decision',
            name='gen',
        ),
        migrations.RemoveField(
            model_name='decision',
            name='solution',
        ),
        migrations.RemoveField(
            model_name='decision',
            name='solution_displayed',
        ),
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gen', models.IntegerField(default=0, null=True, verbose_name='第几代')),
                ('solution', models.CharField(max_length=2000, null=True, verbose_name='方案')),
                ('total_distance', models.CharField(max_length=1000, null=True, verbose_name='总距离')),
                ('balance_factor', models.CharField(max_length=1000, null=True, verbose_name='平衡差')),
                ('solution_displayed', models.CharField(max_length=2000, null=True, verbose_name='用来显示的格式化决策结果')),
                ('decision', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Web.decision')),
            ],
        ),
    ]
