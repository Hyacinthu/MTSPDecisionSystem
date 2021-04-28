from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect, get_list_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from .models import User, Decision
from .forms import UploadCityFile
from NSGA_II import NSGAII
import os

# Create your views here.

# 首页
def index(request):
    return render(request, 'unlogged_homepage.html')

# 登录页面
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        # 如果登录成功，绑定参数到cookie中，set_cookie
        username = request.POST.get('uname')
        password = request.POST.get('pw')
        next_url = request.POST.get('next')
        # 查询用户是否在数据库中
        if User.objects.filter(uname=username).exists():
            user = User.objects.get(uname=username)
            if user.pw == password:
                request.session['member_id'] = user.id
                return render(request, 'home.html')
            else:
                # return HttpResponse('用户密码错误')
                return render(request, 'unlogged_homepgae.html', {'pw': '用户密码错误'})
        else:
            # return HttpResponse('用户不存在')
            return render(request, 'unlogged_homepgae.html', {'uname': '用户不存在'})

# 登出
def logout(request):
    try:
        del request.session['member_id']
    except KeyError:
        pass
    return render(request, 'unlogged_homepage.html')

# 注册页面
def register(request):
    if request.method == "GET":
        return render(request, 'register.html')
    if request.method == "POST":
        username = request.POST.get('phonenumber')
        password = request.POST.get('pw')
        nickname = request.POST.get('nickname')
        email = request.POST.get('email')
        if User.objects.filter(uname=username).exists():
            return render(request, 'register.html', {'uname': '用户已注册'})
        else:
            user = User()
            user.uname = username
            user.pw = password
            user.nickname = nickname
            user.email = email
            user.save()
            return render(request, 'login.html')

# home页面
def home(request):
    if request.method == "GET":
        return render(request, 'home.html')

# “创建决策”选项
def create_mtsp(request):
    if request.method == "GET":
        return render(request, 'create_mtsp.html')
    if request.method == "POST":
        title = request.POST.get('solution_title')
        n = int(request.POST.get('n_num'))
        m = int(request.POST.get('m_num'))
        if n & m:
            u_id = request.session['member_id']
            user = User.objects.get(id = u_id)
            chrom_num = NSGAII.CalculateChromNumber(n, m)
            decision = Decision()
            decision.title = title
            decision.n = n
            decision.m = m
            decision.chrom_num = chrom_num
            decision.state = 1
            decision.user = user
            decision.save()
            return render(request, 'load_cities.html')
        else:
            return render(request, 'create_mtsp.html')
        return render(request, 'create_mtsp.html')

# “载入城市信息”页面
def load_cities(request):
    if request.method == "GET":
        return render(request, 'load_cities.html')
    if request.method == "POST":
        form = UploadCityFile(request.POST, request.FILES)
        if form.is_valid():
            u_id = request.session['member_id']
            user = User.objects.get(id = u_id)
            d = Decision.objects.get(state=1)
            handle_uploaded_file(request.FILES.getlist('city_file'), d)
            return render(request, 'show_result.html')
        else:
            return render(request, 'load_cities.html')

def handle_uploaded_file(f, decision):
    city_string = ""
    num_str = ""
    city = []
    i = 0
    x = 0
    y = 0
    for chunk in f[0].chunks():
        city_string = city_string + str(chunk)
    for s in city_string:
        if s < "0":
            i += 1
        elif s > "9":
            i += 1
        else:
            break
    i -= 1
    for j in range(len(city_string) - i):
        i += 1
        if city_string[i] == "\\":
            if city_string[i+1] == 'r':
                y = int(num_str)
                num_str = ""
                city.append([x, y])
            else:
                continue
        elif city_string[i] == '\'':
            y = int(num_str)
            num_str = ""
            city.append([x, y])
            decision.city = city
            decision.save()
            break
        elif city_string[i] == 'r':
            continue
        elif city_string[i] == 'n':
            continue
        elif city_string[i] == ',':
            x = int(num_str)
            num_str = ""
        else:
            num_str = num_str + city_string[i]

