import random
import sys

import numpy as np

from global_vars import city_num, pheromone_matrix, alpha, beta, distance_matrix


class Ant:

    # 初始化
    def __init__(self, id):

        self.id = id  # ID
        self.__data_init()  # 随机初始化出生点

    # 初始数据
    def __data_init(self):

        self.path = []  # 当前蚂蚁的路径
        self.total_distance = 0.0  # 当前路径的总距离
        self.move_count = 0  # 移动次数
        self.current_city = -1  # 当前停留的城市
        self.open_table_city = np.ones(city_num)  # 探索城市的状态
        self.__ant_birth()  # 生成蚂蚁

    def __ant_birth(self):
        city_index = random.randint(0, city_num - 1)  # 随机初始出生点
        self.path.append(city_index)
        self.current_city = city_index
        self.move_count = 1
        self.open_table_city[city_index] = False

    # 选择下一个城市
    def __choice_next_city(self):

        next_city = -1
        select_city_prob = np.zeros(city_num)  # 存储去下个城市的概率
        total_prob = 0.0

        total_prob = self.__get_next_prob(select_city_prob, total_prob)

        next_city = self.__roulette_wheel_selection(next_city, select_city_prob, total_prob)

        if next_city == -1:
            next_city = random.randint(0, city_num - 1)
            while not (self.open_table_city[next_city]):  # if==False,说明已经遍历过了
                next_city = random.randint(0, city_num - 1)

        # 返回下一个城市序号
        return next_city

    def __get_next_prob(self, select_city_prob, total_prob):
        # 获取去下一个城市的概率
        for i in range(city_num):
            if self.open_table_city[i]:
                try:
                    # 计算概率：与信息素浓度成正比，与距离成反比
                    select_city_prob[i] = pow(pheromone_matrix[self.current_city][i], alpha) * pow(
                        (1.0 / distance_matrix[self.current_city][i]), beta)
                    total_prob += select_city_prob[i]
                except ZeroDivisionError:
                    print('Ant ID: {ID}, current city: {current}, target city: {target}'.format(ID=self.ID,
                                                                                                current=self.current_city,
                                                                                                target=i))
                    sys.exit(1)
        return total_prob

    # 计算路径总距离
    def __cal_total_distance(self):

        global start
        temp_distance = 0.0

        temp_distance = self.__city_traversal(temp_distance)

        # 回路
        end = self.path[0]
        temp_distance += distance_matrix[start][end]
        self.total_distance = temp_distance

    def __roulette_wheel_selection(self, next_city, select_city_prob, total_prob):
        # 轮盘选择城市
        if total_prob > 0.0:
            # 产生一个随机概率,0.0-total_prob
            temp_prob = random.uniform(0.0, total_prob)
            for i in range(city_num):
                if self.open_table_city[i]:
                    # 轮次相减
                    temp_prob -= select_city_prob[i]
                    if temp_prob < 0.0:
                        next_city = i
                        break
        return next_city

    def __city_traversal(self, temp_distance):
        global start
        for i in range(1, city_num):
            start, end = self.path[i], self.path[i - 1]
            temp_distance += distance_matrix[start][end]
        return temp_distance

    # 移动操作
    def __move(self, next_city):

        self.path.append(next_city)
        self.open_table_city[next_city] = False
        self.total_distance += distance_matrix[self.current_city][next_city]
        self.current_city = next_city
        self.move_count += 1

    # 搜索路径
    def search_path(self):

        # 初始化数据
        self.__data_init()

        # 搜素路径，遍历完所有城市为止
        while self.move_count < city_num:
            # 移动到下一个城市
            next_city = self.__choice_next_city()
            self.__move(next_city)

        # 计算路径总长度
        self.__cal_total_distance()