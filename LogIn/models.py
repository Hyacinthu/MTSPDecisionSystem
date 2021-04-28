from django.db import models
from django import forms

# Create your models here.

class User(models.Model):
    uname = models.CharField('用户名', max_length=20, default='')
    pw = models.CharField('密码', max_length = 20)
    nickname = models.CharField('昵称', max_length = 100, default = '')
    email = models.CharField('电子邮箱', max_length = 50, default = '')

class Decision(models.Model):
    # 决策信息
    title = models.CharField('决策名字', max_length = 100, default='')
    n = models.IntegerField('城市数目', default=0)
    m = models.IntegerField('旅行商数目', default=0)
    chrom_num = models.IntegerField('染色体数目', default=0)
    state = models.IntegerField('状态', default=0)
    # 城市信息
    city = models.CharField('城市列表', max_length=65535, default='', null=True)
    # 决策结果
    gen = models.IntegerField('第几代', default=0, null=True)
    solution = models.CharField('方案', max_length=2000, null=True)
    # 用户外键
    user = models.ForeignKey(User, on_delete=models.CASCADE)
