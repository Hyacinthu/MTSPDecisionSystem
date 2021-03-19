#This is the try on NSGA-II(no improvement)

import math
import random

#城市类
#属性：
class City:
    def __init__(self, n):
        self.individuals = []
        self.distance_matrix = []
        self.n = n

    #与数据库连接，读取数据库中存储的城市信息表单
    #def get_cities(self):

    def cal_distance_matrix(self):
        k = self.n-1
        for i in range(self.n-1):
            l = self.n-k
            for j in range(k):
                self.distance_matrix.append(math.ceil(math.sqrt((self.individuals[i][0]-self.individuals[l][0])*(self.individuals[i][0]-self.individuals[l][0])+(self.individuals[i][1]-self.individuals[l][1])*(self.individuals[i][1]-self.individuals[l][1]))))
                l += 1
            k -= 1

    def x_y_find_i(self, c1, c2):
        m = 0
        if(c1 > c2):
            m = c1
            c1 = c2
            c2 = m
        return self.distance_matrix[math.ceil((2*self.n-1-c1)*c1/2+c2-c1-1)]

#种群类
#属性：
#   size：种群大小
#   n：城市数
#   m：旅行商数
#   individuals：个体集合
#   total_d：个体总路程集合，f1(X)，X代指染色体集合
#   balance_factor：平衡系数，f2(X)，X代指染色体集合
#   nds_factor：非支配排序中需要的两个参数集合，n(np)和s(sp)；n为支配计数，s为该个体所支配的其他个体集合
#   d：每个染色体中每个旅行商的路程集合
#   rank_list：非支配排序后的集合
#   rank：非支配排序后每个染色体对应的等级
class Population:
    #初始化种群
    def __init__(self, size, n, m):
        self.size = size
        self.n = n
        self.m = m
        self.individuals = []
        self.total_d = []
        self.balance_factor = []
        self.nds_factor = []
        self.d = []
        self.np = []
        self.sp = []
        self.rank_list = []
        self.rank = []
        #产生第0代种群
        for i in range(self.size):
            chrom2 = []
            chrom1 = random.sample(range(1, self.n), self.n-1)
            chrom2_select = random.sample(range(0, self.n-2), self.m-1)
            chrom2_select.sort()
            for i in range(self.m-1):
                chrom2.append(chrom1[chrom2_select[i]])
            chrom = chrom1+chrom2
            self.individuals.append(chrom)

    #总路程算子
    def f1(self, city):
        self.total_d = []
        self.balance_factor = []
        sum = 0
        for i in range(self.size):
            psum = 0
            pnode = 0
            mcount = self.n - 1     #分割点序号
            jnode = self.individuals[i][mcount]
            for j in range(self.n-1):
                sum += city.x_y_find_i(pnode, self.individuals[i][j])
                pnode = self.individuals[i][j]
                if pnode == jnode:
                    mcount += 1
                    if mcount < self.n+self.m-2:
                        jnode = self.individuals[i][mcount]
                    sum += city.x_y_find_i(pnode, 0)
                    #得到每个染色体中每个旅行商的路程集合
                    self.d.append(sum-psum)
                    psum = sum
                    #---
                    pnode = 0
            sum += city.x_y_find_i(self.individuals[i][self.n-2], 0)
            self.total_d.append(sum)
            self.d.append(sum-psum)
            sum = 0
            self.f2()
            self.d = []

    #平衡系数算子
    def f2(self):
        self.balance_factor.append(max(self.d) - min(self.d))


    #快速非支配排序算子
    def fast_nondominated_sort(self):
        self.n = [0 for i in range(self.size)]     #n为支配计数(被支配)
        self.s = [[] for i in range(self.size)]     #s为该个体所支配的其他个体集合
        self.rank_list = []     #rank_list为非支配排序后的集合
        temp = []
        self.rank = [0 for i in range(self.size)]   #rank为非支配排序后每个染色体对应的等级

        #计算np和sp(i,j,k,l均为计数变量)
        k = self.size-1
        for i in range(self.size-1):
            l = self.size-k
            for j in range(k):
                if self.total_d[i] < self.total_d[l] and self.balance_factor[i] < self.balance_factor[l]:     #第i个染色体支配第l个染色体
                    self.n[l] += 1
                    self.s[i].append(l)
                elif self.total_d[i] > self.total_d[l] and self.balance_factor[i] > self.balance_factor[l]:    #第i个染色体被第l个染色体支配
                    self.n[i] += 1
                    self.s[l].append(i)
                l += 1
            k -= 1
        #测试
        #print(self.n)
        #print(self.s)
        #sort and rank
        times = max(self.n)
        time = 0
        while time < times:
            for i in range(self.size):
                if self.n[i] == 0:
                    temp.append(i)
                    self.n[i] -= 1
            if len(temp) == 0:
                time += 1
                continue
            self.rank_list.append(temp)
            for chrom_dominating in temp:
                for chrom_dominated in self.s[chrom_dominating]:
                    self.n[chrom_dominated] -= 1
            temp = []
            time += 1
        #测试
        #print(self.rank_list)
        for i in range(len(self.rank_list)):
            for chrom in self.rank_list[i]:
                self.rank[chrom] = i
        #测试
        #print(self.rank)


if __name__ == '__main__':
    #测试代码
    N = 16  #染色体数目
    n = 78 #城市数目
    m = 24  #旅行商数目
    city = City(n)
    for i in range(n):
        city.individuals.append([random.randint(0, 100), random.randint(0, 100)])
    print(city.individuals)
    city.cal_distance_matrix()
    print(city.distance_matrix)
    #测试距离矩阵查找函数
    #d = city.x_y_find_i(3, 1)
    #print(d)
    p = Population(N, n, m)
    print(p.individuals)
    p.f1(city)
    print(p.total_d)
    print(p.balance_factor)
    p.fast_nondominated_sort()


