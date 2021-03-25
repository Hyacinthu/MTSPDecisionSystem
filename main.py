#This is the try on NSGA-II(no improvement)

import math
import random
from filecmp import cmp

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
#   generation：种群的代数，即迭代次数
#   individuals：个体集合
#   total_d：个体总路程集合，f1(X)，X代指染色体集合
#   balance_factor：平衡系数，f2(X)，X代指染色体集合
#   d：每个染色体中每个旅行商的路程集合
#   np：支配计数
#   sp：该个体所支配的其他个体集合
#   rank_list：非支配排序后的集合
#   rank：非支配排序后每个染色体对应的等级
#   unsQ：unshaped offspring, 即假子代，为二重列表
class Population:
    #初始化种群
    def __init__(self, size, n, m):
        self.size = size
        self.n = n
        self.m = m
        self.generation = 0
        self.individuals = []
        self.total_d = []
        self.balance_factor = []
        self.d = []
        self.np = []
        self.sp = []
        self.rank_list = []
        self.rank = []
        self.unsQ = []
        #产生第0代种群
        for i in range(self.size):  #问题：也可以出现相同的染色体，出现冗余
            chrom2 = []
            chrom1 = random.sample(range(1, self.n), self.n - 1)
            chrom2 = random.sample(range(0, self.n - 3), self.m - 1)
            chrom2.sort()
            chrom = chrom1 + chrom2
            self.individuals.append(chrom)

    #总路程算子
    def f1(self, city, chroms):     #chroms为任意染色体集合
        self.total_d = []
        self.balance_factor = []
        sum = 0
        for chrom in chroms:
            psum = 0
            ppoint = 0
            po = self.n - 1
            dpoint = chrom[chrom[po]]
            for point in chrom[0:self.n-1]:
                sum += city.x_y_find_i(ppoint, point)
                ppoint = point
                if ppoint == dpoint:
                    sum += city.x_y_find_i(ppoint, 0)
                    if po < self.m + self.n - 3:
                        po += 1
                        dpoint = chrom[chrom[po]]
                    self.d.append(sum - psum)
                    psum = sum
                    ppoint = 0
            sum += city.x_y_find_i(point, 0)
            self.total_d.append(sum)
            self.d.append(sum - psum)
            sum = 0
            self.f2()
            self.d = []

    #平衡系数算子
    def f2(self):
        self.balance_factor.append(max(self.d) - min(self.d))

    #快速非支配排序算子
    def fast_nondominated_sort(self, chroms_size):      # chroms_size不一定要么为N，要么为2N
        self.np = [0 for i in range(chroms_size)]     #n为支配计数(被支配)
        self.sp = [[] for i in range(chroms_size)]     #s为该个体所支配的其他个体集合
        self.rank_list = []     #rank_list为非支配排序后的集合
        temp = []
        self.rank = [0 for i in range(chroms_size)]   #rank为非支配排序后每个染色体对应的等级
        #计算np和sp(i,j,k,l均为计数变量)
        k = chroms_size-1
        for i in range(chroms_size-1):
            l = chroms_size-k
            for j in range(k):
                if self.total_d[i] < self.total_d[l] and self.balance_factor[i] < self.balance_factor[l]:     #第i个染色体支配第l个染色体
                    self.np[l] += 1
                    self.sp[i].append(l)
                elif self.total_d[i] > self.total_d[l] and self.balance_factor[i] > self.balance_factor[l]:    #第i个染色体被第l个染色体支配
                    self.np[i] += 1
                    self.sp[l].append(i)
                l += 1
            k -= 1
        #测试
        print(self.np)
        print(self.sp)
        #sort and rank
        while self.np.count(0) != 0:     #如果np的列表里依然存在0项，即还未全部变为0以下的数，就继续循环（ps：在未结束之前均存在0项，易证）
            for i in range(chroms_size):  #循环搜索0项，归入temp列表
                if self.np[i] == 0:
                    temp.append(i)
                    self.np[i] -= 1
            self.rank_list.append(temp)
            for chrom_dominating in temp:   #将0项所支配的项np-1
                for chrom_dominated in self.sp[chrom_dominating]:
                    self.np[chrom_dominated] -= 1
            temp = []
        #测试
        print(self.rank_list)
        for i in range(len(self.rank_list)):
            for chrom in self.rank_list[i]:
                self.rank[chrom] = i
        #测试
        print(self.rank)

    #To produce unshaped offspring:selection, crossover and mutation
    def unshaped_evolution(self):
        self.unsQ = []
        self.unsQ += self.individuals
        i = 0
        while i < self.size * 2:
            sampleQ = random.sample(range(0, self.size), int(self.size/2))
            srank = []
            for sq in sampleQ:
                srank.append(self.rank[sq])
            srank.sort()
            rank1 = srank[0]
            rank2 = srank[1]
            for sq in sampleQ:
                if self.rank[sq] == rank1:
                    sq1_num = sq
                    sq1 = self.individuals[sq1_num]
                    break
            for sq in sampleQ:
                if self.rank[sq] == rank2:
                    if sq == sq1_num:
                        continue
                    sq2_num = sq
                    sq2 = self.individuals[sq2_num]
                    break
            sq1_copy = sq1.copy()
            sq2_copy = sq2.copy()
            (unsq1, unsq2) = self.crossover(sq1_copy, sq2_copy)
            # 规避有相同形状的个体，去掉未变异个体
            for i in range(0, len(unsq1)):
                if sq1[i] == unsq1[i]:
                    pass
                else:
                    self.unsQ.append(unsq1)
                    break
            for i in range(0, len(unsq2)):
                if sq2[i] == unsq2[i]:
                    pass
                else:
                    self.unsQ.append(unsq2)
                    break
            i += 1

    #交叉
    def crossover(self, chrom1, chrom2):
        # print("origin chrom1:")
        # print(chrom1)
        chrom1 = self.mutation(chrom1)
        # print("chrom1:")
        # print(chrom1)
        # print("\t")
        # print("origin chrom2:")
        # print(chrom2)
        chrom2 = self.mutation(chrom2)
        # print("chrom2:")
        # print(chrom2)
        # print("\t")
        # 交叉部分
        p = random.random()
        if p > 0.5:
            back_chrom1 = chrom1[self.n-1:self.n+self.m-2]
            back_chrom2 = chrom2[self.n-1:self.n+self.m-2]
            mset = self.whether_intersect(back_chrom1, back_chrom2)
            if len(mset) == 0:
                print("交叉失败！！！")
                return (chrom1, chrom2)
            else:
                sp = mset[random.randint(0, len(mset)-1)]
                # 测试
                # print("sp:")
                # print(sp)
                sp += self.n-1
                t = chrom1[sp]
                chrom1[sp] = chrom2[sp]
                chrom2[sp] = t
        return (chrom1, chrom2)

    #变异
    def mutation(self, chrom):
        p = random.random()
        # 测试
        # print("是否变异：")
        # print(p)
        if p > 0.5:     #对于此参数可以进行调试和优化
            #mutate
            p = random.random()
            # 测试
            # print("是否前段交换：")
            # print(p)
            if p >= 0.5:    #前段交换
                ex_el = random.sample(range(0, self.n-2), 2)
                # print(ex_el)
                t = chrom[ex_el[0]]
                chrom[ex_el[0]] = chrom[ex_el[1]]
                chrom[ex_el[1]] = t
                return chrom
            else:   #后段突变，需要优化，目前就直接随机数覆盖
                back_chrom = chrom[self.n-1:self.n+self.m-2]     #提取后段
                mp = random.randint(0, self.m-2)    #后段突变的位置
                # 测试
                # print("mp:")
                # print(mp)
                mset = self.produce_mutation_set(self.n - 2, back_chrom)    #可行的前段序号集合
                sp = random.randint(0, len(mset)-1)
                change = mset[sp]
                back_chrom[mp] = change
                #反着的情况，要调换一下
                back_chrom.sort()
                chrom[self.n-1:self.n+self.m-2] = back_chrom
                return chrom
        else:
            return chrom

    # 产生新子代，即新父种群
    def produce_newf(self, city):
        self.f1(city, self.unsQ)
        self.fast_nondominated_sort(len(self.unsQ))
        print(self.total_d)
        print(self.balance_factor)

    # Tools
    # 集合取反
    def produce_mutation_set(self, num, list):     #num为可行范围，即全集的长度
        set = []
        for i in range(num):
            set.append(i)
        for e in list:
            if list.count(e) > 1:
                list.remove(e)
                continue
            set.remove(e)
        return set

    # 判断两个集合是否有交集，并返回可突变集合
    def whether_intersect(self, list1, list2):
        set1 = set(list1)
        set2 = set(list2)
        intersection = set1 & set2
        if len(intersection) == 0:      #无交集
            l = []
            for i in range(len(list1)):
                l.append(i)
            return l
        else:
            intersection_list = list(intersection)  #交集
            inum = []
            for e in intersection_list:
                for i in range(len(list1)):
                    if(list1[i] == e):
                        inum.append(i)
                for i in range(len(list2)):
                    if(list2[i] == e):
                        inum.append(i)
            s = self.produce_mutation_set(self.m-1, inum)
            # 测试
            # print("set:")
            # print(s)
            return s

if __name__ == '__main__':
    #测试代码
    N = 8  #染色体数目
    n = 20 #城市数目
    m = 4  #旅行商数目
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
    p.f1(city, p.individuals)      #计算两个目标函数的值
    print(p.total_d)
    print(p.balance_factor)
    p.fast_nondominated_sort(p.size)  #快速非支配选择
    p.unshaped_evolution()    #二元竞赛选择
    print(p.unsQ)
    print(len(p.unsQ))
    p.produce_newf(city)