# “显示结果”选项
def show_result(request):
    if request.method == "GET":
        # 数据准备
        u_id = request.session['member_id']
        user = User.objects.get(id = u_id)
        d = Decision.objects.get(state=1)
        city = handle_city_string(d.city)
        # 算法运行
        p = NSGAII.Run(d.n, d.m, d.chrom_num, city)
        d.gen = p.gen
        d.solution = p.individuals
        # 处理并存储格式化数据
        d.solution_displayed = handle_displayed_solution(d.solution, d.n, d.m)
        d.total_distance = p.total_d
        d.balance_factor = p.balance_factor
        # 运行结束
        d.state = 0
        d.save()
        # 显示数据
        # id, title, n, m, gen, solution_displayed, total_distance, balance_factor
        if d.chrom_num < 5:
            display = merge(d.solution_displayed, d.total_distance, d.balance_factor, 0)
        else:
            display = merge(d.solution_displayed, d.total_distance, d.balance_factor, 1)
        print("需要：")
        print(display)
        return render(request, 'show_result.html', {"id" : d.id, "name" : d.title, "n" : d.n, "m" : d.m, "gen" : d.gen, "display" : display})

def handle_displayed_solution(solution, n, m):
    previous_len = n-1
    later_len = m-1
    tag = previous_len
    displayed_solution = [[] for i in range(len(solution))]
    displayed_string = ""
    serial_num = 0
    for route in solution:
        displayed_solution[serial_num].append(serial_num + 1)
        for i in range(n-1):
            if i == 0:
                displayed_string += "0"
            displayed_string += "->"
            if i == route[tag]:
                displayed_string += str(route[i])
                displayed_string += "->0; 0"
                if tag < previous_len + later_len - 1:
                    tag += 1
            else:
                displayed_string += str(route[i])
                if i == n-2:
                    displayed_string += "->0"
        displayed_solution[serial_num].append(displayed_string)
        displayed_string = ""
        serial_num += 1
        tag = previous_len
    return displayed_solution

def merge(solution_displayed, total_distance, balance_factor, tag):   #合并后端数据
    display = []
    if tag == 0:
        for i in range(len(solution_displayed)):
            solution_displayed[i].append(total_distance[i])
            solution_displayed[i].append(balance_factor[i])
            display.append(solution_displayed[i])
        return display
    if tag == 1:
        for i in range(len(solution_displayed)):
            solution_displayed = solution_displayed[0:5]
            total_distance = total_distance[0:5]
            balance_factor = balance_factor[0:5]
            solution_displayed[i].append(total_distance[i])
            solution_displayed[i].append(balance_factor[i])
            display.append(solution_displayed[i])
        return display

def handle_city_string(city):
    city_str = city[1:len(city)]
    city_list = []
    i = 0
    x = 0
    y = 0
    while i < len(city_str):
        if city_str[i] == '[':
            j = i + 1
            while city_str[i] != ',':
                i += 1
            x = int(city_str[j:i])
            j = i + 2
            while city_str[i] != ']':
                i += 1
            y = int(city_str[j:i])
            city_list.append([x, y])
            x = 0
            y = 0
        else:
            i += 1
    return city_list

# “历史记录”选项
def history(request):
    if request.method == "GET":
        u_id = request.session['member_id']
        user = User.objects.get(id=u_id)
        if(Decision.objects.filter(user=user).count() == 0):
            return render(request, 'history_if_no_history.html')
        else:
            decision = Decision.objects.filter(user=user)
            display = []
            for d in decision:
                display_list = list(d.solution_displayed)
                if len(display_list) < 5:
                    display_s = display_list
                else:
                    display_s = display_list[0:5]
                display.append(display_s)
            return render(request, 'history.html', {"decision_list" : decision})

#无历史记录
def no_history(request):
    if request.method == "GET":
        return render(request, 'history_if_no_history.html')

# “个人中心”选项
def self(request):
    if request.method == "GET":
        u_id = request.session['member_id']
        user = User.objects.get(id=u_id)
        nickname = user.nickname
        phonenumber = user.uname
        email = user.email
        return render(request, 'self.html', {"nickname" : nickname, "phonenumber" : phonenumber, "email" : email})

# “帮助”选项
def help(request):
    if request.method == "GET":
        return render(request, 'help.html')