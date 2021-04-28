    from django.shortcuts import render, redirect
    from django.http import HttpResponse, HttpResponseRedirect
    from django import forms
    from .models import User, Decision
    from .forms import UploadCityFile
    from .NSGAII import CalculateChromNumber, Run, Population
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
                chrom_num = CalculateChromNumber(n, m)
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
                decision = Decision.objects.get(state=1)
                # d_title = decision.title
                # file_name = str(u_id) + '__' + d_title
                handle_uploaded_file(request.FILES.getlist('city_file'), decision)
                return render(request, 'show_result.html')
            else:
                return render(request, 'load_cities.html')

    # def handle_uploaded_file(f, decision):
    #     city_string = ""
    #     num_str = ""
    #     i = 0
    #     x = 0
    #     y = 0
    #     for chunk in f[0].chunks():
    #         city_string = city_string + str(chunk)
    #     for s in city_string:
    #         if s < "0":
    #             i += 1
    #         elif s > "9":
    #             i += 1
    #         else:
    #             break
    #     i -= 1
    #     for j in range(len(city_string) - i):
    #         i += 1
    #         if city_string[i] == "\\":
    #             if city_string[i+1] == 'r':
    #                 y = int(num_str)
    #                 num_str = ""
    #                 city = Cities()
    #                 city.x = x
    #                 city.y = y
    #                 city.decision = decision
    #                 city.save()
    #             else:
    #                 continue
    #         elif city_string[i] == '\'':
    #             y = int(num_str)
    #             num_str = ""
    #             city = Cities()
    #             city.x = x
    #             city.y = y
    #             city.decision = decision
    #             city.save()
    #             break
    #         elif city_string[i] == 'r':
    #             continue
    #         elif city_string[i] == 'n':
    #             continue
    #         elif city_string[i] == ',':
    #             x = int(num_str)
    #             num_str = ""   
    #         else:
    #             num_str = num_str + city_string[i]

    # “显示结果”选项
    def show_result(request):
        if request.method == "GET":
            # # 数据准备
            # city = []
            # u_id = request.session['member_id']
            # user = User.objects.get(id = u_id)
            # d = Decision.objects.get(state=1)
            # print(d)
            # print(d.state)
            # cities_num = Cities.objects.filter(decision = d).count()
            # cities = Cities.objects.filter(decision = d)
            # for i in range(cities_num):
            #     city.append([cities[i].x, cities[i].y])
            # # 算法运行
            # p = Run(d.n, d.m, d.chrom_num, city)
            # g = Generation()
            # g.gen = p.gen
            # g.solution = p.individuals
            # g.decision = d
            # g.save()
            # # 显示数据
            # # 运行结束
            # d.state = 0
            # d.generation_id = g.id
            # d.save()
            return render(request, 'show_result.html')

    # “历史记录”选项
    def history(request):
        if request.method == "GET":
            u_id = request.session['member_id']
            user = User.objects.get(id=u_id)
            decision = Decision.objects.filter(user=user)
            # generation = Generation.objects.get(decision=decision)
            # solution = list(generation.solution)
            return render(request, 'history.html', {"decision_list" : decision})#, "routes" : solution})

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