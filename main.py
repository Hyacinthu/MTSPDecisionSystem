# This is the try on NSGA-II(no improvement)

import math
import random
import matplotlib.pyplot as plt

# 城市类
# 属性：
class City:
    def __init__(self, n):
        self.individuals = []
        self.distance_matrix = []
        self.n = n

    # 与数据库连接，读取数据库中存储的城市信息表单
    # def get_cities(self):
    #     cities = []
    #     self.individuals = cities

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

#   种群类
#   属性：
#   size：种群大小
#   n：城市数
#   m：旅行商数
#   mutation_pro：变异概率
#   frontm_pro：染色体前段变异概率，后段变异概率为1 - frontm_pro
#   crossover_pro：交叉概率
#   max_gen：最大迭代次数
#   gen：迭代次数
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
#   crowding_distance：拥挤度列表
#   crowding_sorted_list：经过拥挤度排序后的列表
class Population:
    #初始化种群
    def __init__(self, size, n, m, m_pro, c_pro, max_g, fm_pro):
        self.size = size
        self.n = n
        self.m = m
        self.mutation_pro = m_pro
        self.frontm_pro = fm_pro
        self.crossover_pro = c_pro
        self.max_gen = max_g
        self.gen = 0
        self.individuals = []
        self.total_d = []
        self.balance_factor = []
        self.d = []
        self.np = []
        self.sp = []
        self.rank_list = []
        self.rank = []
        self.unsQ = []
        self.crowding_distance = []
        self.crowding_sorted_list = []
        # 产生第0代种群
        for i in range(self.size):  # 问题：也可以出现相同的染色体，出现冗余
            chrom2 = []
            chrom1 = random.sample(range(1, self.n), self.n - 1)
            chrom2 = random.sample(range(0, self.n - 3), self.m - 1)
            chrom2.sort()
            chrom = chrom1 + chrom2
            self.individuals.append(chrom)

    # 总路程算子
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

    # 平衡系数算子
    def f2(self):
        self.balance_factor.append(max(self.d) - min(self.d))

    # 快速非支配排序算子
    def fast_nondominated_sort(self, chroms_size):      # chroms_size不一定要么为N，要么为2N
        self.np = [0 for i in range(chroms_size)]     #n为支配计数(被支配)
        self.sp = [[] for i in range(chroms_size)]     # s为该个体所支配的其他个体集合
        self.rank_list = []     # rank_list为非支配排序后的集合
        temp = []
        self.rank = [0 for i in range(chroms_size)]   # rank为非支配排序后每个染色体对应的等级
        # 计算np和sp(i,j,k,l均为计数变量)
        k = chroms_size-1
        for i in range(chroms_size-1):
            l = chroms_size-k
            for j in range(k):
                if self.total_d[i] < self.total_d[l] and self.balance_factor[i] < self.balance_factor[l]:     # 第i个染色体支配第l个染色体
                    self.np[l] += 1
                    self.sp[i].append(l)
                elif self.total_d[i] > self.total_d[l] and self.balance_factor[i] > self.balance_factor[l]:    # 第i个染色体被第l个染色体支配
                    self.np[i] += 1
                    self.sp[l].append(i)
                l += 1
            k -= 1
        # 测试
        # print(self.np)
        # print(self.sp)
        # sort and rank
        while self.np.count(0) != 0:     # 如果np的列表里依然存在0项，即还未全部变为0以下的数，就继续循环（ps：在未结束之前均存在0项，易证）
            for i in range(chroms_size):  # 循环搜索0项，归入temp列表
                if self.np[i] == 0:
                    temp.append(i)
                    self.np[i] -= 1
            self.rank_list.append(temp)
            for chrom_dominating in temp:   # 将0项所支配的项np-1
                for chrom_dominated in self.sp[chrom_dominating]:
                    self.np[chrom_dominated] -= 1
            temp = []
        # 测试
        # print(self.rank_list)
        for i in range(len(self.rank_list)):
            for chrom in self.rank_list[i]:
                self.rank[chrom] = i
        # 测试
        # print(self.rank)

    # To produce unshaped offspring:selection, crossover and mutation
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

    # 交叉
    def crossover(self, chrom1, chrom2):
        chrom1 = self.mutation(chrom1)
        chrom2 = self.mutation(chrom2)
        p = random.random()
        if p > (1 - self.crossover_pro):
            back_chrom1 = chrom1[self.n-1:self.n+self.m-2]
            back_chrom2 = chrom2[self.n-1:self.n+self.m-2]
            mset = self.whether_intersect(back_chrom1, back_chrom2)
            if len(mset) == 0:
                print("交叉失败！！！")
                return (chrom1, chrom2)
            else:
                sp = mset[random.randint(0, len(mset)-1)]
                t = back_chrom1[sp]
                back_chrom1[sp] = back_chrom2[sp]
                back_chrom2[sp] = t
                back_chrom1.sort()
                back_chrom2.sort()
                chrom1[self.n-1:self.n+self.m-2] = back_chrom1
                chrom2[self.n-1:self.n+self.m-2] = back_chrom2
        return (chrom1, chrom2)

    # 变异
    def mutation(self, chrom):
        p = random.random()
        if p > (1 - self.mutation_pro):     # 对于此参数可以进行调试和优化
            p = random.random()
            if p >= (1 - self.frontm_pro):    # 前段交换
                ex_el = random.sample(range(0, self.n-2), 2)    # 换位的两个序号
                t = chrom[ex_el[0]]
                chrom[ex_el[0]] = chrom[ex_el[1]]
                chrom[ex_el[1]] = t
                return chrom
            else:   # 后段突变，需要优化，目前就直接随机数覆盖
                back_chrom = chrom[self.n-1:self.n+self.m-2]     # 提取后段
                mp = random.randint(0, self.m-2)    # 后段突变的位置
                mset = self.produce_mutation_set(self.n - 2, back_chrom.copy())    # 可行的前段序号集合
                sp = random.randint(0, len(mset)-1)
                change = mset[sp]
                back_chrom[mp] = change
                # 反着的情况，要调换一下
                back_chrom.sort()
                chrom[self.n-1:self.n+self.m-2] = back_chrom
                return chrom
        else:
            return chrom

    # 拥挤度算子(Crowding distance)
    def crowding_distance_computation(self, r_list, miss_num):
        # print(self.rank_list)
        self.crowding_distance = [[] for i in range(len(r_list))]
        self.crowding_sorted_list = []      # 该表为r_list经过拥挤度排序后的序号表
        total_distance = []
        b_factor = []
        r_dic = {}
        for e in r_list:    # e为unsQ中染色体的序号
            r_dic[e] = self.total_d[e]
        # print(r_dic)
        r_dic_sorted = sorted(r_dic.items(), key=lambda item:item[1])   # r_dic_sorted为列表里包含元组的形式
        # print(r_dic_sorted)
        i = 0
        for chrom_num in r_dic_sorted:
            self.crowding_distance[i].append(chrom_num[0])
            i += 1
        for chrom_num in r_dic_sorted:
            total_distance.append(chrom_num[1])
        # print("总路程：")
        # print(total_distance)
        for chrom_num in r_dic_sorted:
            b_factor.append(self.balance_factor[chrom_num[0]])
        # print("平衡系数：")
        # print(b_factor)
        f1_d = max(total_distance) - min(total_distance)
        f2_d = max(b_factor) - min(b_factor)
        if f1_d == 0 and f2_d != 0:
            for e in self.crowding_distance:
                e.append(self.balance_factor[e[0]])
        elif f1_d != 0 and f2_d == 0:
            for e in self.crowding_distance:
                e.append(self.total_d[e[0]])
        elif f1_d != 0 and f2_d != 0:
            self.crowding_distance[0].append(444444444444)
            self.crowding_distance[len(self.crowding_distance)-1].append(4444444444444)
            for i in range(len(self.crowding_distance)):
                if len(self.crowding_distance[i]) == 1:
                    front = self.crowding_distance[i-1][0]
                    back = self.crowding_distance[i+1][0]
                    cd = (self.total_d[back] - self.total_d[front])/f1_d + (self.balance_factor[front] - self.balance_factor[back])/f2_d
                    self.crowding_distance[i].append(cd)
        else:
            for e in self.crowding_distance:
                e.append(0)
        self.QuickSort(self.crowding_distance, 0, len(self.crowding_distance)-1)
        for i in range(miss_num):
            self.crowding_sorted_list.append(self.crowding_distance[i][0])

    # 产生新子代，即新父种群
    def produce_newf(self, city):
        self.f1(city, self.unsQ)
        self.fast_nondominated_sort(len(self.unsQ))
        # print(self.total_d)
        # print(self.balance_factor)
        # print(self.rank)
        # print(self.rank_list)
        self.individuals = []
        i = 0
        while len(self.individuals) + len(self.rank_list[i]) <= self.size:
            for chrom in self.rank_list[i]:
                self.individuals.append(chrom)
            if len(self.individuals) == self.size:      # 为了防止当unsQ的长度刚好等于self.size时，而造成rank_list[i]越界
                break
            i += 1
        # print(self.individuals)
        # 拥挤度计算，同等级进行比较
        if len(self.individuals) < self.size:
            self.crowding_distance_computation(self.rank_list[i], self.size - len(self.individuals))
            self.individuals += self.crowding_sorted_list
        for i in range(len(self.individuals)):
            self.individuals[i] = self.unsQ[self.individuals[i]]

    #结果输出
    def Generate_Results(self):
        print("新父代：")
        print(self.individuals)

    # 迭代入口
    def run(self, city):
        while self.gen < self.max_gen:
            print("第"+str(self.gen)+"代种群：")
            print(self.individuals)
            self.f1(city, self.individuals)
            print("第" + str(self.gen) + "代个体总路程(f1)：")
            print(self.total_d)
            print("第" + str(self.gen) + "代个体平衡系数(f2)：")
            print(self.balance_factor)
            self.fast_nondominated_sort(N)
            self.unshaped_evolution()
            self.produce_newf(city)
            self.gen += 1
        print("第" + str(self.gen) + "代种群：")
        print(self.individuals)
        self.f1(city, self.individuals)
        print("第" + str(self.gen) + "代个体总路程(f1)：")
        print(self.total_d)
        print("第" + str(self.gen) + "代个体平衡系数(f2)：")
        print(self.balance_factor)
        # 通过外部接口传送到数据库和web前端
        # self.Generate_Results()
        self.plot_final_front()

    # Tools
    # 集合取反
    def produce_mutation_set(self, num, list):     #num为可行范围，即全集的长度
        set = []
        list0 = []
        for l in list:
            if l not in list0:
                list0.append(l)
        for i in range(num):
            set.append(i)
        for e in list0:
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

    # 快速排序
    def QuickSort(self, list, low, high):
        if low < high:
            pivotpos = self.partition(list, low, high)
            self.QuickSort(list, low, pivotpos - 1)
            self.QuickSort(list, pivotpos + 1, high)

    # 划分
    def partition(self, list, low, high):
        pivot = list[low]
        while low < high:
            while low < high and list[high][1] >= pivot[1]:
                high -= 1
            list[low] = list[high]
            while low < high and list[low][1] <= pivot[1]:
                low += 1
            list[high] = list[low]
        list[low] = pivot
        return low

    #图像打印
    # Lets plot the final front now
    def plot_final_front(self):
        total_dsitance = [i * 1 for i in self.total_d]
        balance_factor = [j * 1 for j in self.balance_factor]
        plt.xlabel('Total distance', fontsize=15)
        plt.ylabel('Balance Factor', fontsize=15)
        plt.scatter(total_dsitance, balance_factor)
        plt.show()

if __name__ == '__main__':
    # 测试代码
    N = 8  # 染色体数目
    n = 20 # 城市数目
    m = 4  # 旅行商数目
    m_pro = 0.8     # 变异概率
    c_pro = 0.2     # 交叉概率
    max_gen = 100   # 最大迭代次数
    fm_pro = 0.5    # 染色体前段突变概率
    city = City(n)
    cities = [[34, 53], [96, 62], [29, 21], [10, 48], [14, 3], [3, 64], [13, 77], [48, 13], [69, 53], [79, 13], [26, 33], [85, 43],[63, 56], [2, 57], [69, 93], [79, 31], [35, 35], [26, 96], [60, 47], [30, 74]]
    city.individuals += cities
    # for i in range(n):
    #     city.individuals.append([random.randint(0, 100), random.randint(0, 100)])
    city.cal_distance_matrix()
    p = Population(N, n, m, m_pro, c_pro, max_gen, fm_pro)
    p.run(city)
