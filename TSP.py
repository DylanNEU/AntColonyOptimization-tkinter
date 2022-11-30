import copy
import sys
import threading
import tkinter
from functools import reduce

import numpy as np

from Ant import Ant
from global_vars import city_num, pos_x, pos_y, ant_num, pheromone_matrix, rho, q, city_name


class TSP:

    def __init__(self, root, width=800, height=600, n=city_num):

        self.best_ant = None
        self.ants = None
        self.iterator = 0
        self.root = root
        self.width = width
        self.height = height
        # 城市数目初始化为city_num
        self.city_num = n
        # 绘制城市坐标点所需的圆点半径
        self.__r = 2
        self.nodes = []
        self.objects = []
        # 需要一个线程锁保证运行
        self.__lock = threading.RLock()
        self.__running = None
        self.__bind_event()
        self.__canvas_init()

        self.clear()

    # 画板初始化
    def __canvas_init(self):
        self.root.title("蚁群算法解决中国省会城市TSP问题实时演示")
        # 创建一个tkinter画布
        self.canvas = tkinter.Canvas(
            self.root,
            width=self.width,
            height=self.height,
            bg="#FFFFFF",  # 背景白色
            xscrollincrement=1,
            yscrollincrement=1
        )
        self.canvas.pack(expand=tkinter.NO, fill=tkinter.BOTH)

    # 停止运行
    def __stop_running(self):
        self.__lock.acquire()  # 需求锁
        self.__running = False  # 停止运行
        self.__lock.release()  # 释放掉进程锁

    # 开始运行
    def __start_running(self):
        self.__lock.acquire()  # 需求锁
        self.__running = True  # 开始运行
        self.__lock.release()  # 释放掉进程锁

    # 键盘按键
    def __bind_event(self):
        self.root.bind("q", self.exit)  # 退出程序
        self.root.bind("c", self.clear)  # 初始化清空
        self.root.bind("e", self.search)  # 开始搜索
        self.root.bind("s", self.stop)  # 停止搜索

    # 退出事件
    def exit(self, evt):
        self.__stop_running()  # 停止线程
        self.root.destroy()  # 清理掉窗口
        print("info: successfully exited.")
        sys.exit()  # 退出程序

    # 暂停
    def stop(self, evt):  # 停止搜索，原理同exit
        self.__stop_running()  # 停止线程

    # 清除
    def __remove_all(self):  # 删除画布上的所有形状
        for s in self.canvas.find_all():
            self.canvas.delete(s)

    # 初始化，清空
    def clear(self, evt=None):
        self.__stop_running()  # 停止线程
        self.__remove_all()  # 删除
        cities = len(pos_x)

        for i in range(cities):
            # x, y是为了动画演示而转换的位置坐标
            # tkinter的画布方向与地球的经纬度方向不一致 ，需要进行上下反转
            # 此外，如果直接按照经纬度位置绘制，点与点之间距离太密，必须进行放缩才能看清
            x = pos_x[i] * 12 - 900
            y = (pos_y[i] * 16 - 200) * -1 + 600
            self.canvas.create_text(125, 10, text="键盘控制: e-开始, s-暂停, c-重置, q-退出")
            self.__create_node(x, y)
            self.canvas.create_text(x, y - 10,  # 使用create_text方法在坐标（302，77）处绘制文字
                                    text='(' + str(round(pos_x[i], 2)) + ',' + str(round(pos_y[i], 2)) + ')',
                                    # 所绘制文字的内容
                                    fill='black'  # 所绘制文字的颜色为灰色
                                    )
            self.canvas.create_text(x, y - 25, text=city_name[i], fill='black')
            self.ants = [Ant(ID) for ID in range(ant_num)]  # 初始蚁群
            self.best_ant = Ant(-1)  # 初始最优解
            self.best_ant.total_distance = 1 << 31  # 初始最大距离
            self.iterator = 1  # 初始化迭代次数

    # 新建坐标
    def __create_node(self, x, y):
        self.nodes.append((x, y))
        node = self.canvas.create_oval(x - self.__r, y - self.__r, x + self.__r, y + self.__r,
                                       fill="#ff0000",
                                       outline="#000000",
                                       tags="node",
                                       )
        self.objects.append(node)

    # 画线
    def line(self, order):
        self.canvas.delete("line")

        def lines(i1, i2):
            p1, p2 = self.nodes[i1], self.nodes[i2]
            self.canvas.create_line(p1, p2, fill="#000000", tags="line")
            return i2

        reduce(lines, order, order[-1])

    # 蚂蚁遍历
    def __ant_traversal(self):
        # 遍历每一只蚂蚁
        for ant in self.ants:
            # 搜索一条路径
            ant.search_path()
            # 与当前最优蚂蚁比较
            if ant.total_distance < self.best_ant.total_distance:
                # 更新最优解
                self.best_ant = copy.deepcopy(ant)

    # 搜索
    def search(self, evt=None):

        # 开启线程
        self.__start_running()

        while self.__running:
            self.__ant_traversal()
            # 更新信息素
            self.__update_pheromone_matrix()
            print("iter: ", self.iterator, ", best length: ", self.best_ant.total_distance)
            # 连线
            self.line(self.best_ant.path)
            # 设置标题
            self.root.title("蚁群算法解决中国省会城市TSP问题实时演示 最短路径长度: %f 迭代次数: %d" % \
                            (round(self.best_ant.total_distance, 6), self.iterator))
            # 更新画布
            self.canvas.update()
            self.iterator += 1

    # 更新信息素矩阵
    def __update_pheromone_matrix(self):

        # 获取每只蚂蚁在其路径上留下的信息素
        temp = np.zeros((city_num, city_num))
        for ant in self.ants:
            for i in range(1, city_num):
                start, end = ant.path[i - 1], ant.path[i]
                temp[start][end] += q / ant.total_distance
                temp[end][start] = temp[start][end]

        # 更新所有城市之间的信息素，旧信息素衰减加上新迭代信息素
        for i in range(city_num):
            for j in range(city_num):
                pheromone_matrix[i][j] = temp[i][j] + pheromone_matrix[i][j] * rho

    # 主循环
    def mainloop(self):
        self.root.mainloop()
